import copy,pathlib,unittest,uuid
import sync_catalog as s
HEADERS=['Original ID','Book Title','Author(s)','Book Type','Main Category','Subcategory','Topic Tags','Language','Publication Year','Series / Volume','Notes / Uncertainty','ISBN','Edition','Format','Shelf / File Location']
def row(id,title):return [id,title,'Manually corrected author','Reference','Science','Custom topic','Custom tag','English','2024','Volume 2','Manual note','ISBN','Second','PDF','https://drive.google.com/file/d/'+id+'/view']
def file(id,title='Added.pdf'):return {'id':id,'title':title,'mime_type':'application/pdf','folder':'Inbox','url':'https://drive.google.com/file/d/'+id+'/view','modified_time':'2001-01-01T00:00:00Z'}
class SyncTests(unittest.TestCase):
 def setUp(self):
  parent=pathlib.Path(__file__).resolve().parent/'sync_tests.local';parent.mkdir(exist_ok=True)
  self.root=parent/uuid.uuid4().hex;self.root.mkdir()
  s.write_csv(self.root/'public_library_catalog.csv',[HEADERS,row('public-old','Keep public')])
  for name,value in {'bookshelf_source.json':{'headers':HEADERS,'rows':[row('personal-old','Keep personal')],'summary':{'review_ids':[],'updated_at':'2020-01-01'}},'vault_inventory.json':{'files':[file('public-old')],'folders':[],'remaining':[]},'metadata_source_order.json':{'public-old':0},'metadata_audit.json':{},'sync_config.json':{'enabled':True,'public_updated_at':'2020-01-01'}}.items():s.write_json(self.root/name,value)
  self.scan={'complete':True,'errors':[],'started_at':'2026-10-15T00:00:00Z','finished_at':'2026-10-15T00:00:01Z','vaults':{'public-library':{'files':[file('public-old'),file('new-public')]},'bookshelf':{'files':[file('personal-old'),file('new-personal','کتاب تازه.pdf'),file('asset','image.jpg'),file('catalog','book_catalog.html')]}}}
 def tearDown(self):
  assert self.root.resolve().is_relative_to(pathlib.Path(__file__).resolve().parent/'sync_tests.local')
  for child in self.root.iterdir():
   assert child.is_file() and child.resolve().is_relative_to(self.root.resolve())
   child.unlink()
  self.root.rmdir()
 def test_additive_idempotent_and_old_modification_dates(self):
  r=s.ingest(self.root,self.scan);self.assertEqual(r['added'],{'public-library':1,'bookshelf':1})
  self.assertEqual(s.read_csv(self.root/'public_library_catalog.csv')[1],row('public-old','Keep public'))
  personal=s.read_json(self.root/'bookshelf_source.json');self.assertEqual(personal['rows'][0],row('personal-old','Keep personal'));self.assertEqual(personal['rows'][1][7],'Persian')
  self.assertFalse(s.ingest(self.root,self.scan)['changed']);self.assertTrue((self.root/'sync_pending.local.json').exists())
 def test_incomplete_scan_never_writes(self):
  before=(self.root/'public_library_catalog.csv').read_bytes();self.scan['complete']=False
  with self.assertRaises(ValueError):s.ingest(self.root,self.scan)
  self.assertEqual(before,(self.root/'public_library_catalog.csv').read_bytes());self.assertFalse((self.root/'sync_pending.local.json').exists())
 def test_same_id_in_other_vault_is_not_deduplicated(self):
  self.scan['vaults']['bookshelf']['files'].append(file('public-old'))
  result=s.ingest(self.root,self.scan);self.assertEqual(result['added']['bookshelf'],2)
 def test_upstream_additions_do_not_replace_manual_edits(self):
  upstream=s.read_json(self.root/'bookshelf_source.json');upstream['rows'][0][2]='Less certain replacement';upstream['rows'].append(row('upstream-new','Added upstream'));upstream['summary']['review_ids']=['upstream-new']
  s.ingest(self.root,self.scan,upstream=upstream)
  result=s.read_json(self.root/'bookshelf_source.json');self.assertEqual(result['rows'][0][2],'Manually corrected author');self.assertIn('upstream-new',result['summary']['review_ids'])
 def test_recovery_preserves_concurrent_edits(self):
  before=s.read_csv(self.root/'public_library_catalog.csv');after=before+[row('recover','Recover')]
  s.write_json(self.root/'sync_pending.local.json',{'writes':{'public_library_catalog.csv':{'before':before,'after':after}}})
  s.recover(self.root);self.assertEqual(s.read_csv(self.root/'public_library_catalog.csv'),after)
  edited=copy.deepcopy(after);edited[1][2]='New manual correction';s.write_csv(self.root/'public_library_catalog.csv',edited)
  with self.assertRaises(ValueError):s.recover(self.root)
if __name__=='__main__':unittest.main()
