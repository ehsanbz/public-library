"""Additive, vault-scoped ingestion of a complete connector scan. No credentials required.

The scheduled agent performs Drive reads with scan_vaults.js and publishes only the
allowlisted outputs. This module never moves, deletes or changes Drive permissions.
"""
import argparse,csv,datetime,hashlib,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parent
NAMES={'public-library':'Public Library','bookshelf':'My Bookshelf'}
EXT={'pdf','epub','mobi','azw','azw3','djvu','doc','docx','rtf','chm','htm','html','mht','txt','rar','zip','mp3'}
EXCLUDE={'book_catalog.html','book_catalog.csv','index.html','library_readme.txt','readme.txt','readme.md'}
CATEGORIES={'Arts & Culture','Biography & Memoir','Business & Economics','Health','Historical Fiction','History','Language & Linguistics','Literary Fiction','Mystery & Thriller','Philosophy','Psychology','Religion','Science','Science Fiction','Social Sciences','Technology & Computing','Travel & Geography'}
def read_json(p,default=None):return json.loads(p.read_text(encoding='utf-8')) if p.exists() else default
def write_json(p,value):
 temp=p.with_suffix(p.suffix+'.tmp');temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8');temp.replace(p)
def read_csv(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.reader(f))
def write_csv(p,rows):
 temp=p.with_suffix('.csv.tmp')
 with temp.open('w',encoding='utf-8-sig',newline='') as f:csv.writer(f).writerows(rows)
 temp.replace(p)
def read_document(path):return read_csv(path) if path.suffix=='.csv' else read_json(path)
def recover(root):
 pending=read_json(root/'sync_pending.local.json',{})
 for name,change in pending.get('writes',{}).items():
  path=root/name;current=read_document(path)
  if current==change['after']:continue
  if current!=change['before']:raise ValueError('Concurrent edit while recovering '+name+'; preserve and reconcile it before retrying')
  (write_csv if path.suffix=='.csv' else write_json)(path,change['after'])
def candidate(f):
 name=f['title'].casefold();folder=f.get('folder','').casefold()
 return (name not in EXCLUDE and pathlib.Path(name).suffix.lstrip('.') in EXT and
  not any(part.endswith('_files') or part in {'.git','node_modules','__macosx','_ needed softwares'} for part in folder.split('/')) and
  f.get('mime_type') not in {'application/vnd.google-apps.shortcut','application/vnd.google-apps.folder'})
def validate_scan(scan):
 if not scan.get('complete') or scan.get('errors'):raise ValueError('Incomplete Drive scan: do not ingest or checkpoint')
 if set(scan.get('vaults',{}))!=set(NAMES):raise ValueError('Both vaults must be scanned independently')
 for v in scan['vaults'].values():
  ids=[f['id'] for f in v['files']]
  if len(ids)!=len(set(ids)):raise ValueError('Repeated file IDs within a vault scan')
def new_rows(scan,public,personal):
 validate_scan(scan);known={'public-library':{r[0] for r in public},'bookshelf':{r[0] for r in personal}}
 return [(vault,f) for vault,v in scan['vaults'].items() for f in v['files'] if f['id'] not in known[vault] and candidate(f)]
def default_row(vault,f):
 title=re.sub(r'\.(?:'+('|'.join(EXT))+r')$','',f['title'],flags=re.I).replace('_',' ').strip()
 parts=f.get('folder','').split('/');category=parts[0] if parts[0] in CATEGORIES else 'Unknown'
 sub=parts[1] if category!='Unknown' and len(parts)>1 else 'Needs review'
 kind='Fiction' if category in {'Literary Fiction','Historical Fiction','Science Fiction','Mystery & Thriller'} else 'Nonfiction' if category!='Unknown' else 'Unknown'
 author='Unknown'
 if re.search('مجله|ویرگول',title):category='Arts & Culture';sub='Literary periodicals';kind='Reference';author='Various authors'
 language='Persian' if re.search(r'[\u0600-\u06ff]',f['title']) else 'Unknown'
 notes='REVIEW: New automatically discovered entry; authorship and edition metadata need verification. '
 if language=='Persian':notes+='Persian tag assigned by owner rule for Persian-script filename; book text not independently verified. '
 notes+='Title/category use filename or explicit source folder only. Original file: '+f['title']+' | Source folder: '+f.get('folder','')+'.'
 return [f['id'],title,author,kind,category,sub,sub,language,'Unknown','Unknown',notes,'Unknown','Unknown',pathlib.Path(f['title']).suffix.lstrip('.').upper(),f['url']]
