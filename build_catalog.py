import pathlib,json,re,csv,collections
root=pathlib.Path(__file__).resolve().parent
sync=json.loads((root/'sync_config.json').read_text(encoding='utf-8'))
previous_audit=json.loads((root/'metadata_audit.json').read_text(encoding='utf-8')) if (root/'metadata_audit.json').exists() else {}
source=json.loads((root/'vault_inventory.json').read_text(encoding='utf-8'))
assert not source['remaining']
headers=['Original ID','Book Title','Author(s)','Book Type','Main Category','Subcategory','Topic Tags','Language','Publication Year','Series / Volume','Notes / Uncertainty','ISBN','Edition','Format','Shelf / File Location']
rows=[]; excluded=[]
topics={'PHILOSOPHY':'Philosophy','HISTORY':'History','POLITIC':'Politics & Society','PSYCHOLOGY':'Psychology','RELIGION':'Religion & Spirituality','SOCIOLOGY':'Politics & Society','LITERATURE':'Literature & Cinema','SCIENCE':'Science','ECONOM':'Economics','POET':'Poetry','ART':'Arts','MUSIC':'Music'}
for f in source['files']:
 name=f['title']; folder=f['folder']; ext=pathlib.Path(name).suffix.lower().lstrip('.')
 if ext in ['exe','jpg','jpeg','gif','png','dll','ini'] or '_ NEEDED SOFTWARES' in folder:
  excluded.append(f);continue
 title=re.sub(r'\.(pdf|djvu|epub|docx?|rtf|htm[l]?|rar|zip|mp3)$','',name,flags=re.I).strip()
 parts=folder.split('/'); top=parts[0]; author=top if top!='0-OTHERS' else 'Unknown'
 cat='Literature' if top!='0-OTHERS' else 'Unknown';sub=top
 for key,value in topics.items():
  if key in folder.upper() and top=='0-OTHERS':cat=value;sub=parts[1] if len(parts)>1 else top;break
 if top=='0-OTHERS' and '0-POEM' in folder:cat='Poetry';sub='Poetry'
 if top=='0-OTHERS' and '0-NOVEL & STORY' in folder:cat='Literature';sub='Novels & Short Stories'
 if top=='0-OTHERS' and 'RELIGIOUS' in folder:cat='Religion & Spirituality';sub='Religion'
 if top=='0-OTHERS' and 'TRANING' in folder:cat='Learning & Skills';sub='Practical guides'
 if top=='0-OTHERS' and '0-POEM' in folder and len(parts)>2:author=parts[2]
 if top in ['ARISTOTLE','SOREN KIERKEGAARD','Friedrich Wilhelm Nietzsche','BERTRAND RUSSELL']:cat='Philosophy'
 if top in ['احمد شاملو','فروغ فرخزاد','سهراب سپهری']:cat='Poetry'
 fmt=ext.upper() if ext in ['pdf','djvu','epub','doc','docx','rtf','htm','html','rar','zip','mp3'] else ('PDF' if f['mime_type']=='application/pdf' else 'Unknown')
 typ='Archive / Collection' if fmt in ['RAR','ZIP'] else 'Audio' if fmt=='MP3' else 'Document'
 notes='Filename-derived title; author and subject inferred from source folder; contents, language and edition not verified. Source folder: '+folder
 if author=='Unknown':notes+=' Author unknown; source folder is a subject collection.'
 # Language is intentionally unverified: script and author nationality do not establish a book language.
 language='English' if '/IN ENGLISH' in folder else 'Persian' if '/IN PERSIAN' in folder else 'Unknown'
 if language!='Unknown':notes+=' Language inferred from explicit source-folder label.'
 rows.append([f['id'],title,author,typ,cat,sub,'Source folder: '+folder,language,'Unknown','Unknown',notes,'Unknown','Unknown',fmt,f['url']])
from metadata_rules import enrich,key,EVIDENCE
source_by_id={f['id']:(i,f) for i,f in enumerate(source['files'])}
enriched=[];review_ids=[];audit={}
for row in rows:
 i,f=source_by_id[row[0]]
 revised,review,trace=enrich(i,f,row)
 enriched.append(revised);audit[row[0]]=trace
 if review:review_ids.append(row[0])
rows=enriched
groups=collections.defaultdict(list)
for row in rows:
 if row[2] not in ['Unknown','Various authors']:groups[(key(row[1]),key(row[2]),row[7],row[9])].append(row)
