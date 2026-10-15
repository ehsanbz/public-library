"""GitHub-hosted Drive discovery and narrowly scoped personal Inbox organization.

Durable catalog masters live in Git; Drive parents are the recovery source of truth.
Credentials are read only from the runner environment and never written to outputs.
"""
import datetime
import json
import os
import pathlib
import re
import subprocess
import time
import urllib.parse
import urllib.request

import sync_catalog as catalog

ROOT = pathlib.Path(__file__).resolve().parent
PERSONAL = '1NvUlp3CWKggnwhxBS862_2i1LsIEOsxM'
INBOX = '18ksW5WwplfoJa0XHheJS6N3mcnVeKhKw'
FOLDER = 'application/vnd.google-apps.folder'
SHORTCUT = 'application/vnd.google-apps.shortcut'
FIELDS = 'id,name,mimeType,parents,webViewLink,resourceKey,size,modifiedTime,createdTime,trashed'
OUTPUTS = ['index.html', 'catalog_data.json', 'book_catalog.csv',
           'public_library_catalog.csv', 'bookshelf_catalog.csv', 'bookshelf_source.json',
           'vault_inventory.json', 'metadata_source_order.json', 'metadata_audit.json',
           'sync_config.json', 'README.md']


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class CloudSetupError(Exception):
    """Only fixed, credential-free messages may be emitted to public logs."""


def credential_info(secret):
    try:
        info = json.loads(secret)
    except (ValueError, TypeError):
        raise CloudSetupError('GOOGLE_DRIVE_CREDENTIALS_JSON must contain valid JSON, not a file path or encoded string.') from None
    if not isinstance(info, dict):
        raise CloudSetupError('GOOGLE_DRIVE_CREDENTIALS_JSON must contain a JSON credential object.')
    if 'installed' in info or 'web' in info:
        raise CloudSetupError('The secret contains the downloaded OAuth CLIENT file. Authorize it once with authorize_drive.py, then replace the secret with the generated credential JSON containing a refresh_token. See CLOUD_SETUP.md.')
    # google.oauth2.credentials.Credentials.to_json() omits type; accept its normal output.
    if not info.get('type') and all(info.get(k) for k in ('client_id', 'client_secret', 'refresh_token')):
        info['type'] = 'authorized_user'
    kind = info.get('type')
    required = {'authorized_user': ('client_id', 'client_secret', 'refresh_token'),
                'service_account': ('client_email', 'private_key', 'token_uri')}
    if kind not in required:
        raise CloudSetupError('Use generated authorized_user credentials with a refresh_token, or a service_account key. A downloaded OAuth client file or access token alone cannot run unattended.')
    if any(not isinstance(info.get(k), str) or not info[k].strip() for k in required[kind]):
        raise CloudSetupError('The credential JSON is missing required authorization fields. Generate it again using CLOUD_SETUP.md; do not paste credentials into logs or chat.')
    return info


