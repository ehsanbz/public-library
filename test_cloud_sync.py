import copy
import unittest
from unittest.mock import patch

import cloud_sync as c


class FakeDrive:
    def __init__(self):
        self.keys = {}
        self.mutations = []
        self.files = {
            c.PERSONAL: {'id': c.PERSONAL, 'name': 'Bookshelf', 'mimeType': c.FOLDER},
            c.INBOX: {'id': c.INBOX, 'name': 'Inbox', 'mimeType': c.FOLDER, 'parents': [c.PERSONAL]},
            'arts': {'id': 'arts', 'name': 'Arts & Culture', 'mimeType': c.FOLDER, 'parents': [c.PERSONAL]},
            'periodicals': {'id': 'periodicals', 'name': 'Literary periodicals', 'mimeType': c.FOLDER, 'parents': ['arts']},
            'book': {'id': 'book', 'name': 'مجله ویرگول.pdf', 'mimeType': 'application/pdf', 'parents': [c.INBOX, 'unrelated']},
            'unknown': {'id': 'unknown', 'name': 'Uncertain.pdf', 'mimeType': 'application/pdf', 'parents': [c.INBOX]},
            'shortcut': {'id': 'shortcut', 'name': 'Other vault', 'mimeType': c.SHORTCUT, 'parents': [c.INBOX]},
        }

    def get(self, file_id):
        return copy.deepcopy(self.files[file_id])

    def children(self, parent):
        return [copy.deepcopy(f) for f in self.files.values() if parent in f.get('parents', [])]

    def request(self, method, path, params, body):
        self.mutations.append((method, path, params, body))
        assert method == 'PATCH'
        item = self.files[path.split('/')[-1]]
        item['parents'] = [p for p in item['parents'] if p != params['removeParents']] + [params['addParents']]
        return self.get(item['id'])


class CloudTests(unittest.TestCase):
    def test_resource_key_headers_stay_bounded_for_large_vaults(self):
        from unittest.mock import Mock
        drive = object.__new__(c.Drive)
        drive.keys = {str(i): 'key-'+str(i) for i in range(3000)}
        response = Mock(ok=True)
        response.json.return_value = {'files': []}
        drive.session = Mock()
        drive.session.request.return_value = response
        drive.request('GET', 'files', {'q': "'42' in parents and trashed = false"})
        self.assertEqual(drive.session.request.call_args.kwargs['headers'],
                         {'X-Goog-Drive-Resource-Keys': '42/key-42'})
        drive.request('GET', 'files/99', {})
        self.assertEqual(drive.session.request.call_args.kwargs['headers'],
                         {'X-Goog-Drive-Resource-Keys': '99/key-99'})

    @patch.object(c.catalog, 'write_json')
    def test_verified_new_book_metadata_guides_sorting_before_ingestion(self, _):
        from test_sync_catalog import HEADERS
        drive = FakeDrive()
        drive.files['book']['name'] = 'New book.pdf'
        additions = {'bookshelf:book': {'fields': {'Main Category': 'Arts & Culture',
                                                  'Subcategory': 'Literary periodicals'}}}
        def read(path, default=None):
            return {'rows': [], 'headers': HEADERS} if path.name == 'bookshelf_source.json' else additions
        with patch.object(c.catalog, 'read_json', side_effect=read):
            self.assertEqual(c.organize(drive)['moved'], 1)
        self.assertIn('periodicals', drive.files['book']['parents'])

    def test_credential_validation_never_exposes_secret_values(self):
        import json
        sentinel = 'PRIVATE-SENTINEL-NOT-FOR-LOGS'
        for info in ({'installed': {'client_secret': sentinel}}, {'type': 'authorized_user', 'client_secret': sentinel}, [sentinel]):
            with self.assertRaises(c.CloudSetupError) as error:
                c.credential_info(json.dumps(info))
            self.assertNotIn(sentinel, str(error.exception))
        with self.assertRaises(c.CloudSetupError):
            c.credential_info(sentinel)

    def test_normal_google_credentials_json_without_type_is_accepted(self):
        import json
        info = {'client_id': 'id', 'client_secret': 'secret', 'refresh_token': 'refresh'}
        self.assertEqual(c.credential_info(json.dumps(info))['type'], 'authorized_user')

    @patch.object(c.catalog, 'write_json')
    @patch.object(c.catalog, 'read_json', return_value={'rows': [], 'headers': []})
    def test_moves_only_classified_inbox_and_recovers_without_local_state(self, *_):
        drive = FakeDrive()
        result = c.organize(drive)
        self.assertEqual(result, {'moved': 1, 'needs_review': 1})
        self.assertEqual(set(drive.files['book']['parents']), {'periodicals', 'unrelated'})
        self.assertEqual(drive.files['unknown']['parents'], [c.INBOX])
        self.assertEqual(drive.files['shortcut']['parents'], [c.INBOX])
        self.assertEqual(c.organize(drive)['moved'], 0)
        self.assertEqual(len(drive.mutations), 1)

    def test_rejects_destination_outside_personal_vault(self):
        drive = FakeDrive()
        drive.files['periodicals']['parents'] = ['foreign']
        drive.files['foreign'] = {'id': 'foreign', 'name': 'Other vault', 'mimeType': c.FOLDER, 'parents': []}
        with self.assertRaises(ValueError):
            c.verify_personal_destination(drive, 'periodicals')
        self.assertEqual(drive.mutations, [])

    def test_walk_does_not_follow_shortcuts(self):
        state = c.walk(FakeDrive(), c.INBOX)
        self.assertEqual({f['id'] for f in state['files']}, {'book', 'unknown'})
        self.assertEqual(len(state['shortcuts']), 1)

    def test_scan_failure_never_returns_complete(self):
        drive = FakeDrive()
        with self.assertRaises(KeyError):
            c.scan(drive, {'vaults': {'bookshelf': 'https://drive.google.com/drive/folders/'+c.PERSONAL,
                                     'public-library': 'https://drive.google.com/drive/folders/inaccessible'}})

    def test_pagination_exhausted_and_incomplete_search_rejected(self):
        drive = object.__new__(c.Drive)
        pages = [{'files': [{'id': 'one'}], 'nextPageToken': 'next'},
                 {'files': [{'id': 'two'}]}]
        requests = []
        def request(method, path, params):
            requests.append(params)
            return pages.pop(0)
        drive.request = request
        self.assertEqual([f['id'] for f in drive.children('root')], ['one', 'two'])
        self.assertEqual(requests[1]['pageToken'], 'next')
        drive.request = lambda *args: {'files': [], 'incompleteSearch': True}
        with self.assertRaises(ValueError):
            drive.children('root')


if __name__ == '__main__':
    unittest.main()
