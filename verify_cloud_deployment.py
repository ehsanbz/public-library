"""Verify deployed catalog bytes; safe to retry after a successful Pages deployment."""
import pathlib
import subprocess
import time
import urllib.request

root = pathlib.Path(__file__).resolve().parent
commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
for attempt in range(12):
    try:
        for name in ['index.html', 'catalog_data.json', 'book_catalog.csv',
                     'public_library_catalog.csv', 'bookshelf_catalog.csv']:
            request = urllib.request.Request('https://ehsanbz.github.io/public-library/'+name+'?commit='+commit,
                                             headers={'Cache-Control': 'no-cache'})
            with urllib.request.urlopen(request, timeout=30) as response:
                assert response.read() == (root/name).read_bytes(), 'Deployment differs from committed catalog'
        print('Live combined catalog and both separate vault exports verified.')
        break
    except (OSError, AssertionError):
        if attempt == 11:
            raise
        time.sleep(10)
