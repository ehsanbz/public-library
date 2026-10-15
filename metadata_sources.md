# Metadata sources and method

## Separate vaults

Automatic maintenance now uses the read-only workflow in `SYNC.md`. The initial imported snapshots contained 1,416 Public Library entries and 500 Bookshelf entries; these are baseline counts, not fixed limits. The first complete scan found four additional periodical PDFs in the personal Inbox and added them with review flags. Existing metadata is preserved in the per-vault masters. New source paths and discovery provenance are recorded separately from previously reviewed credits. The hourly schedule reads Drive files in place and publishes catalog metadata only; it does not organize files, change sharing, or write to the original Bookshelf repository.

The combined catalog keeps Public Library (1,416 entries) and My Bookshelf (500 entries) distinct. The [original Bookshelf repository](https://github.com/ehsanbz/bookshelf-catalog) supplies the unchanged metadata and review flags in `bookshelf_source.json`; the CSV fields were verified identical to the catalog in the [personal Drive vault](https://drive.google.com/drive/folders/1NvUlp3CWKggnwhxBS862_2i1LsIEOsxM). Importing the catalog does not reclassify its entries or reverify its books. Every output row records its vault; records are not deduplicated or combined across sources. The Public Library shortcut inside the personal vault is not followed. Original catalogs are also exported separately. Per-entry audit records distinguish imported Bookshelf metadata from Public Library evidence. Both vaults are snapshots, not automatic synchronizations.

## Public Library evidence

Updated 15 October 2026. All 1,416 catalog entries retain their Drive IDs and original file links. Source filenames and folder paths are retained in each entry’s notes.

The catalog uses the original Bookshelf category vocabulary. Foreign author names use consistent surname-first spelling; Persian authors retain Persian names. Fiction, poetry, drama, memoir, biography, religion, philosophy, political writing and practical guides are distinguished.

Evidence comes from explicit filename credits, author collections, readable document text, and visual inspection of ambiguous scanned title/front-matter pages. `metadata_audit.json` records field provenance. `metadata_evidence.json` contains only language assertions needed to reproduce the catalog, never book text. Local source text and downloaded scans are excluded from the repository.

At the owner’s request, a Persian-script filename or author name, including Iranian authors, assigns a Persian language tag. This catalog policy is not proof of the document’s language: notes and audit fields distinguish policy tags from readable text or visual verification. Confirmed additional languages remain alongside Persian, including English Khayyam/Ferdowsi translations and Azerbaijani poetry. Other unverified language inferences remain in the review filter. Text extraction with control characters or broken font encodings is rejected as language proof. Unknown authors remain Unknown; collective works use Various authors. A translator, editor or biography subject is not silently promoted to the original author. Sacred texts retain unassigned original authorship. Publication years, ISBNs and editions are left unverified unless established for the specific file.

No per-file text lengths, book text, download credentials or scanned pages are published. The review pass rechecked 149 source files through Drive text extraction and downloaded 29 difficult files for direct inspection. Opening and final pages of 24 previously downloaded documents were also revisited where renderable. Final-page signatures established Hamid Hamid, Anton Pannekoek, Perry Anderson and Moslem Mansouri. Scanned drawing-guide credits established Andrew Loomis, Gholamhossein Amirkhani, Gene Franks and Ferdinando Tacconi. Windows-1256 HTML body bylines established Khosrow Shahani and corrected Mohammad Pourthani; office-file editor properties were not used as author credits. Jalal Al-e Ahmad’s first-person autobiography was distinguished from secondary biographies. Readable EPUB/ZIP text, legacy Word narrative, RTF narrative, and visually checked scans resolve additional language inferences. The Penguin Readers adaptation of The Grass Is Singing is distinguished from the unabridged work. Audio tracks and opaque archives remain explicitly unverified.

Bibliographic checks include:

- [University of Dodoma library: The Power of Charm](https://catalog.udom.ac.tz/cgi-bin/koha/opac-detail.pl?biblionumber=4690) — Brian Tracy and Ron Arden.
- [Wiley: Drawing and Designing with Confidence](https://uat.store.wiley.com/en-us/drawing-and-designing-with-confidence-a-step-by-step-guide-p-9780471283904) — Mike W. Lin.
- [Ahmad Shamlou official site: Yerma](https://shamlou.org/?p=347) — Lorca’s play, translated by Shamlou.
- [Ahmad Shamlou official site: Song of Songs](https://shamlou.org/?p=2740) — recreation/translation, distinguished from original authorship.
- [WorldCat: Philosophy and Revolution](https://search.worldcat.org/title/52147472) — Raya Dunayevskaya; also confirmed in the Persian scan.
- [Scanned collection by Rasoul Parvizi](https://fa.wikisource.org/wiki/فهرست:Shalvarha-ye_vassle_dar_-_Rasoul_Parvizi.pdf) — contents identify Qesse-ye Eynakam.

Potential duplicate groups match cleaned title, author, language and volume. They indicate possible same-work overlaps, not byte-identical files; all files remain accessible.
