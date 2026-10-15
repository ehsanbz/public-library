# MY PUBLIC LIBRARY catalog

[Open the searchable catalog](https://ehsanbz.github.io/my-public-library-catalog/)

1,416 catalog entries from 1,533 files across 216 folders, inventoried 15 October 2026. 117 software/image assets excluded from the catalog and retained in the inventory.

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
