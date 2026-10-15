# Run the library while your computer is off

The repository now includes `.github/workflows/library-sync.yml`: an hourly GitHub-hosted job (at minute 23) with a manual **Run workflow** button. It sorts the personal Inbox, scans both vaults independently, preserves curated metadata, commits additions and deploys GitHub Pages directly. It does not use Codex, a local computer, connector sessions, local scans or local checkpoints. The authoritative metadata masters and builder are checked out from this repository every run. Drive IDs and current parents make moves recoverable even if a runner stops after a move but before publication.

## One-time authorization

The Codex Google Drive connection cannot be exported to GitHub Actions. Provide a separate Google authorization using the repository secret named **GOOGLE_DRIVE_CREDENTIALS_JSON**. Never commit credentials or paste them in issues, chat or workflow logs.

Preferred: use your own Google account's OAuth offline credentials (`type: authorized_user`, with `client_id`, `client_secret`, `refresh_token` and `token_uri: https://oauth2.googleapis.com/token`). Enable the Google Drive API in your Google Cloud project, create a Desktop OAuth client, and authorize Drive access once using `authorize_drive.py`. It opens Google's consent page and saves credentials locally for you to paste directly into the GitHub secret. Use a Google OAuth app in Production (or an eligible Internal app); External apps left in Testing can issue refresh tokens that expire after seven days. See [Google offline access](https://developers.google.com/identity/protocols/oauth2/web-server#offline) and [token expiry](https://developers.google.com/identity/protocols/oauth2#expiration).

An existing service account JSON key is also supported if it has read access to Public Library and Editor access to the personal vault. Share only the required folders with its email address. Service accounts can face My Drive ownership/storage restrictions when creating missing folders: if this occurs, precreate the category/subcategory folders with your own account, or use the recommended user OAuth credentials. Sharing a folder never requires making it public.

1. Open [repository Actions secrets](https://github.com/ehsanbz/public-library/settings/secrets/actions). Add the credential JSON as **GOOGLE_DRIVE_CREDENTIALS_JSON**.
2. Open [Pages settings](https://github.com/ehsanbz/public-library/settings/pages) and select **GitHub Actions** as the publishing source. The workflow deploys directly, because commits made with the workflow token do not trigger a separate branch Pages build.
3. Open [library workflows](https://github.com/ehsanbz/public-library/actions/workflows/library-sync.yml), choose **Run workflow**, and confirm the first run completes, including live deployment verification.
4. After that success, disable the old Codex desktop routine **Organize personal Inbox and sync both vaults** so the two schedulers do not compete. Until then the desktop routine remains available.

## Scope and recovery

- Only eligible personal Inbox files are moved, within the personal category/subcategory hierarchy. Existing metadata guides classification; new uncertain items remain in Inbox for review. Saved web pages requiring assets stay in Inbox for review. Names, file bytes, sharing and unrelated parents are preserved. Public Library is read-only; shortcuts are never followed.
- Both complete vault scans must succeed before Inbox changes. A second scan follows sorting. Pagination is exhausted; incomplete scans fail without committing partial catalogs. Newly uploaded books with old modification dates are found.
- The original Bookshelf repository and private Drive catalog files remain read-only. Their existing metadata is preserved; the original repository supplies additional missing IDs.
- Only allowlisted catalog metadata is committed. No books, raw text, credentials, local move journals or scans are uploaded. The Pages artifact contains only the public catalog and CSV exports.
- Concurrent workflow runs are serialized. A concurrent human commit aborts publication instead of overwriting corrections. A later run starts from current GitHub masters and Drive state, recovering previously moved but unpublished books.
- Hourly is a best-effort schedule, not an immediate Drive event. GitHub may delay scheduled runs and may disable schedules in public repositories after 60 days of repository inactivity. Reenable the workflow in Actions if that happens. See [GitHub scheduled workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).

The cloud job is **not operational until the secret and Pages setup are completed and its first run succeeds**. Existing desktop status in `sync_config.json` remains accurate until that transition is verified.
