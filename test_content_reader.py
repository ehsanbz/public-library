import copy
import pathlib
import unittest
from unittest.mock import patch

import content_reader as reader
from test_sync_catalog import HEADERS, row


class ContentReaderTests(unittest.TestCase):
    def test_backlog_is_vault_scoped_balanced_and_advances_past_completed_reads(self):
        rows = {v:{} for v in ['bookshelf','public-library']}
        state = {'vaults': {v:{'files':[]} for v in rows}}
        audit = {}
        for vault in rows:
            for identifier in ['same','second','third']:
                item = {'id':identifier,'title':identifier+'.pdf','folder':'Existing category','size':'20'}
                state['vaults'][vault]['files'].append(item)
                entry = row(identifier,'Existing reviewed book')
                entry[10] = 'REVIEW: Verify inferred author and language.'
                rows[vault][identifier]=entry
        keys={v+':'+identifier for v in rows for identifier in rows[v]}
        self.assertEqual(reader.reading_queue(state,rows,audit,{}),[])
        queue = reader.reading_queue(state,rows,audit,{},review_keys=keys)
        self.assertEqual([q[1] for q in queue[:4]],['bookshelf','public-library']*2)
        item=state['vaults']['bookshelf']['files'][0]
        audit['bookshelf:same']={'content_analysis':{'fingerprint':reader.fingerprint(item),'status':'read','can_sort':False,'attempts':1}}
        keys.remove('bookshelf:same')
        queue=reader.reading_queue(state,rows,audit,{},review_keys=keys)
        self.assertNotIn(('bookshelf','same'),[(q[1],q[2]['id']) for q in queue])
        self.assertIn(('public-library','same'),[(q[1],q[2]['id']) for q in queue])
        keys.remove('public-library:third')
        queue=reader.reading_queue(state,rows,audit,{},review_keys=keys)
        self.assertNotIn(('public-library','third'),[(q[1],q[2]['id']) for q in queue])

    def test_daily_queue_keeps_deferred_new_books_but_excludes_old_reviews(self):
        old=row('deferred','New upload awaiting its first read')
        old[10]='REVIEW: Unknown metadata'
        state={'vaults':{'bookshelf':{'files':[{'id':'deferred','title':'upload.pdf','folder':'History'}]}}}
        rows={'bookshelf':{'deferred':old}}
        self.assertEqual(reader.reading_queue(state,rows,{},{}),[])
        queue=reader.reading_queue(state,rows,{}, {},pending_new={'bookshelf:deferred'})
        self.assertEqual(queue[0][2]['id'],'deferred')

    def test_reviewed_fields_override_only_their_fields_and_preserve_reading_provenance(self):
        automatic={'bookshelf:same':{'fields':{'Author(s)':'Read author','Book Title':'OCR title'},
                                    'content_analysis':{'verified_languages':['Persian']}}}
        reviewed={'bookshelf:same':{'fields':{'Book Title':'Verified title'}}}
        merged=reader.merge_overrides(automatic,reviewed)
        self.assertEqual(merged['bookshelf:same']['fields'],{'Author(s)':'Read author','Book Title':'Verified title'})
        self.assertEqual(merged['bookshelf:same']['content_analysis']['verified_languages'],['Persian'])

    def setUp(self):
        self.pages = [{'page': 1, 'text': 'A History of Iran\nBy Jane Historian\nIranian history and historical essays.', 'method': 'OCR'}]
        self.categories = {'History': ['Iranian history']}
        self.item = {'id': 'new', 'title': 'upload.pdf', 'modified_time': '2026-10-16', 'size': '20'}
        self.prediction = {'title': 'A History of Iran', 'author': 'Jane Historian',
            'category': 'History', 'subcategory': 'Iranian history',
            'title_evidence': 'A History of Iran', 'author_evidence': 'By Jane Historian',
            'category_evidence': 'Iranian history and historical essays.',
            'title_confidence': .99, 'author_confidence': .99, 'category_confidence': .95}

    def test_grounded_metadata_and_category_are_accepted_without_publishing_text(self):
        result = reader.validated(self.prediction, self.pages, self.categories, self.item, ['English'])
        self.assertEqual(result['fields']['Author(s)'], 'Jane Historian')
        self.assertEqual(result['fields']['Main Category'], 'History')
        self.assertTrue(result['content_analysis']['can_sort'])
        import json
        self.assertNotIn('By Jane Historian', json.dumps(result))
        self.assertNotIn('Iranian history and historical essays.', json.dumps(result))

    def test_form_check_blocks_confident_but_conflicting_fiction_classification(self):
        prediction = dict(self.prediction, category='Literary Fiction', subcategory='General fiction',
                          form='Nonfiction', form_confidence=.99,
                          form_evidence='Iranian history and historical essays.')
        result = reader.validated(prediction,self.pages,{'Literary Fiction':['General fiction']},self.item,['English'])
        self.assertFalse(result['content_analysis']['can_sort'])
        self.assertNotIn('Main Category',result['fields'])

    def test_hallucinated_author_and_injected_destination_are_rejected(self):
        prediction = dict(self.prediction, author='Invented Person', category='../Other vault', subcategory='Inbox')
        result = reader.validated(prediction, self.pages, self.categories, self.item, ['English'])
        self.assertNotIn('Author(s)', result['fields'])
        self.assertNotIn('Main Category', result['fields'])
        self.assertFalse(result['content_analysis']['can_sort'])

    def test_low_confidence_subject_does_not_move_book(self):
        result = reader.validated(dict(self.prediction, category_confidence=.6), self.pages, self.categories, self.item, [])
        self.assertFalse(result['content_analysis']['can_sort'])

    def test_minor_ocr_error_is_tolerated_but_different_author_is_not(self):
        pages = [{'page': 1, 'text': 'By Alexandrianna Historiographer', 'method': 'OCR'}]
        self.assertTrue(reader.grounded('By Alexandrianna Historlographer', pages, 'Alexandrianna Historiographer'))
        self.assertFalse(reader.grounded('By Completely Different', pages, 'Completely Different'))
        pages[0]['method'] = 'embedded text'
        self.assertFalse(reader.grounded('By Alexandrianna Historlographer', pages))

    def test_category_capitalization_is_canonicalized(self):
        prediction = dict(self.prediction, category='HISTORY', subcategory='IRANIAN HISTORY')
        result = reader.validated(prediction, self.pages, self.categories, self.item, ['English'])
        self.assertEqual(result['fields']['Subcategory'], 'Iranian history')

    def test_persian_owner_tag_is_separate_from_detected_book_language(self):
        result = reader.validated(self.prediction, self.pages, self.categories,
                                 dict(self.item, title='کتاب.pdf'), ['English'])
        self.assertEqual(result['fields']['Language'], 'English; Persian')
        self.assertEqual(result['content_analysis']['verified_languages'], ['English'])
        self.assertTrue(result['content_analysis']['policy_persian'])

    def test_changed_file_or_reader_version_invalidates_fingerprint(self):
        self.assertNotEqual(reader.fingerprint(self.item), reader.fingerprint(dict(self.item, modified_time='later')))

    def test_enrichment_extends_pending_transaction_without_losing_new_rows(self):
        from test_sync_catalog import SyncTests
        case = SyncTests('test_additive_idempotent_and_old_modification_dates')
        case.setUp()
        try:
            reader.catalog.ingest(case.root, case.scan)
            reading = reader.validated(self.prediction, self.pages, self.categories, self.item, ['English'])
            reader.update_existing(case.root, {'bookshelf:new-personal': reading})
            self.assertFalse(reader.catalog.ingest(case.root, case.scan)['changed'])
            saved = reader.catalog.read_json(case.root/'bookshelf_source.json')
            self.assertEqual(next(r for r in saved['rows'] if r[0]=='new-personal')[2], 'Jane Historian')
        finally:
            case.tearDown()

    def test_existing_curated_metadata_is_not_replaced(self):
        original = row('old', 'Curated title')
        original[4:6] = ['Science', 'Custom topic']
        original[7] = 'German'
        original[2] = 'Curated author'
        documents = {'bookshelf_source.json': {'headers': HEADERS, 'rows': [original], 'summary': {}},
                     'metadata_audit.json': {'old': {'vault': 'My Bookshelf', 'author_source': 'Manual verification'}},
                     'sync_config.json': {}}
        csvdata = [HEADERS]
        def read(path, default=None):return copy.deepcopy(documents.get(path.name, default))
        def write(path, value):documents[path.name] = copy.deepcopy(value)
        reading = reader.validated(self.prediction, self.pages, self.categories, self.item, ['English'])
        with patch.object(reader.catalog,'read_json',side_effect=read), patch.object(reader.catalog,'write_json',side_effect=write), patch.object(reader.catalog,'read_csv',return_value=csvdata), patch.object(reader.catalog,'write_csv'):
            reader.update_existing(pathlib.Path('.'), {'bookshelf:old': reading})
        after = documents['bookshelf_source.json']['rows'][0]
        self.assertEqual(after, original)
        self.assertEqual(documents['metadata_audit.json']['old']['author_source'], 'Manual verification')

    def test_ocr_is_used_for_image_only_pdf(self):
        try:
            import fitz
        except ImportError:
            self.skipTest('PyMuPDF is installed on the cloud runner')
        import uuid
        parent = pathlib.Path(__file__).resolve().parent/'sync_tests.local'
        parent.mkdir(exist_ok=True)
        directory = parent/uuid.uuid4().hex
        directory.mkdir()
        path = directory/'scan.pdf'
        try:
            doc = fitz.open()
            doc.new_page()
            doc.save(path)
            doc.close()
            with patch.object(reader, 'ocr_page', return_value='Scanned Book Title By Sample Author') as ocr:
                result = reader.extract(path, directory)
            self.assertTrue(ocr.called)
            self.assertEqual(result[0]['method'], 'OCR')
        finally:
            path.unlink(missing_ok=True)
            directory.rmdir()


if __name__ == '__main__':
    unittest.main()
