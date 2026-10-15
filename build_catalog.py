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
rows.sort(key=lambda r:(r[4].casefold(),r[5].casefold(),r[2].casefold(),r[1].casefold()))
assert len(rows)==len({r[0] for r in rows})
summary={'screened_files':len(source['files']),'catalog_output_rows':len(rows),'review_ids':[r[0] for r in rows],'review_count':len(rows),'duplicate_groups':0,'duplicate_rows':0,'updated_at':'2026-10-15','excluded_assets':len(excluded),'folders_scanned':len(source['folders'])}
data={'headers':headers,'rows':rows,'summary':summary}
(root/'catalog_data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
with (root/'book_catalog.csv').open('w',encoding='utf-8-sig',newline='') as out:csv.writer(out).writerows([headers,*rows])
template=(root/'catalog_ui.template.html').read_text(encoding='utf-8')
payload=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
html=template.replace('__CATALOG_DATA__',payload)
(root/'index.html').write_text(html,encoding='utf-8')
(root/'.nojekyll').write_text('',encoding='utf-8')
(root/'README.md').write_text(f'''# MY PUBLIC LIBRARY catalog

[Open the searchable catalog](https://ehsanbz.github.io/my-public-library-catalog/)

{len(rows):,} catalog entries from {len(source['files']):,} files across {len(source['folders'])} folders, inventoried 15 October 2026. {len(excluded)} software/image assets excluded from the catalog and retained in the inventory.

The Bookshelf interface supports normalized Persian/Arabic search, filters, sorting, table and card views, details, and CSV export. Books stay on Google Drive; links preserve the resource keys and existing access permissions.

## Metadata

Titles come from filenames; authors and subjects are inferred from folder labels. All entries are flagged for review. Language, publication year, ISBN, series, and edition remain Unknown until verified. Archive contents are not expanded; one file is one entry. Duplicates are retained, and content-based duplicate detection has not been performed. This is a complete file inventory, not a verified bibliographic edition catalog.

## Files and updates

- `index.html`: standalone catalog, also usable offline.
- `book_catalog.csv`: UTF-8 catalog with the same 15 columns as Bookshelf.
- `catalog_data.json`: catalog data and summary.
- `vault_inventory.json`: source file metadata and scanned folder paths.
- `catalog_ui.template.html` and `build_catalog.py`: reusable interface and builder.

Run `python build_catalog.py` after updating the inventory and template. The Drive inventory is a snapshot and does not refresh automatically. GitHub Pages serves the main branch root.
''',encoding='utf-8')
assert json.loads(re.search(r'<script id="catalog-data" type="application/json">(.*?)</script>',html,re.S)[1])==data
assert len(list(csv.reader((root/'book_catalog.csv').open(encoding='utf-8-sig'))))-1==len(rows)
print(json.dumps({k:v for k,v in summary.items() if k!='review_ids'},ensure_ascii=True))
