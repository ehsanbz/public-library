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
    @patch.object(c.catalog, 'write_json')
    @patch.object(c.catalog, 'read_json', return_value={'rows': []})
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
