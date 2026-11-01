# LIVEHUB public link discovery upgrade

This package adds a scheduled public-web discovery crawler and displays discovered links in the LIVEHUB Discover view.

## What it does

- Searches public Google News RSS and Reddit RSS for sports viewing discussions and provider information.
- Extracts URLs from public RSS descriptions and public pages.
- Crawls only domains explicitly listed in `LIVEHUB_ALLOWED_HOSTS`.
- Detects supported media URL types (`.m3u8`, `.mp4`, `.mpd`, YouTube, and provider embed/player URLs).
- Writes results to `data/discovery.json`, which the existing LIVEHUB page reads and displays.
- Keeps ordinary search results and discussion pages as leads, not as fake playable channels.

## Important limits

A discovered URL is not proof that a stream is live, authorized, or embeddable. The crawler does not bypass logins, DRM, paywalls, geographic restrictions, anti-bot controls, or provider access restrictions. Only add domains for providers whose content you are authorized to display. Some providers block third-party embedding even when their pages are public.

This is a public-link discovery index, not a crawler of the entire internet. It uses public RSS feeds and a bounded crawl of operator-allowlisted sites.

## Configure allowed provider domains

In GitHub: **Settings → Secrets and variables → Actions → Variables → New repository variable**.

- Name: `LIVEHUB_ALLOWED_HOSTS`
- Value: comma-separated hostnames, for example `example-broadcaster.com,player.example-provider.com`

Use provider domains only when you have permission to display their media. Do not include URL schemes or paths. The crawler does not treat an allowlisted domain as proof of content rights.

Optional variable:
- `LIVEHUB_MAX_CRAWL_PAGES`: maximum provider pages crawled per run (default 60).

## Run locally

```bash
python3 discovery.py
```

Then serve the project directory with a local web server, for example:

```bash
python3 -m http.server 8000
```

Open `http://localhost:8000`.

## Deploy

Replace the repository's `discovery.py`, `README.md`, and `index.html` with the files in this package, and preserve `.github/workflows/refresh-discovery.yml` and `data/`. Commit and push. The existing GitHub Actions workflow refreshes the index every six hours and can also be run manually from the Actions tab.

The player can only play direct media or embeds that the provider permits the browser to load. CORS, CSP, geolocation, sign-in, and DRM restrictions may prevent playback; those restrictions cannot be fixed by extracting a URL.