class Drive:
    def __init__(self, info):
        # Lazy imports let tests exercise safety boundaries without credentials.
        from google.auth.transport.requests import AuthorizedSession
        scopes = ['https://www.googleapis.com/auth/drive']
        if info.get('type') == 'service_account':
            from google.oauth2.service_account import Credentials
            credentials = Credentials.from_service_account_info(info, scopes=scopes)
        elif info.get('type') == 'authorized_user':
            from google.oauth2.credentials import Credentials
            credentials = Credentials.from_authorized_user_info(info, scopes=scopes)
        else:
            raise ValueError('Drive secret must contain authorized_user or service_account credentials')
        self.session = AuthorizedSession(credentials)
        self.keys = {}

    def request(self, method, path, params=None, body=None):
        headers = {}
        # Only send resource keys for the file/parent addressed by THIS request.
        # Sending every discovered key eventually exceeds Google's header limit (HTTP 413).
        addressed = set(re.findall(r"'([^']+)' in parents", (params or {}).get('q', '')))
        if path.startswith('files/'):
            addressed.add(path.split('/')[1])
        selected = [k+'/'+self.keys[k] for k in sorted(addressed) if k in self.keys]
        if selected:
            headers['X-Goog-Drive-Resource-Keys'] = ','.join(selected)
        for attempt in range(4):
            response = self.session.request(method, 'https://www.googleapis.com/drive/v3/'+path,
                                            params=params, json=body, headers=headers, timeout=90)
            if response.status_code in (429, 500, 502, 503, 504) and method == 'GET' and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            if not response.ok:
                # Do not emit response bodies, credentials or private book contents to public logs.
                explanations = {
                    'notFound': 'File or folder is unavailable to the cloud identity.',
                    'insufficientPermissions': 'The Google authorization lacks the required Drive scope.',
                    'insufficientFilePermissions': 'The cloud identity lacks permission for this file or folder.',
                    'accessNotConfigured': 'Enable Google Drive API in the credential project.',
                    'rateLimitExceeded': 'Google Drive rate limit exceeded.',
                    'userRateLimitExceeded': 'Google Drive per-user rate limit exceeded.',
                    'storageQuotaExceeded': 'The cloud identity cannot create folders because its storage quota is unavailable or exceeded. Use user OAuth credentials or precreate filing folders.',
                    'appNotAuthorizedToFile': 'The OAuth app is not authorized for this file.',
                    'teamDriveFileLimitExceeded': 'The shared Drive file limit was reached.',
                }
                reasons = []
                try:
                    reasons = [e.get('reason') for e in response.json().get('error', {}).get('errors', [])]
                except (ValueError, AttributeError, TypeError):
                    pass
                hints = list(dict.fromkeys(explanations[r] for r in reasons if r in explanations))
                raise CloudSetupError('Drive '+method+' failed with HTTP '+str(response.status_code)+'. '+' '.join(hints))
            result = response.json()
            for item in result.get('files', [result]):
                if item.get('resourceKey') and item.get('id'):
                    self.keys[item['id']] = item['resourceKey']
            return result

    def get(self, file_id):
        return self.request('GET', 'files/'+file_id,
                            {'fields': FIELDS, 'supportsAllDrives': 'true'})

    def children(self, folder_id):
        found, page, seen_pages = [], None, set()
        while True:
            params = {'q': "'"+folder_id+"' in parents and trashed = false",
                      'fields': 'nextPageToken,incompleteSearch,files('+FIELDS+')',
                      'pageSize': 1000, 'supportsAllDrives': 'true',
                      'includeItemsFromAllDrives': 'true'}
            if page:
                params['pageToken'] = page
            result = self.request('GET', 'files', params)
            if result.get('incompleteSearch'):
                raise ValueError('Incomplete Drive search; no catalog checkpoint is allowed')
            found.extend(result.get('files', []))
            page = result.get('nextPageToken')
            if not page:
                return found
            if page in seen_pages:
                raise ValueError('Repeated Drive page token')
            seen_pages.add(page)


def drive_item(raw, folder=''):
    url = raw.get('webViewLink') or 'https://drive.google.com/file/d/'+raw['id']+'/view'
    if raw.get('resourceKey') and 'resourcekey=' not in url.lower():
        url += ('&' if '?' in url else '?')+'resourcekey='+urllib.parse.quote(raw['resourceKey'])
    return {'id': raw['id'], 'title': raw['name'], 'mime_type': raw['mimeType'],
            'url': url, 'folder': folder, 'size': raw.get('size'),
            'modified_time': raw.get('modifiedTime'), 'created_time': raw.get('createdTime')}