duplicate_groups=[group for group in groups.values() if len(group)>1]
for n,group in enumerate(duplicate_groups,1):
 for row in group:row[10]+=' DUP-'+str(n)+': matching normalized title, author, language and volume; retained as separate files, not confirmed identical copies.'
rows.sort(key=lambda r:(r[4].casefold(),r[5].casefold(),r[2].casefold(),r[9].casefold(),r[1].casefold()))
# Per-vault source CSV is the metadata master: rebuilding must preserve manual edits.
if (root/'public_library_catalog.csv').exists():
 with (root/'public_library_catalog.csv').open(encoding='utf-8-sig',newline='') as stream:master=list(csv.reader(stream))
 assert master[0]==headers and all(len(r)==15 for r in master[1:])
 rows=master[1:]
 review_ids=[r[0] for r in rows if r[10].startswith('REVIEW:')]
 for r in rows:
  if r[0] in previous_audit and previous_audit[r[0]].get('vault','Public Library')=='Public Library':audit[r[0]]=previous_audit[r[0]]
  elif 'public-library:'+r[0] in previous_audit:audit[r[0]]=previous_audit['public-library:'+r[0]]
assert len(rows)==len({r[0] for r in rows})
summary={'screened_files':len(source['files']),'catalog_output_rows':len(rows),'review_ids':review_ids,'review_count':len(review_ids),'duplicate_groups':len(duplicate_groups),'duplicate_rows':sum(map(len,duplicate_groups)),'updated_at':sync['catalog_updated_at'],'excluded_assets':len(excluded),'folders_scanned':len(source['folders']),'authors_identified':sum(r[2] not in ['Unknown','Various authors'] for r in rows),'languages_identified':sum(r[7]!='Unknown' for r in rows),'category_counts':dict(collections.Counter(r[4] for r in rows)),'language_counts':dict(collections.Counter(r[7] for r in rows)),'text_extraction_attempted':len(EVIDENCE),'language_confirmed_from_text':sum(v.get('text_readable_language',False) for v in audit.values())}
personal=json.loads((root/'bookshelf_source.json').read_text(encoding='utf-8'))
assert personal['headers']==headers
with (root/'public_library_catalog.csv').open('w',encoding='utf-8-sig',newline='') as out:csv.writer(out).writerows([headers,*rows])
with (root/'bookshelf_catalog.csv').open('w',encoding='utf-8-sig',newline='') as out:csv.writer(out).writerows([headers,*personal['rows']])
vaults=[{'id':'public-library','name':'Public Library','drive_url':'https://drive.google.com/drive/folders/0B9wuggJUWO5PejkzOUJZTWx6NGM?resourcekey=0-CHaAwLapPnvIJ7BW3Nj8jw','repository_url':'https://github.com/ehsanbz/public-library','csv':'public_library_catalog.csv','count':len(rows),'review_ids':review_ids,'updated_at':sync['public_updated_at']},
 {'id':'bookshelf','name':'My Bookshelf','drive_url':'https://drive.google.com/drive/folders/1NvUlp3CWKggnwhxBS862_2i1LsIEOsxM','repository_url':'https://github.com/ehsanbz/bookshelf-catalog','csv':'bookshelf_catalog.csv','count':len(personal['rows']),'review_ids':personal['summary']['review_ids'],'updated_at':personal['summary']['updated_at']}]
rows=[r+['Public Library'] for r in rows]+[r+['My Bookshelf'] for r in personal['rows']]
for r in personal['rows']:
 audit_key='bookshelf:'+r[0] if r[0] in audit else r[0]
 previous_personal=previous_audit.get('bookshelf:'+r[0]) or previous_audit.get(r[0],{})
 audit[audit_key]=previous_personal if previous_personal.get('vault')=='My Bookshelf' else{'vault':'My Bookshelf','author_source':'imported unchanged from bookshelf-catalog','language_source':'imported unchanged from bookshelf-catalog','source_repository':'https://github.com/ehsanbz/bookshelf-catalog','source_catalog_date':personal['summary']['updated_at']}
