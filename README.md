# Reel Nest Privacy Policy

Public privacy-policy site for the Reel Nest Android app.

## GitHub Pages

1. Push this repository to the `main` branch.
2. Open **Settings → Pages** in GitHub.
3. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
4. Select the `main` branch and `/(root)` folder.

GitHub Pages publishes the generated files in the repository root. The public URL is:

https://fellow-survivor-studio.github.io/reel-nest/

## Updating the policy

Edit the localized files in `content/`, then run:

```sh
python scripts/build_site.py
```

Commit both the updated source files and generated root/`dist` files.
