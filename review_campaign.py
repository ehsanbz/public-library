"""Finite, manually started cloud review. State contains IDs/status only, never book text."""
import collections
import datetime
import json
import os
import pathlib
import sys
import time
import urllib.request

import sync_catalog as catalog

ROOT = pathlib.Path(__file__).resolve().parent
STATE = 'review_campaign.json'


def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def prepare(root, requested, new_id):
    previous = catalog.read_json(root/STATE, {})
    if requested:
        if previous.get('id') != requested:
            raise ValueError('Review campaign ID does not match the saved snapshot')
        return previous
    if previous.get('id') == new_id:
        return previous  # Retry after a completed checkpoint but failed deployment.
    if previous.get('status') == 'running':
        raise ValueError('A review is already active; resume using its saved campaign ID')
    personal = catalog.read_json(root/'bookshelf_source.json')
    rows = {'bookshelf': personal['rows'], 'public-library': catalog.read_csv(root/'public_library_catalog.csv')[1:]}
    listed = set(personal['summary'].get('review_ids', []))
    entries = {}
    for vault, records in rows.items():
        for row in records:
            if row[10].startswith('REVIEW:') or (vault=='bookshelf' and row[0] in listed):
                entries[vault+':'+row[0]] = 'pending'
    state = {'id': new_id, 'started_at': stamp(), 'status':'running' if entries else 'complete', 'entries':entries}
    catalog.write_json(root/STATE, state)
    return state


def load(root, identifier):
    state = catalog.read_json(root/STATE)
    if state.get('id') != identifier:
        raise ValueError('Wrong review campaign')
    return state


def pending_keys(root, scan, identifier):
    from content_reader import fingerprint
    state = load(root, identifier)
    audit = catalog.read_json(root/'metadata_audit.json', {})
    found = {vault+':'+item['id']:item for vault,snapshot in scan['vaults'].items() for item in snapshot['files']}
    for key, status in state['entries'].items():
        if status != 'pending':
            continue
        if key not in found:
            state['entries'][key] = 'unavailable'
            continue
        item = found[key]
        previous = (audit.get(key) or audit.get(item['id'], {})).get('content_analysis', {})
        if previous.get('fingerprint')==fingerprint(item) and previous.get('status')=='read':
            state['entries'][key] = 'already_read'
        elif not catalog.candidate(item):
            state['entries'][key] = 'not_a_book'
    catalog.write_json(root/STATE, state)
    return {key for key,status in state['entries'].items() if status=='pending'}


def record_results(root, identifier, readings):
    state = load(root, identifier)
    for key, reading in readings.items():
        if state['entries'].get(key) != 'pending':
            raise ValueError('Result outside the fixed pending snapshot')
        state['entries'][key] = reading['content_analysis']['status']
    if 'pending' not in state['entries'].values():
        state.update(status='complete', finished_at=stamp())
    state['updated_at'] = stamp()
    catalog.write_json(root/STATE, state)


def continue_campaign(root):
    state = catalog.read_json(root/STATE)
    pending = sum(v=='pending' for v in state['entries'].values())
    print(json.dumps({'campaign':state['id'], 'status':state['status'], 'remaining':pending,
                      'outcomes':dict(collections.Counter(state['entries'].values()))}))
    if state['status']=='complete' or not pending:
        return
    # workflow_dispatch is a finite continuation, not a scheduled routine.
    repository = os.environ['GITHUB_REPOSITORY']
    if repository != 'ehsanbz/public-library':
        raise ValueError('Unexpected repository')
    headers = {'Authorization':'Bearer '+os.environ['GITHUB_TOKEN'],
               'Accept':'application/vnd.github+json', 'Content-Type':'application/json',
               'X-GitHub-Api-Version':'2022-11-28'}
    # This runs after the reading job releases its maintenance lock. Let a queued
    # daily sync finish before dispatching the next one-time batch.
    for attempt in range(30):
        busy_daily = False
        for workflow in ['library-sync.yml','library-review-once.yml']:
            query = 'https://api.github.com/repos/'+repository+'/actions/workflows/'+workflow+'/runs?per_page=20'
            with urllib.request.urlopen(urllib.request.Request(query,headers=headers),timeout=30) as response:
                runs=json.load(response)['workflow_runs']
            active=[r for r in runs if r['status']!='completed' and str(r['id'])!=os.environ['GITHUB_RUN_ID']]
            if workflow=='library-review-once.yml' and active:
                print('Another one-time batch is already queued or running; no duplicate dispatched.')
                return
            busy_daily = busy_daily or (workflow=='library-sync.yml' and bool(active))
        if not busy_daily:
            break
        if attempt==0:
            print('Letting the regular daily sync finish before continuing the one-time review.')
        time.sleep(60)
    else:
        raise RuntimeError('Daily sync is still busy; resume this campaign manually')
    url = 'https://api.github.com/repos/'+repository+'/actions/workflows/library-review-once.yml/dispatches'
    body = json.dumps({'ref':'main','inputs':{'campaign_id':state['id']}}).encode()
    request = urllib.request.Request(url, data=body, method='POST', headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 204:
            raise RuntimeError('Review continuation was not accepted')
    print('Next batch of this one-time review has been dispatched.')


if __name__ == '__main__':
    command = sys.argv[1]
    if command=='prepare':
        state = prepare(ROOT, os.environ.get('REQUESTED_CAMPAIGN',''), os.environ['GITHUB_RUN_ID'])
        with open(os.environ['GITHUB_ENV'],'a',encoding='utf-8') as env:
            env.write('LIBRARY_REVIEW_CAMPAIGN='+state['id']+'\n')
        print(json.dumps({'campaign':state['id'],'entries':len(state['entries']),'status':state['status']}))
    elif command=='continue':
        continue_campaign(ROOT)
    else:
        raise ValueError('Unknown command')
