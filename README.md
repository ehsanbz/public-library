# Public Library

[Open the catalog](https://ehsanbz.github.io/public-library/)

1,916 entries in two distinct vaults: **Public Library (1,416)** and **My Bookshelf (500)**. Use the Include vaults checkboxes to browse either or both. Results stay grouped by vault, even when sorting. Every row, details panel and CSV export records its vault. Books are never moved or combined across Drive folders; existing IDs and access links are preserved.

## Sources

- Public Library: [Drive vault](https://drive.google.com/drive/folders/0B9wuggJUWO5PejkzOUJZTWx6NGM?resourcekey=0-CHaAwLapPnvIJ7BW3Nj8jw), with the reviewed metadata and Persian tagging rule from this repository.
- My Bookshelf: [Drive vault](https://drive.google.com/drive/folders/1NvUlp3CWKggnwhxBS862_2i1LsIEOsxM) and [original catalog](https://github.com/ehsanbz/bookshelf-catalog), snapshot dated 2026-10-14. Its 500 entries, metadata and review flags are imported unchanged; Drive and GitHub CSV fields were compared and matched. The shortcut to Public Library inside this vault is not imported as another copy.

No deduplication or bibliographic merging occurs across vaults. Author, language, category and review filters combine with vault selection. Co-authored books appear under each author. Filtered CSV exports contain only the selected results, with a Vault column. Reset all includes both vaults again.

## Data and rebuilding

- `index.html`: offline-capable interface and embedded data.
- `catalog_data.json` / `book_catalog.csv`: combined browse data, with an explicit Vault field.
- `public_library_catalog.csv` / `bookshelf_catalog.csv`: separate 15-column source catalogs.
- `bookshelf_source.json`: unchanged source snapshot from the original GitHub catalog.
- `vault_inventory.json`, `metadata_source_order.json`, `metadata_rules.py`, `metadata_evidence.json`, `metadata_audit.json`, `metadata_sources.md`: Public Library inventory and metadata evidence; audit records identify imported Bookshelf provenance separately.
- `build_catalog.py` / `catalog_ui.template.html`: builder and interface template.

Run `python build_catalog.py` to rebuild, then `python verify_metadata.py`. The published inputs reproduce the catalog without book text or scanned pages. Existing Drive IDs, source paths and provenance are public with the owner’s approval. No books are stored here. This is a snapshot: changes to either Drive vault or the original Bookshelf repository are not automatically imported into this combined catalog. The original Bookshelf catalog remains independently maintained.