def walk(drive, root_id):
    root = drive.get(root_id)
    if root.get('mimeType') != FOLDER or root.get('trashed'):
        raise ValueError('Configured vault root is not an accessible folder')
    result = {'files': [], 'folders': [], 'shortcuts': []}
    queue, visited = [(root_id, '')], set()
    while queue:
        folder_id, path = queue.pop(0)
        if folder_id in visited:
            raise ValueError('Repeated folder in vault traversal')
        visited.add(folder_id)
        children = drive.children(folder_id)
        result['folders'].append({'id': folder_id, 'path': path,
                                  'url': 'https://drive.google.com/drive/folders/'+folder_id,
                                  'count': len(children)})
        for raw in children:
            if raw['mimeType'] == SHORTCUT:
                result['shortcuts'].append({'id': raw['id'], 'title': raw['name'], 'folder': path})
            elif raw['mimeType'] == FOLDER:
                queue.append((raw['id'], '/'.join(filter(None, [path, raw['name']]))))
            else:
                result['files'].append(drive_item(raw, path))
    result['files'].sort(key=lambda f: f['id'])
    return result


def verify_personal_destination(drive, destination):
    seen = set()
    while destination != PERSONAL:
        if destination in seen or destination == INBOX:
            raise ValueError('Destination is not in the personal filing hierarchy')
        seen.add(destination)
        item = drive.get(destination)
        if item.get('mimeType') != FOLDER or item.get('trashed') or len(item.get('parents', [])) != 1:
            raise ValueError('Cannot verify destination ancestry')
        destination = item['parents'][0]


def ensure_folder(drive, parent, name):
    verify_personal_destination(drive, parent)
    matches = [f for f in drive.children(parent) if f['name'] == name and f['mimeType'] == FOLDER]
    if len(matches) > 1:
        raise ValueError('Ambiguous filing folder; resolve duplicate folder names')
    if matches:
        return matches[0]['id']
    result = drive.request('POST', 'files', {'fields': FIELDS, 'supportsAllDrives': 'true'},
                           {'name': name, 'mimeType': FOLDER, 'parents': [parent]})
    verify_personal_destination(drive, result['id'])
    return result['id']


def organize(drive, root=ROOT):
    inbox = drive.get(INBOX)
    if inbox.get('mimeType') != FOLDER or inbox.get('parents') != [PERSONAL]:
        raise ValueError('Personal Inbox location changed; refusing to move files')
    state = walk(drive, INBOX)
    source_ids = {f['path']: f['id'] for f in state['folders']}
    metadata = {r[0]: r for r in catalog.read_json(root/'bookshelf_source.json')['rows']}
    moved, unresolved = 0, 0
    destinations = {}
    journal = []
    for item in state['files']:
        if not catalog.candidate(item):
            continue
        # Saved web pages can require sibling assets; leave them intact for review.
        if pathlib.Path(item['title']).suffix.lower() in {'.html', '.htm', '.mht'}:
            unresolved += 1
            continue
        row = metadata.get(item['id']) or catalog.default_row('bookshelf', item)
        row = list(row)
        if item['id'] not in metadata:
            additions = catalog.read_json(root/'metadata_additions.json', {})
            headers = catalog.read_json(root/'bookshelf_source.json')['headers']
            for field, value in additions.get('bookshelf:'+item['id'], {}).get('fields', {}).items():
                if field not in headers[1:14]:
                    raise ValueError('Verified addition cannot alter source ID or link')
                row[headers.index(field)] = value
        category, subcategory = row[4:6]
        if category not in catalog.CATEGORIES or subcategory in {'', 'Unknown', 'Needs review'}:
            unresolved += 1
            continue
        source_parent = source_ids[item['folder']]
        source = drive.get(item['id'])
        if source_parent not in source.get('parents', []):
            continue  # Owner moved it concurrently; respect their organization.
        key = (category, subcategory)
        if key not in destinations:
            parent = ensure_folder(drive, PERSONAL, category)
            destinations[key] = ensure_folder(drive, parent, subcategory)
        destination = destinations[key]
        verify_personal_destination(drive, destination)
        # Revalidate that the source still belongs to Inbox immediately before mutation.
        ancestor = source_parent
        visited = set()
        while ancestor != INBOX:
            if ancestor in visited or ancestor == PERSONAL:
                raise ValueError('Source left the Inbox; refusing move')
            visited.add(ancestor)
            parents = drive.get(ancestor).get('parents', [])
            if len(parents) != 1:
                raise ValueError('Cannot verify Inbox source ancestry')
            ancestor = parents[0]
        source = drive.get(item['id'])
        if source_parent not in source.get('parents', []):
            continue
        journal.append({'id': item['id'], 'source': source_parent,
                        'destination': destination, 'status': 'pending'})
        catalog.write_json(root/'cloud_moves.local.json', journal)
        drive.request('PATCH', 'files/'+item['id'],
                      {'addParents': destination, 'removeParents': source_parent,
                       'fields': FIELDS, 'supportsAllDrives': 'true'}, {})
        after = drive.get(item['id'])
        expected = (set(source['parents']) - {source_parent}) | {destination}
        if set(after.get('parents', [])) != expected or after['name'] != source['name']:
            raise ValueError('Move verification failed')
        journal[-1]['status'] = 'verified'
        catalog.write_json(root/'cloud_moves.local.json', journal)
        moved += 1
    return {'moved': moved, 'needs_review': unresolved}


