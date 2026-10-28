# Public Library

[Open the catalog](https://ehsanbz.github.io/public-library/)

117,067 entries in three collections: **Public Library (1,416)**, **Shervin Vakili Library (62,431)** and **Litera999 (53,220)**. Use the Include vaults checkboxes to browse any combination. Results stay grouped by vault, even when sorting. Every row, details panel and CSV export records its vault. Books are never moved between vaults; existing IDs and access links are preserved.

## Sources

- Public Library: [Drive vault](https://drive.google.com/drive/folders/0B9wuggJUWO5PejkzOUJZTWx6NGM?resourcekey=0-CHaAwLapPnvIJ7BW3Nj8jw), with the reviewed metadata and Persian tagging rule from this repository.

- Shervin Vakili Library: [Telegram library](https://t.me/SherwinVakiliLibrary), updated from the supplied CSV dated 2026-10-28. Existing reviewed records and IDs are preserved by matching original post links. Previously reviewed records absent from the CSV are retained. New CSV entries retain their source titles and notes; missing bibliographic fields remain Unknown and flagged for review.
- Litera999: [Telegram library](https://t.me/litera999), imported from the supplied CSV dated 2026-10-28. Source titles, notes and post links are preserved. Bibliographic fields and attachment formats remain unverified and flagged for review. Both Telegram collections are saved snapshots preserved by daily rebuilds; Drive synchronization does not fetch Telegram updates.

No deduplication or bibliographic merging occurs across vaults. Author, language, category and review filters combine with vault selection. Co-authored books appear under each author. Filtered CSV exports contain only the selected results, with a Vault column. Reset all includes all three collections again.

## Data and rebuilding

- `index.html`: offline-capable interface and embedded data.
- `catalog_data.json` / `book_catalog.csv`: combined browse data, with an explicit Vault field.
- `public_library_catalog.csv`: 15-column Public Library source catalog.
- `shervin_vakili_source.json` / `shervin_vakili_catalog.csv`: durable Telegram collection metadata and separate export.
- `shervin_vakili_provenance.json`: original inventory IDs, every book attachment/post reference, and bibliographic source links from the validated review checkpoint.
- `shervin_vakili_metadata.json`: saved source descriptors (filename, labeled caption lines, hashtags and contributor credits). `enrich_shervin.py` recovers metadata; `shervin_vakili_metadata_audit.json` records field values, basis and source excerpts; `shervin_vakili_metadata_report.json` records coverage. Run enrichment explicitly before rebuilding; daily rebuilds preserve the saved enriched source.
- `litera999_source.json` / `litera999_catalog.csv`: fourth collection source and export.
- `shervin_vakili_csv_reference.json` / `litera999_csv_reference.json`: complete supplied CSV records and input checksums. `reference_import_report.json` records reconciliation counts.
- `bookshelf_source.json`: personal-vault maintenance data, excluded from the public catalog.
- `vault_inventory.json`, `metadata_source_order.json`, `metadata_rules.py`, `metadata_evidence.json`, `metadata_audit.json`, `metadata_sources.md`: Public Library inventory and metadata evidence; audit records identify imported Bookshelf provenance separately.
- `build_catalog.py` / `catalog_ui.template.html`: builder and interface template.

Run `python build_catalog.py` to rebuild, then `python verify_metadata.py`. `public_library_catalog.csv`, `bookshelf_source.json`, `metadata_audit.json` and `sync_config.json` are durable inputs; preserve them when rebuilding. The published inputs reproduce the catalog without book text or scanned pages. Existing Drive IDs, source paths and provenance are public with the owner’s approval. No books are stored here. Daily checks run on GitHub Actions with Google Drive API authorization and do not require a local computer or Codex. New books are read with text extraction, OCR and a multilingual model on the cloud runner. Reliably categorized personal Inbox files are filed within the personal vault; Public Library remains read-only. See CLOUD_READER.md. See [cloud setup](CLOUD_SETUP.md) and `SYNC.md`. The rendered page is a snapshot of the last published metadata update. Full folder traversal finds uploaded books with old modification dates. Private Drive catalog files and the original Bookshelf repository remain read-only.
