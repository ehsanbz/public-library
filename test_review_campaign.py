import copy
import pathlib
import io
import json
import unittest
from unittest.mock import patch

import review_campaign as campaign
import content_reader as reader
from test_sync_catalog import HEADERS, row


class CampaignTests(unittest.TestCase):
    def setUp(self):
        personal=row('same','Personal reviewed book'); personal[10]='REVIEW: Author'
        public=row('same','Public reviewed book'); public[10]='REVIEW: Language'
        self.documents={'bookshelf_source.json':{'rows':[personal],'summary':{'review_ids':['same']}},
                        'metadata_audit.json':{}}
        self.public=[HEADERS,public]
        def read(path,default=None):return copy.deepcopy(self.documents.get(path.name,default))
        def write(path,value):self.documents[path.name]=copy.deepcopy(value)
        self.read=patch.object(campaign.catalog,'read_json',side_effect=read)
        self.write=patch.object(campaign.catalog,'write_json',side_effect=write)
        self.csv=patch.object(campaign.catalog,'read_csv',side_effect=lambda p:copy.deepcopy(self.public))
        self.read.start(); self.write.start(); self.csv.start()
        self.addCleanup(self.read.stop); self.addCleanup(self.write.stop); self.addCleanup(self.csv.stop)
        self.root=pathlib.Path('.')

    def test_fixed_snapshot_does_not_grow_and_same_ids_stay_separate(self):
        initial=campaign.prepare(self.root,'','one')
        self.assertEqual(set(initial['entries']),{'bookshelf:same','public-library:same'})
        another=row('later','Later uploaded book'); another[10]='REVIEW: New'
        self.public.append(another)
        resumed=campaign.prepare(self.root,'one','ignored')
        self.assertEqual(initial,resumed)
        with self.assertRaises(ValueError):campaign.prepare(self.root,'','two')

    def test_attempts_are_terminal_and_completion_prevents_dispatch(self):
        campaign.prepare(self.root,'','one')
        campaign.record_results(self.root,'one',{'bookshelf:same':{'content_analysis':{'status':'reading_failed_model_reading'}}})
        state=campaign.load(self.root,'one')
        self.assertEqual(state['entries']['bookshelf:same'],'reading_failed_model_reading')
        self.assertEqual(state['status'],'running')
        campaign.record_results(self.root,'one',{'public-library:same':{'content_analysis':{'status':'read'}}})
        with patch.object(campaign.urllib.request,'urlopen') as network:
            campaign.continue_campaign(self.root)
        self.assertFalse(network.called)
        self.assertEqual(campaign.load(self.root,'one')['status'],'complete')
        self.assertEqual(campaign.prepare(self.root,'','one')['status'],'complete')

    def test_next_batch_dispatch_keeps_the_same_snapshot_and_has_no_schedule(self):
        campaign.prepare(self.root,'','one')
        class Response(io.BytesIO):
            status=204
        responses=[Response(b'{"workflow_runs":[]}'),Response(b'{"workflow_runs":[]}'),Response(b'')]
        with patch.dict(campaign.os.environ,{'GITHUB_REPOSITORY':'ehsanbz/public-library',
                        'GITHUB_RUN_ID':'one','GITHUB_TOKEN':'unit-test-placeholder'}), \
             patch.object(campaign.urllib.request,'urlopen',side_effect=responses) as network:
            campaign.continue_campaign(self.root)
        request=network.call_args.args[0]
        self.assertEqual(request.method,'POST')
        self.assertTrue(request.full_url.endswith('/library-review-once.yml/dispatches'))
        self.assertEqual(json.loads(request.data),{'ref':'main','inputs':{'campaign_id':'one'}})

    def test_missing_and_already_read_entries_are_not_read_again(self):
        campaign.prepare(self.root,'','one')
        item={'id':'same','title':'book.pdf','folder':'History','size':'2'}
        self.documents['metadata_audit.json']={'bookshelf:same':{'content_analysis':{
            'status':'read','fingerprint':reader.fingerprint(item)}}}
        scan={'vaults':{'bookshelf':{'files':[item]},'public-library':{'files':[]}}}
        self.assertEqual(campaign.pending_keys(self.root,scan,'one'),set())
        campaign.record_results(self.root,'one',{})
        state=campaign.load(self.root,'one')
        self.assertEqual(state['entries'],{'bookshelf:same':'already_read','public-library:same':'unavailable'})
        self.assertEqual(state['status'],'complete')

    def test_results_outside_snapshot_and_wrong_campaign_are_rejected(self):
        campaign.prepare(self.root,'','one')
        with self.assertRaises(ValueError):campaign.load(self.root,'other')
        with self.assertRaises(ValueError):
            campaign.record_results(self.root,'one',{'bookshelf:later':{'content_analysis':{'status':'read'}}})


if __name__=='__main__':unittest.main()