for v in audit.values():v.setdefault('vault','Public Library')
headers=headers+['Vault']
summary.update(catalog_output_rows=len(rows),vault_counts={v['name']:v['count'] for v in vaults},review_ids=review_ids+personal['summary']['review_ids'],review_count=len(review_ids)+len(personal['summary']['review_ids']),authors_identified=sum(r[2] not in ['Unknown','Various authors'] for r in rows),languages_identified=sum(r[7]!='Unknown' for r in rows),category_counts=dict(collections.Counter(r[4] for r in rows)),language_counts=dict(collections.Counter(r[7] for r in rows)))
data={'headers':headers,'rows':rows,'summary':summary,'vaults':vaults,'sync':{'enabled':sync['enabled'],'frequency':sync['frequency'],'execution':sync['execution']}}
(root/'catalog_data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'metadata_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
with (root/'book_catalog.csv').open('w',encoding='utf-8-sig',newline='') as out:csv.writer(out).writerows([headers,*rows])
template=(root/'catalog_ui.template.html').read_text(encoding='utf-8')
payload=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
html=template.replace('__CATALOG_DATA__',payload)
(root/'index.html').write_text(html,encoding='utf-8')
(root/'.nojekyll').write_text('',encoding='utf-8')
(root/'README.md').write_text(f'''# Public Library

[Open the catalog](https://ehsanbz.github.io/public-library/)

{len(rows):,} entries in two distinct vaults: **Public Library ({vaults[0]['count']:,})** and **My Bookshelf ({vaults[1]['count']:,})**. Use the Include vaults checkboxes to browse either or both. Results stay grouped by vault, even when sorting. Every row, details panel and CSV export records its vault. Books are never moved or combined across Drive folders; existing IDs and access links are preserved.

## Sources

- Public Library: [Drive vault](https://drive.google.com/drive/folders/0B9wuggJUWO5PejkzOUJZTWx6NGM?resourcekey=0-CHaAwLapPnvIJ7BW3Nj8jw), with the reviewed metadata and Persian tagging rule from this repository.
- My Bookshelf: [Drive vault](https://drive.google.com/drive/folders/1NvUlp3CWKggnwhxBS862_2i1LsIEOsxM) and [original catalog](https://github.com/ehsanbz/bookshelf-catalog), personal metadata updated {personal['summary']['updated_at']}. Existing entries, metadata and review flags are preserved; newly discovered files are added by the scheduled sync and uncertain fields are marked for review. The shortcut to Public Library inside this vault is not imported as another copy.

No deduplication or bibliographic merging occurs across vaults. Author, language, category and review filters combine with vault selection. Co-authored books appear under each author. Filtered CSV exports contain only the selected results, with a Vault column. Reset all includes both vaults again.

## Data and rebuilding

- `index.html`: offline-capable interface and embedded data.
- `catalog_data.json` / `book_catalog.csv`: combined browse data, with an explicit Vault field.
- `public_library_catalog.csv` / `bookshelf_catalog.csv`: separate 15-column source catalogs.
- `bookshelf_source.json`: personal-vault metadata master, seeded from the original GitHub catalog and extended by scheduled discovery.
- `vault_inventory.json`, `metadata_source_order.json`, `metadata_rules.py`, `metadata_evidence.json`, `metadata_audit.json`, `metadata_sources.md`: Public Library inventory and metadata evidence; audit records identify imported Bookshelf provenance separately.
- `build_catalog.py` / `catalog_ui.template.html`: builder and interface template.

Run `python build_catalog.py` to rebuild, then `python verify_metadata.py`. `public_library_catalog.csv`, `bookshelf_source.json`, `metadata_audit.json` and `sync_config.json` are durable inputs; preserve them when rebuilding. The published inputs reproduce the catalog without book text or scanned pages. Existing Drive IDs, source paths and provenance are public with the owner’s approval. No books are stored here. Automatic hourly checks use connected Drive and GitHub tools through Codex desktop. Keep the computer on, awake and the app running; this is not a cloud-only Drive watcher. The rendered page is a snapshot of the last published metadata update. See `SYNC.md`. Files are discovered by full folder traversal, so uploaded books with old modification dates are still found. Drive files, private Drive catalogs and the original Bookshelf repository are read-only to this scheduled workflow.
''',encoding='utf-8')
assert json.loads(re.search(r'<script id="catalog-data" type="application/json">(.*?)</script>',html,re.S)[1])==data
assert len(list(csv.reader((root/'book_catalog.csv').open(encoding='utf-8-sig'))))-1==len(rows)
print(json.dumps({k:v for k,v in summary.items() if k!='review_ids'},ensure_ascii=True))