def scan(drive, config):
    result = {'started_at': now(), 'complete': False, 'errors': [], 'vaults': {}}
    for vault, url in config['vaults'].items():
        print('Scanning vault: '+vault, flush=True)
        parsed = urllib.parse.urlparse(url)
        root_id = parsed.path.rstrip('/').split('/')[-1]
        key = urllib.parse.parse_qs(parsed.query).get('resourcekey', [None])[0]
        if key:
            drive.keys[root_id] = key
        try:
            result['vaults'][vault] = walk(drive, root_id)
        except CloudSetupError as error:
            raise CloudSetupError('While scanning '+vault+': '+str(error)) from None
        print('Completed vault scan: '+vault, flush=True)
    result.update(complete=True, finished_at=now())
    catalog.validate_scan(result)
    return result


def upstream_catalog():
    url = 'https://raw.githubusercontent.com/ehsanbz/bookshelf-catalog/main/index.html'
    import re
    with urllib.request.urlopen(url, timeout=60) as response:
        html = response.read(20_000_001)
    if len(html) > 20_000_000:
        raise ValueError('Upstream catalog exceeds expected size')
    match = re.search(rb'<script id="catalog-data" type="application/json">(.*?)</script>', html, re.S)
    if not match:
        raise ValueError('Original Bookshelf catalog data is missing')
    return json.loads(match[1])


def main():
    secret = os.environ.get('GOOGLE_DRIVE_CREDENTIALS_JSON', '')
    if not secret:
        raise ValueError('Add GOOGLE_DRIVE_CREDENTIALS_JSON in repository Actions secrets first')
    drive = Drive(credential_info(secret))
    config = catalog.read_json(ROOT/'sync_config.json')
    # Complete read access to BOTH vaults is required before any Inbox mutations.
    scan(drive, config)
    print('Organizing personal Inbox.', flush=True)
    organized = organize(drive)
    state = scan(drive, config)  # Scan after moves; crash recovery discovers moved IDs here next run.
    result = catalog.ingest(ROOT, state, overrides=catalog.read_json(ROOT/'metadata_additions.json', {}), upstream=upstream_catalog())
    config = catalog.read_json(ROOT/'sync_config.json')
    config.update(execution='GitHub Actions hosted runner with Google Drive API',
                  cloud_enabled=True, personal_inbox_organization=True)
    catalog.write_json(ROOT/'sync_config.json', config)
    # Rebuild also on no-addition runs: a previous commit or deployment may have failed.
    subprocess.run(['python', str(ROOT/'build_catalog.py')], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(['python', str(ROOT/'verify_metadata.py')], cwd=ROOT, check=True)
    print(json.dumps({'organization': organized, 'catalog': result}))


if __name__ == '__main__':
    try:
        main()
    except CloudSetupError as error:
        print('::error::'+str(error))
        raise SystemExit(1)
    except Exception as error:
        # No auth response bodies / raw metadata / book content in public runner logs.
        print('Cloud sync failed: '+type(error).__name__+'. Check Drive authorization, folder access and workflow setup.')
        raise SystemExit(1)
