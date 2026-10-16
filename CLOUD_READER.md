# Automatic reading and filing

The daily GitHub Actions workflow reads new books from their contents, including scanned PDFs. It needs only the existing Google Drive authorization: no Codex session, local PC, external AI API key or inference subscription.

## Reading process

1. Fully scan both vaults. Prioritize unresolved personal Inbox files, then new eligible files in either vault. Never follow shortcuts.
2. Download a temporary copy on the GitHub runner (up to 100 MiB). Extract PDF opening pages, credits, contents and three body samples. Image-only pages use Tesseract OCR with Persian, English, Arabic and German recognition. EPUB, DOCX, TXT and basic RTF text are supported too.
3. Run the Apache-2.0 [Qwen3-4B model](https://huggingface.co/Qwen/Qwen3-4B-GGUF) on the runner CPU through llama.cpp. Model weights are pinned to a revision. No book contents are sent to Hugging Face or an external inference API; Hugging Face only supplies model weights.
4. Independently detect text languages using Lingua. Keep the owner's Persian policy tag separate from languages detected in sampled text.
5. Accept titles and author names only when normalized exact supporting spans exist in sampled text. Constrain output to JSON and categories/subcategories already in the personal catalog. Ignore instructions inside books. Only classifications meeting confidence and evidence checks can guide a move.
6. Fill unknown metadata and replace automatically generated filename titles. Preserve curated fields, IDs and links. Machine-read metadata remains reviewable. Persist page numbers, OCR method, language results, model version and file fingerprint in catalog provenance, never excerpts or extracted text.
7. Sort reliably categorized personal Inbox books, verify their new parents, rebuild separate/combined catalogs, publish and check the live site. Public Library files remain read-only, even when their new metadata is analyzed.

## Limits and recovery

The reader samples up to eleven PDF pages, not the entire book. It processes up to eight candidates per daily run; remaining candidates are picked up on later runs, including entries already added with Unknown metadata. Cached fingerprints avoid repeated work. Unreadable or unresolved files are retried once; a changed file or reader version enables another attempt. Password-protected, oversized, unsupported or ambiguous files stay marked for review. Saved web pages with companion assets remain in Inbox.

OCR and model confidence are imperfect. Authors may remain Unknown and ambiguous books may remain in Inbox. Scanned languages beyond the installed OCR packs may require another language pack. Existing curated data takes precedence.

Book copies, images, OCR text, prompts and responses exist only in the temporary runner session. They are excluded from commits, Pages, uploaded artifacts and caches. The model has no tools or credentials; separate constrained code validates and performs Drive moves. Credentials remain in the existing Actions secret.

The schedule remains daily at 16:23 UTC; GitHub can delay starts. The runner has a 90-minute timeout and caches Python build dependencies. Your PC can remain off.
