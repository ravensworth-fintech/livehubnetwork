# LIVEHUB discovery bundle

This package adds a scheduled, multi-source discovery index to the existing browser-based LIVEHUB app. It uses free public GitHub Actions runners and static JSON hosting; it does not require a paid database or video host.

## What it searches

- Reddit public search RSS for community discussions and viewing recommendations. These are **leads only**; the app does not extract or play stream URLs from discussion posts.
- GitHub repository search for open-source live-TV and public-stream projects. Repositories are **leads only**; check licenses and source provenance.
- The public iptv-org playlist, but direct playlist entries are imported only when their host matches an explicit `LIVEHUB_ALLOWED_HOSTS` repository variable. Host allowlisting is not proof of broadcast rights; independently verify rights before enabling playback.
- The browser also provides one-click searches across DuckDuckGo, Reddit, GitHub and YouTube for the user's query.

## Deploy for free

1. Create a **private GitHub repository** for personal use and upload this folder's contents.
2. In repository Settings → Actions → General, allow workflows to create and approve pull requests / write repository contents (or ensure the workflow's `contents: write` permission is allowed).
3. In Settings → Secrets and variables → Actions → Variables, optionally create `LIVEHUB_ALLOWED_HOSTS` as a comma-separated list of domains you have independently verified are authorized to distribute the streams. Leave it empty by default.
4. Open Actions → Refresh LIVEHUB discovery index → Run workflow. It will also run every six hours.
5. Host the repository with GitHub Pages (Settings → Pages → Deploy from branch, select `main` and `/ (root)`). The resulting site serves `index.html` and `data/discovery.json` from the same origin.

GitHub Pages is public hosting: do not publish private notes, personal credentials, or anything you expect to remain private. For private access, use an access-controlled host; GitHub Pages itself does not provide private-site authentication.

## Important limits

- No service can guarantee free access to every CBS/ABC/NBC/FOX/ESPN feed, NFL game, or paid reality show. Search results may point to official provider pages that require a subscription or TV-provider login.
- This project intentionally does not scrape or extract unauthorized Ace Stream, pirate IPTV, or subscription-bypass feeds. It does not proxy, decrypt, or remove ads.
- Reddit/GitHub search is rate-limited and may return no results; the workflow logs failures and keeps the last committed catalogue if refresh fails before writing.
- The direct stream allowlist is intentionally empty by default. Add a domain only after verifying that the provider permits public redistribution/embedding.
- Browser playback still depends on CORS, codec, HLS/DASH support, DRM and provider embed policy. A URL can be reachable but not playable.
- A static frontend cannot run continuous background crawling by itself. The scheduled GitHub Actions workflow performs discovery every six hours.

## Local preview

Open `index.html` directly for the UI, or run a local static server from this directory (for example `python -m http.server 8000`) and visit `http://localhost:8000`. The discovery catalogue will populate after `python discovery.py` has run with network access.
