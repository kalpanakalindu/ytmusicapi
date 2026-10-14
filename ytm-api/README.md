# Vortify YouTube Music API

Read-only API on top of [ytmusicapi](https://github.com/sigma67/ytmusicapi), no login needed.

## Run locally
    python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    python api/index.py          # http://localhost:5000/health

## Deploy on Vercel
1. Push this folder to a GitHub repo.
2. vercel.com -> Add New -> Project -> import the repo -> Deploy (no build settings needed).
3. Open https://YOUR-PROJECT.vercel.app/health and /search?q=believer&filter=songs

Or with the CLI: `npm i -g vercel`, then `vercel login` and `vercel --prod` in this folder.

Optional environment variables (Project -> Settings -> Environment Variables):
- `YTM_LOCATION` country code for results (LK, US, GB ...)
- `ALLOW_ORIGIN` your site URL instead of `*`