def ingest(root,scan,overrides=None,upstream=None):
 validate_scan(scan);overrides=overrides or {};recover(root)
 pcsv=read_csv(root/'public_library_catalog.csv');headers=pcsv[0];public=pcsv[1:]
 personal=read_json(root/'bookshelf_source.json');old_personal=list(personal['rows'])
 # Original catalog is an additional source: merge by ID without erasing local additions
 # or replacing curated non-Unknown values with inferred upstream guesses.
 upstream_added=0
 if upstream:
  assert upstream['headers']==headers
  known={r[0]:r for r in personal['rows']}
  for r in upstream['rows']:
   if r[0] not in known:personal['rows'].append(r);known[r[0]]=r;upstream_added+=1
  personal['summary']['review_ids']=list(dict.fromkeys(personal['summary']['review_ids']+[i for i in upstream['summary']['review_ids'] if i not in {r[0] for r in old_personal}]))
 additions=new_rows(scan,public,personal['rows']);changed=bool(additions or upstream_added)
 if not changed:return {'changed':False,'added':{v:0 for v in NAMES},'pending':(root/'sync_pending.local.json').exists()}
 pending=root/'sync_pending.local.json'
 if not pending.exists():write_json(pending,{'started_at':scan['started_at'],'status':'prepared','new_ids':{v:[f['id'] for vv,f in additions if vv==v] for v in NAMES},'before_counts':{'public-library':len(public),'bookshelf':len(old_personal)}})
 inventory=read_json(root/'vault_inventory.json');source_order=read_json(root/'metadata_source_order.json');audit=read_json(root/'metadata_audit.json')
 counts={v:0 for v in NAMES};existing_inventory={f['id'] for f in inventory['files']}
 for vault,f in additions:
  r=default_row(vault,f);o=overrides.get(vault+':'+f['id'],{})
  for field,value in o.get('fields',{}).items():
   if field not in headers[1:14]:raise ValueError('Override cannot change source ID/link')
   r[headers.index(field)]=value
  if re.search(r'[\u0600-\u06ff]',f['title']+' '+r[2]) and 'Persian' not in r[7].split('; '):r[7]='; '.join(x for x in [r[7] if r[7]!='Unknown' else '', 'Persian'] if x)
  if vault=='public-library':
   public.append(r)
   if f['id'] not in existing_inventory:source_order[f['id']]=len(inventory['files']);inventory['files'].append(f);existing_inventory.add(f['id'])
  else:
   personal['rows'].append(r);personal['summary']['review_ids'].append(f['id'])
  key=f['id'] if f['id'] not in audit else vault+':'+f['id']
  audit[key]={'vault':NAMES[vault],'author_source':'automatic filename/folder discovery; needs review','language_source':'owner Persian tagging rule' if 'Persian' in r[7] else 'unverified','source_path':f.get('folder',''),'discovered_at':scan['finished_at']}
  counts[vault]+=1
 # Every existing row survives untouched; new IDs are idempotent within each vault.
 assert public[:len(pcsv)-1]==pcsv[1:]
 assert personal['rows'][:len(old_personal)]==old_personal
 for rows in [public,personal['rows']]:assert len(rows)==len({r[0] for r in rows}) and all(len(r)==15 for r in rows)
 day=scan['finished_at'][:10];config=read_json(root/'sync_config.json',{})
 config['catalog_updated_at']=day
 if counts['public-library']:config['public_updated_at']=day
 if counts['bookshelf'] or upstream_added:
  personal['summary'].update(updated_at=day,catalog_output_rows=len(personal['rows']),review_count=len(personal['summary']['review_ids']))
 payload={'public_library_catalog.csv':[headers,*public],'bookshelf_source.json':personal,'vault_inventory.json':inventory,'metadata_source_order.json':source_order,'metadata_audit.json':audit,'sync_config.json':config}
 transaction=read_json(pending);transaction['writes']={name:{'before':read_document(root/name),'after':value} for name,value in payload.items()};write_json(pending,transaction);recover(root)
 write_json(root/'sync_last_apply.local.json',{'changed':True,'added':counts,'upstream_added':upstream_added,'finished_at':scan['finished_at']})
 return {'changed':True,'added':counts,'upstream_added':upstream_added,'pending':True}
def main():
 a=argparse.ArgumentParser();a.add_argument('action',choices=['plan','apply','published']);a.add_argument('--root',type=pathlib.Path,default=ROOT);a.add_argument('--scan',type=pathlib.Path);a.add_argument('--upstream',type=pathlib.Path);a.add_argument('--commit');args=a.parse_args();root=args.root
 if args.action=='published':
  if not args.commit:raise ValueError('A verified published commit is required')
  write_json(root/'sync_checkpoint.local.json',{'last_successful_publish':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commit':args.commit})
  (root/'sync_pending.local.json').unlink(missing_ok=True);print('Publication checkpoint saved.');return
 scan=read_json(args.scan or root/'latest_scan.local.json');p=read_csv(root/'public_library_catalog.csv');personal=read_json(root/'bookshelf_source.json')
 if args.action=='plan':print(json.dumps({'complete':scan.get('complete'),'new_candidates':[{'vault':v,**f} for v,f in new_rows(scan,p[1:],personal['rows'])]},ensure_ascii=True));return
 print(json.dumps(ingest(root,scan,read_json(root/'sync_additions.local.json',{}),read_json(args.upstream) if args.upstream else None)))
if __name__=='__main__':main()
