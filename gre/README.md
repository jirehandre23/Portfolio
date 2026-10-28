# GRE Vocabulary Master

Open the private study app: https://jireh-gre-study.equitable-fa-3092.chatgpt.site

The GitHub Pages entry point lives at `gre/index.html`. The `source/` directory contains a snapshot of the application source. The live application runs on ChatGPT Sites with an owner-private access policy, ChatGPT sign-in, and Cloudflare D1 persistence. GitHub Pages alone does not provide authentication or database storage. Updating this mirror does not automatically deploy the Sites application; publish changes through the configured Sites project.

## Features
- All 253 original words and all 14 semantic categories.
- French translations, example sentences, near-synonyms, contrasts, and pronunciation.
- Daily mixed quiz: target 10 missed words, 10 due reviews, and up to 10 new words; older words fill shortages, while first-day quizzes are shorter.
- Flashcards, typed recall, and sentence practice.
- Scheduled reviews, missed-word retries, saved sessions, backup export/import.
- Account-scoped cloud saves with optimistic revision checks. Conflicting devices prompt for an explicit choice rather than overwriting silently.

## Moving existing progress online
1. Open your downloaded HTML file and export progress under Display, backup & study guide.
2. Open the online app and import the JSON backup.
3. Wait for Saved to your account.
4. Open the same app on your phone using the same ChatGPT account.

Use one device at a time. Offline changes stay in browser storage; sync when connected. A conflict can be resolved by choosing cloud progress or the local device, preferably exporting a backup first. The app requires an initial online page load; it is not an installable offline PWA.

## Implementation
`source/lib/study-html.ts` contains the self-contained interface. `source/app/api/progress/route.ts` authorizes each request, isolates records by the authenticated user ID, validates state, and uses compare-and-swap revision updates. `source/db/schema.ts` and `source/drizzle/` define the database schema. Private records, credentials, and study backups are not committed here.

Source snapshot deployment commit: `10cd832e89f7716ff937760f67bb1e085f84027b`.
