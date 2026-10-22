import json,csv,re,pathlib
p=pathlib.Path(__file__).resolve().parent
d=json.loads((p/'catalog_data.json').read_text(encoding='utf-8'))
v=json.loads((p/'vault_inventory.json').read_text(encoding='utf-8'))['files']
by={r[0]:r for r in d['rows']}
assert len(d['rows'])==len({(r[15],r[0]) for r in d['rows']})
assert len(d['rows'])==sum(v['count'] for v in d['vaults'])
assert all(len(r)==16 for r in d['rows'])
assert d['headers'][-1]=='Vault'
public=[r for r in d['rows'] if r[15]=='Public Library']
personal=[r for r in d['rows'] if r[15]=='My Bookshelf']
assert len(public)>=1416 and len(personal)>=500
by={r[0]:r for r in public}
all_ids={r[0] for r in d['rows']}
imported=json.loads((p/'bookshelf_source.json').read_text(encoding='utf-8'))
assert [r[:15] for r in personal]==imported['rows'],'Imported metadata changed'
assert next(v for v in d['vaults'] if v['id']=='bookshelf')['review_ids']==imported['summary']['review_ids']
source={f['id']:f for f in v}
assert all(r[14]==source[r[0]]['url'] for r in public)
assert all(r[14].startswith(('https://drive.google.com/','https://docs.google.com/')) for r in public)
original=json.loads((p.parent/'work/catalog_data.json').read_text(encoding='utf-8')) if (p.parent/'work/catalog_data.json').exists() else None
allowed={'Arts & Culture','Biography & Memoir','Business & Economics','Health','Historical Fiction','History','Language & Linguistics','Literary Fiction','Mystery & Thriller','Philosophy','Psychology','Religion','Science','Science Fiction','Social Sciences','Technology & Computing','Travel & Geography','Unknown'}
assert all(r[4] in allowed for r in d['rows'])
def row(i):return by[v[i]['id']]
assert row(377)[2]=='Rolland, Romain'
assert row(425)[2]=='Bickel, Margot'
assert row(719)[2]=='Shaw, George Bernard'
assert row(771)[2]=='Camus, Albert'
assert row(106)[7]=='Romanian'
assert row(923)[7]=='Azerbaijani; Persian'
assert row(1125)[7]==row(1130)[7]=='English; Persian'
assert row(1009)[7]=='Persian'
assert row(804)[7]=='Italian'
assert row(1515)[2]=='Stein, Marky'
assert row(1404)[2]=='Silverstein, Shel'
assert row(1384)[2]=='رسول پرویزی'
assert row(1135)[1]=='دیوان شمس تبریزی'
assert row(943)[1]=='مردان مریخی، زنان ونوسی'
assert row(1428)[1]=='مانیفست حزب کمونیست'
assert row(1244)[2]=='Anderson, Perry'
assert row(1239)[2]=='Pannekoek, Anton'
assert row(1526)[2]=='Loomis, Andrew'
assert all('Persian' in r[7].split('; ') for r in public if re.search(r'[\u0600-\u06ff]',source[r[0]]['title']+' '+r[2]))
assert all(not re.search(r'\.(pdf|docx?|epub|mht|rar|zip)$',r[1],re.I) for r in public)
html=(p/'index.html').read_text(encoding='utf-8')
assert '<title>Public Library</title>' in html
assert '<div class="brand">Public Library</div>' in html
assert '__CATALOG_DATA__' not in html
embedded=json.loads(re.search(r'<script id="catalog-data" type="application/json">(.*?)</script>',html,re.S)[1])
assert embedded==d
with (p/'book_catalog.csv').open(encoding='utf-8-sig',newline='') as f:assert list(csv.reader(f))==[d['headers'],*d['rows']]
assert set(d['summary']['review_ids'])<=all_ids
shervin=json.loads((p/'shervin_vakili_source.json').read_text(encoding='utf-8'))
third=[r for r in d['rows'] if r[15]=='Shervin Vakili Library']
assert [r[:15] for r in third]==shervin['rows']
assert all(re.fullmatch(r'https://t.me/SherwinVakiliLibrary/\d+',r[14]) for r in third)
assert d['summary']['vault_counts']=={'Public Library':len(public),'My Bookshelf':len(personal),'Shervin Vakili Library':len(third)}
for filename,subset in [('public_library_catalog.csv',public),('bookshelf_catalog.csv',personal),('shervin_vakili_catalog.csv',third)]:
 with (p/filename).open(encoding='utf-8-sig',newline='') as f:assert list(csv.reader(f))==[d['headers'][:15],*[r[:15] for r in subset]]
assert all(r[2] not in ['Havaye Tazeh','دیوان شمس تبریزی','ترانه های خیام','مانیفست حزب کمونیست','سنت و سکولاریسم'] for r in d['rows'])
print('PASS: dynamic counts in three distinct collections; source rows and review flags preserved; source links preserved; separate and combined CSVs agree; existing metadata regressions pass.')
