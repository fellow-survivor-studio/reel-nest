# Reel Nest Legal Documents

Public site for the Reel Nest Android app's privacy policy and terms of use.

## GitHub Pages

1. Push this repository to the `main` branch.
2. Open **Settings → Pages** in GitHub.
3. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
4. Select the `main` branch and `/(root)` folder.

GitHub Pages publishes the generated files in the repository root, so a push to
`main` publishes immediately. The public URLs are:

- Privacy policy: https://fellow-survivor-studio.github.io/reel-nest/ (other languages at `/{lang}/`)
- Terms of use: https://fellow-survivor-studio.github.io/reel-nest/terms/ (other languages at `/terms/{lang}/`)

Korean is the default at each path; `en`, `ja`, `zh`, `es` and `pt` are the other languages.

## Updating the documents

The texts must match the ones shipped in the app
(`app/src/main/assets/legal/privacy_policy_*.txt` and `terms_of_use_*.txt`).

The privacy policy promises that the previous version stays viewable on this
site, so before overwriting a text, move the current one to
`content/archive/<privacy_policy|terms_of_use>_<lang>_<YYYY-MM-DD>.txt`, where the
date is its effective date. Previous versions are published under `archive/<date>/`
(and `terms/archive/<date>/`), linked from the current page and excluded from the
sitemap. A Korean file is required for each archived date.

Then copy the new texts into `content/` and run:

```sh
python scripts/build_site.py
```

Commit both the updated source files and generated root/`dist` files. Publish
on the same day as the app release that ships the same texts, and for a terms
change follow the notice period in the terms (Article 3).
