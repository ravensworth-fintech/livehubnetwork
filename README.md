# LIVEHUB — in-app playback and discovery upgrade

This is a static GitHub Pages frontend plus a scheduled GitHub Actions discovery index.

## What changed

- Clicking a supported discovery candidate now loads it into the LIVEHUB player instead of opening Reddit, Google, or GitHub search results in another tab.
- Discovery records distinguish ordinary community/search leads from playable candidates.
- The scanner extracts explicit URLs from Reddit listing content, but promotes a URL to a playable candidate only when its host is in `LIVEHUB_ALLOWED_HOSTS` and its format is supported (HLS `.m3u8`, MP4, YouTube, or an explicitly supplied `/embed/` or `/player/` URL).
- The Add Source dialog supports official embeddable player URLs.
- Ordinary provider homepages remain labelled as portals. LIVEHUB does not pretend a homepage is a video stream.

## Install/update in your existing repository

1. Download and unzip this package.
2. In your existing `ravensworth-fintech/livehubnetwork` repository, replace `index.html`, `discovery.py`, and `README.md` with the versions in this package. Upload the `data/discovery.json` file too if it is included.
3. Preserve `.github/workflows/refresh-discovery.yml` or use the included version.
4. In Settings → Secrets and variables → Actions → Variables, optionally set `LIVEHUB_ALLOWED_HOSTS` to comma-separated domains you have independently confirmed are authorized to distribute or embed their streams. Example format: `public-broadcaster.example,official-provider.example`. Leave it empty until verified.
5. Go to Actions → Refresh LIVEHUB discovery index → Run workflow.
6. When it succeeds, wait for Pages to deploy, then hard-refresh LIVEHUB.

## Playback limits and rights

- Allowlisting is a technical filter, not proof of copyright or redistribution permission. Only add domains whose owners authorize the stream for this use.
- A Reddit post, news article, repository, or channel homepage is not itself a playable video. Those remain discovery leads unless an explicit supported media/player URL is found.
- Browser playback may still fail because of provider CORS rules, codecs, DRM, geographic restrictions, login requirements, or embed restrictions. LIVEHUB cannot remove or bypass those restrictions.
- This project does not scrape or expose unauthorized subscription feeds, pirate IPTV, or subscription-bypass streams. It does not proxy, decrypt, or remove ads.
- A static site cannot crawl continuously. GitHub Actions refreshes the index on its six-hour schedule; the frontend loads the generated JSON catalogue.

## Local preview

Run `python -m http.server 8000` in this directory and open `http://localhost:8000`. Run `python discovery.py` to refresh the JSON index (requires network access).
