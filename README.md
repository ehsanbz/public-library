# Public Library

[Open the catalog](https://ehsanbz.github.io/public-library/)

1,920 entries in two distinct vaults: **Public Library (1,416)** and **My Bookshelf (504)**. Use the Include vaults checkboxes to browse either or both. Results stay grouped by vault, even when sorting. Every row, details panel and CSV export records its vault. Books are never moved between vaults; existing IDs and access links are preserved.

## Sources

- Public Library: [Drive vault](https://drive.google.com/drive/folders/0B9wuggJUWO5PejkzOUJZTWx6NGM?resourcekey=0-CHaAwLapPnvIJ7BW3Nj8jw), with the reviewed metadata and Persian tagging rule from this repository.
- My Bookshelf: [Drive vault](https://drive.google.com/drive/folders/1NvUlp3CWKggnwhxBS862_2i1LsIEOsxM) and [original catalog](https://github.com/ehsanbz/bookshelf-catalog), personal metadata updated 2026-10-15. Existing entries, metadata and review flags are preserved; newly discovered files are added by the scheduled sync and uncertain fields are marked for review. The shortcut to Public Library inside this vault is not imported as another copy.

No deduplication or bibliographic merging occurs across vaults. Author, language, category and review filters combine with vault selection. Co-authored books appear under each author. Filtered CSV exports contain only the selected results, with a Vault column. Reset all includes both vaults again.

## Data and rebuilding

- `index.html`: offline-capable interface and embedded data.
- `catalog_data.json` / `book_catalog.csv`: combined browse data, with an explicit Vault field.
- `public_library_catalog.csv` / `bookshelf_catalog.csv`: separate 15-column source catalogs.
- `bookshelf_source.json`: personal-vault metadata master, seeded from the original GitHub catalog and extended by scheduled discovery.
- `vault_inventory.json`, `metadata_source_order.json`, `metadata_rules.py`, `metadata_evidence.json`, `metadata_audit.json`, `metadata_sources.md`: Public Library inventory and metadata evidence; audit records identify imported Bookshelf provenance separately.
- `build_catalog.py` / `catalog_ui.template.html`: builder and interface template.

Run `python build_catalog.py` to rebuild, then `python verify_metadata.py`. `public_library_catalog.csv`, `bookshelf_source.json`, `metadata_audit.json` and `sync_config.json` are durable inputs; preserve them when rebuilding. The published inputs reproduce the catalog without book text or scanned pages. Existing Drive IDs, source paths and provenance are public with the owner’s approval. No books are stored here. Daily checks run on GitHub Actions with Google Drive API authorization and do not require a local computer or Codex. Personal Inbox files are organized within the personal vault; Public Library remains read-only. See [cloud setup](CLOUD_SETUP.md) and `SYNC.md`. The rendered page is a snapshot of the last published metadata update. Full folder traversal finds uploaded books with old modification dates. Private Drive catalog files and the original Bookshelf repository remain read-only.
