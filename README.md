# Public Library

[Open the catalog](https://ehsanbz.github.io/public-library/)

28,692 entries in three distinct collections: **Public Library (1,416)** and **My Bookshelf (507)**, plus **Shervin Vakili Library (26,769)**. Use the Include vaults checkboxes to browse any combination. Results stay grouped by vault, even when sorting. Every row, details panel and CSV export records its vault. Books are never moved between vaults; existing IDs and access links are preserved.

## Sources

- Public Library: [Drive vault](https://drive.google.com/drive/folders/0B9wuggJUWO5PejkzOUJZTWx6NGM?resourcekey=0-CHaAwLapPnvIJ7BW3Nj8jw), with the reviewed metadata and Persian tagging rule from this repository.
- My Bookshelf: [Drive vault](https://drive.google.com/drive/folders/1NvUlp3CWKggnwhxBS862_2i1LsIEOsxM) and [original catalog](https://github.com/ehsanbz/bookshelf-catalog), personal metadata updated 2026-10-22. Existing entries, metadata and review flags are preserved; newly discovered files are added by the scheduled sync and uncertain fields are marked for review. The shortcut to Public Library inside this vault is not imported as another copy.

- Shervin Vakili Library: [Telegram library](https://t.me/SherwinVakiliLibrary), imported from the reviewed local catalog dated 2026-10-23. Only entries classified as Books are included; excluded and unresolved candidates are omitted. Book links open their original Telegram posts. Metadata recovers explicit source labels, subject hashtags and volume markers, plus exact title/author subject matches to the existing catalog. Language and subject estimates based on title/filename wording are explicitly marked **inferred** in Details and remain flagged for review. A translated caption or author nationality does not establish the attachment language. Unknown values remain where evidence is insufficient. Filename and contributor credits are searchable. This is a saved snapshot, preserved by daily rebuilds; Drive synchronization does not fetch Telegram updates.

No deduplication or bibliographic merging occurs across vaults. Author, language, category and review filters combine with vault selection. Co-authored books appear under each author. Filtered CSV exports contain only the selected results, with a Vault column. Reset all includes all three collections again.

## Data and rebuilding

- `index.html`: offline-capable interface and embedded data.
- `catalog_data.json` / `book_catalog.csv`: combined browse data, with an explicit Vault field.
- `public_library_catalog.csv` / `bookshelf_catalog.csv`: separate 15-column source catalogs.
- `shervin_vakili_source.json` / `shervin_vakili_catalog.csv`: durable Telegram collection metadata and separate export.
- `shervin_vakili_metadata.json`: saved source descriptors (filename, labeled caption lines, hashtags and contributor credits). `enrich_shervin.py` recovers metadata; `shervin_vakili_metadata_audit.json` records field values, basis and source excerpts; `shervin_vakili_metadata_report.json` records coverage. Run enrichment explicitly before rebuilding; daily rebuilds preserve the saved enriched source.
- `bookshelf_source.json`: personal-vault metadata master, seeded from the original GitHub catalog and extended by scheduled discovery.
- `vault_inventory.json`, `metadata_source_order.json`, `metadata_rules.py`, `metadata_evidence.json`, `metadata_audit.json`, `metadata_sources.md`: Public Library inventory and metadata evidence; audit records identify imported Bookshelf provenance separately.
- `build_catalog.py` / `catalog_ui.template.html`: builder and interface template.

Run `python build_catalog.py` to rebuild, then `python verify_metadata.py`. `public_library_catalog.csv`, `bookshelf_source.json`, `metadata_audit.json` and `sync_config.json` are durable inputs; preserve them when rebuilding. The published inputs reproduce the catalog without book text or scanned pages. Existing Drive IDs, source paths and provenance are public with the owner’s approval. No books are stored here. Daily checks run on GitHub Actions with Google Drive API authorization and do not require a local computer or Codex. New books are read with text extraction, OCR and a multilingual model on the cloud runner. Reliably categorized personal Inbox files are filed within the personal vault; Public Library remains read-only. See CLOUD_READER.md. See [cloud setup](CLOUD_SETUP.md) and `SYNC.md`. The rendered page is a snapshot of the last published metadata update. Full folder traversal finds uploaded books with old modification dates. Private Drive catalog files and the original Bookshelf repository remain read-only.
