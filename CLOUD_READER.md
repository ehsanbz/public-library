# Automatic reading and filing

The daily GitHub Actions workflow reads new books and personal Inbox files from their contents, including scanned PDFs. Existing review-marked books are handled by a separate, manually started one-time cleanup. Both use the existing Google Drive authorization: no Codex session, local PC, external AI API key or inference subscription.

## Reading process

1. Fully scan both vaults. Alternate between vaults so each gets up to two of the four batch slots when both have work. The daily routine handles Inbox files, new discoveries and explicitly queued overflow from those discoveries; it does not process the old review backlog. Never follow shortcuts or merge records across vaults.
2. Download a temporary copy on the GitHub runner (up to 100 MiB). Extract PDF opening pages, credits, contents and three body samples. Image-only pages use Tesseract OCR with Persian, English, Arabic and German recognition. Persian cover/title pages get independent Persian-only layout passes. EPUB, DOCX, TXT and basic RTF text are supported too.
3. Run the Apache-2.0 [Qwen3-8B model](https://huggingface.co/Qwen/Qwen3-8B-GGUF) on the runner CPU through llama.cpp. Model weights are pinned to a revision. No book contents are sent to Hugging Face or an external inference API; Hugging Face only supplies model weights.
4. Read title/author credits separately from subject classification. A separate evidence-backed fiction/nonfiction decision constrains category selection, so an author's reputation does not determine this book's genre. Independently detect text languages using Lingua. Keep the owner's Persian policy tag separate from languages detected in sampled text.
5. Accept titles and author names only when normalized supporting spans exist in sampled text, allowing up to 5% spelling differences on OCR pages. Constrain output to JSON and categories/subcategories already in either catalog, while preserving separate vault records. Ignore instructions inside books. Only classifications meeting confidence and evidence checks can guide a move.
6. Fill unknown metadata and replace automatically generated filename titles. Preserve curated fields, IDs and links. Machine-read metadata remains reviewable. Persist page numbers, OCR method, language results, model version and file fingerprint in catalog provenance, never excerpts or extracted text.
7. Sort reliably categorized personal Inbox books, verify their new parents, rebuild separate/combined catalogs, publish and check the live site. Public Library files remain read-only, even when their new metadata is analyzed.

## Limits and recovery

The reader samples up to eleven PDF pages, not the entire book. The daily routine processes up to four candidates per run and saves excess new discoveries for later runs. A successful read is cached even if some fields remain uncertain; failed new reads may retry once. Provenance records verified text languages separately from preserved catalog language labels. Review flags remain when edition, duplicates or other questions remain unresolved; this is not a promise to clear every flag. Password-protected, oversized, unsupported or ambiguous files stay marked for review. Only the daily personal Inbox organizer can move files.

## One-time review cleanup

Manually start **One-time review of existing books** (`library-review-once.yml`). Leave `campaign_id` blank to save a fixed snapshot of the existing REVIEW-marked books in both vaults. Its `review_campaign.json` checkpoint contains scoped Drive IDs and outcome statuses, not book content. New uploads do not join this snapshot.

The cleanup reads four entries per batch, publishes accepted metadata, then dispatches its next batch immediately. It does not wait for a daily schedule. Each pending entry gets one attempt; matching successful reads already in provenance are retained without repeating them. Unsupported, unreadable, missing or still-uncertain entries get recorded outcomes. No Drive files move during this cleanup.

When the snapshot has no pending entries, its state becomes `complete` and no further batch is dispatched. There is no schedule on this workflow. On infrastructure failure, the chain stops with its last saved checkpoint; rerun the failed job or manually resume with the saved campaign ID. A shared maintenance lock prevents concurrent catalog writes, and continuation waits for an active daily sync rather than replacing its queued run. The regular daily schedule remains unchanged.

OCR and model confidence are imperfect. Authors may remain Unknown and ambiguous books may remain in Inbox. Scanned languages beyond the installed OCR packs may require another language pack. Existing curated data takes precedence.

Book copies, images, OCR text, prompts and responses exist only in the temporary runner session. They are excluded from commits, Pages, uploaded artifacts and caches. The model has no tools or credentials; separate constrained code validates and performs Drive moves. Credentials remain in the existing Actions secret.

The schedule remains daily at 16:23 UTC; GitHub can delay starts. The runner has a 90-minute timeout and caches Python build dependencies. Your PC can remain off.
