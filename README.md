# Public Library

[Open the searchable catalog](https://ehsanbz.github.io/my-public-library-catalog/)

1,416 catalog entries from 1,533 files across 216 folders, inventoried 15 October 2026. 117 software/image assets excluded from the catalog and retained in the inventory.

The Bookshelf interface supports normalized Persian/Arabic search, filters, sorting, table and card views, details, and CSV export. Books stay on Google Drive; links preserve the resource keys and existing access permissions.

## Metadata

Metadata has been enriched using document text, explicit filename credits, author collections, and curated bibliographic corrections. Titles have been cleaned; authors, translators and biography subjects are distinguished. Categories follow the original Bookshelf vocabulary. Language is checked against extracted text where readable; remaining language inferences are explicitly marked in each entry. 1,356 entries have named authors and 1,414 have a language assignment. Unknown fields remain Unknown; years, ISBNs and editions are not invented. Review flags identify remaining uncertainty, and the per-entry notes preserve original filenames and folder paths. Archive contents are not expanded; one file is one entry. Potential duplicates are retained, with matching title/author/language/volume groups flagged for review.

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
