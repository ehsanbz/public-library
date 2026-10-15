import pathlib,json,re,csv,collections
root=pathlib.Path(__file__).resolve().parent
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
assert len(rows)==len({r[0] for r in rows})
summary={'screened_files':len(source['files']),'catalog_output_rows':len(rows),'review_ids':review_ids,'review_count':len(review_ids),'duplicate_groups':len(duplicate_groups),'duplicate_rows':sum(map(len,duplicate_groups)),'updated_at':'2026-10-15','excluded_assets':len(excluded),'folders_scanned':len(source['folders']),'authors_identified':sum(r[2] not in ['Unknown','Various authors'] for r in rows),'languages_identified':sum(r[7]!='Unknown' for r in rows),'category_counts':dict(collections.Counter(r[4] for r in rows)),'language_counts':dict(collections.Counter(r[7] for r in rows)),'text_extraction_attempted':len(EVIDENCE),'language_confirmed_from_text':sum(v['text_readable_language'] for v in audit.values())}
data={'headers':headers,'rows':rows,'summary':summary}
(root/'catalog_data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'metadata_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
with (root/'book_catalog.csv').open('w',encoding='utf-8-sig',newline='') as out:csv.writer(out).writerows([headers,*rows])
template=(root/'catalog_ui.template.html').read_text(encoding='utf-8')
payload=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
html=template.replace('__CATALOG_DATA__',payload)
(root/'index.html').write_text(html,encoding='utf-8')
(root/'.nojekyll').write_text('',encoding='utf-8')
(root/'README.md').write_text(f'''# Public Library

[Open the searchable catalog](https://ehsanbz.github.io/my-public-library-catalog/)

{len(rows):,} catalog entries from {len(source['files']):,} files across {len(source['folders'])} folders, inventoried 15 October 2026. {len(excluded)} software/image assets excluded from the catalog and retained in the inventory.

The Bookshelf interface supports normalized Persian/Arabic search, filters, sorting, table and card views, details, and CSV export. Books stay on Google Drive; links preserve the resource keys and existing access permissions.

## Metadata

Metadata has been enriched using document text, explicit filename credits, author collections, and curated bibliographic corrections. Titles have been cleaned; authors, translators and biography subjects are distinguished. Categories follow the original Bookshelf vocabulary. Language is checked against extracted text where readable; remaining language inferences are explicitly marked in each entry. {summary['authors_identified']:,} entries have named authors and {summary['languages_identified']:,} have a language assignment. Unknown fields remain Unknown; years, ISBNs and editions are not invented. Review flags identify remaining uncertainty, and the per-entry notes preserve original filenames and folder paths. Archive contents are not expanded; one file is one entry. Potential duplicates are retained, with matching title/author/language/volume groups flagged for review.

## Files and updates

- `index.html`: standalone catalog, also usable offline.
- `book_catalog.csv`: UTF-8 catalog with the same 15 columns as Bookshelf.
- `catalog_data.json`: catalog data and summary.
- `vault_inventory.json`: source file metadata and scanned folder paths.
- `catalog_ui.template.html` and `build_catalog.py`: reusable interface and builder.
- `metadata_rules.py`: curated normalization and bibliographic corrections.
- `metadata_audit.json`: field provenance for the enriched catalog.
- `metadata_evidence.json` and `metadata_source_order.json`: reproducible language evidence and stable source mapping.
- `metadata_sources.md`: methodology, uncertainty policy and bibliographic references.

Run `python build_catalog.py` after updating the inventory, evidence, rules and template. Local extracted-text evidence supports the audit; book text is not published to this repository. The Drive inventory is a snapshot and does not refresh automatically. GitHub Pages serves the main branch root.
''',encoding='utf-8')
assert json.loads(re.search(r'<script id="catalog-data" type="application/json">(.*?)</script>',html,re.S)[1])==data
assert len(list(csv.reader((root/'book_catalog.csv').open(encoding='utf-8-sig'))))-1==len(rows)
print(json.dumps({k:v for k,v in summary.items() if k!='review_ids'},ensure_ascii=True))
