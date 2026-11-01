# LIVEHUB — Personal Streaming Starter

A lightweight, static, browser-based streaming directory. It uses one HTML file, browser storage, and HLS.js (loaded from jsDelivr) for compatible HLS playback.

## Included
- Sports-first home page and categories for Sports, Live TV, News, Entertainment, International, Favorites, and My Sources
- Starter directory of official free streaming destinations
- Search and favorites
- Add your own authorized source URLs
- Official YouTube embed support (ads may appear; this app does not block them)
- Direct HLS (.m3u8) and MP4 playback where the source permits browser playback
- Local browser storage for custom sources, favorites, and recent history

## Important playback notes
- This is a directory/player shell, not a source provider. It does not include pirated playlists, private feeds, DRM circumvention, stream proxies, or ad removal.
- Many broadcasters do not permit third-party embedding. Their cards open the official provider site instead.
- A source can be free to watch but still show ads, require an account, be region-restricted, or restrict embedding.
- Direct HLS playback requires the source to allow browser cross-origin access (CORS). If it does not, open the provider's official player.
- 1080p depends on the original source and your connection.
- ABC/CBS/NBC/FOX local network livestreams are not universally free online. The included cards link to official portals; local live access may require a TV provider or other eligibility.
- This app does not block YouTube ads.

## Easiest setup: GitHub + Vercel (browser-only)

1. Download and unzip `livehub-starter.zip` on your computer.
2. Open GitHub and create a new **public** repository named `livehub` (public repositories can use GitHub's free hosting/deployment integrations; the app itself contains no secrets).
3. In the new repository, choose **Add file → Upload files**.
4. Upload `index.html` from the unzipped folder and commit the change to the `main` branch. (You may also upload this README.)
5. Open Vercel and sign in with the same GitHub account.
6. Choose **Add New → Project**, import the `livehub` repository.
7. If Vercel asks for framework settings, select **Other**. Leave Build Command and Install Command empty. Set Output Directory to `.` (a single period); `vercel.json` in this starter also records the static-site configuration.
8. Click **Deploy**. When deployment finishes, open the generated `.vercel.app` address.
9. Bookmark that address. The app is ready to use.

## Updating later
1. Open the `livehub` repository on GitHub.
2. Open `index.html`, choose the pencil/edit action, make the change, and commit.
3. Vercel automatically redeploys the updated site.
4. Refresh the site in your browser.

## Adding a channel
1. Open the website and click **Add source**.
2. Enter a name, category, source type, and URL.
3. Choose:
   - **Official website** for a provider page (opens in a new tab).
   - **Official YouTube** for a YouTube watch/live URL (official player; ads may appear).
   - **Direct HLS** for an authorized `.m3u8` URL.
   - **Direct MP4** for an authorized `.mp4` URL.
4. Save. Your custom source is stored in this browser.

## Storage
Favorites, recent history, and custom sources are saved in the browser's local storage. They remain on this browser profile and are not synced to another computer. Clearing browser site data will erase them. Export/backup is not included in this starter version.

## Free hosting note
Vercel Hobby is for personal, non-commercial projects and has usage/fair-use limits. Do not use this app as a stream proxy or media host. Video plays directly from the original provider.
