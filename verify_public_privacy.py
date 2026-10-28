from pathlib import Path
import json,re,base64,gzip,csv
root=Path(__file__).resolve().parent
approved={'index.html','book_catalog.csv','public_library_catalog.csv','shervin_vakili_catalog.csv','litera999_catalog.csv','.nojekyll','README.md','verify_public_privacy.py','AGENTS.md','.github/workflows/catalog-publish.yml'}
actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and '.git' not in p.relative_to(root).parts}
assert actual<=approved, 'Unapproved files: '+str(actual-approved)
html=(root/'index.html').read_text(encoding='utf-8')
packed=re.search(r'<script id="catalog-data" type="application/octet-stream">(.*?)</script>',html).group(1)
data=json.loads(gzip.decompress(base64.b64decode(packed)))
assert data.get('access_links_published') is False
assert data['sync']['enabled'] is False
assert all(r[0].startswith('CAT-') and not r[14] for r in data['rows'])
assert not re.search(r'https?://|(?:t[.]me|telegram[.]me|drive[.]google[.]com|docs[.]google[.]com)/',json.dumps(data),re.I)
assert all(not any(k in v for k in ('drive_url','source_url','url')) for v in data['vaults'])
for p in root.glob('*.csv'):
 with p.open(encoding='utf-8-sig',newline='') as f:
  records=list(csv.reader(f))
  assert all(r[0].startswith('CAT-') and not r[14] for r in records[1:]), p.name
 assert not re.search(r'https?://',p.read_text(encoding='utf-8-sig')), p.name
assert not re.search(r'https?://(?:drive[.]google[.]com|docs[.]google[.]com|t[.]me|telegram[.]me)',html,re.I)
print('PASS: metadata only; no original file identifiers or book access links; source synchronization paused.')
