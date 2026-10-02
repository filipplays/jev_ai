# GitHub Pages for JEV

This folder is intended to be served via GitHub Pages (use `docs/` in the repository root).

Quick deploy

1. Create a GitHub repository and push this project.
2. In the repository Settings → Pages, select `main` (or `master`) branch and `docs/` folder as the source.
3. Visit the provided URL: `https://<github-username>.github.io/<repo>/docs/` or `https://<github-username>.github.io/<repo>/` depending on Pages configuration.

Configuration steps you must perform

- Edit `docs/jev_mobile.html` and set `WORKER_URL` to your published Cloudflare Worker URL (e.g. `https://jev-proxy-worker.<id>.workers.dev`).
- In your Cloudflare Worker, set `ALLOWED_ORIGIN` to your GitHub Pages origin (for example `https://your-username.github.io`). You can set that as a variable in `wrangler.toml` under `[vars]` or in the Cloudflare Dashboard.

Example `wrangler.toml` snippet to set `ALLOWED_ORIGIN`:

```toml
[vars]
ALLOWED_ORIGIN = "https://your-username.github.io"
```

Then re-run `wrangler publish` to apply the change.

Notes
- Do NOT commit secrets such as `JEV_API_KEY`. Use `wrangler secret put JEV_API_KEY` and `wrangler secret put JEV_API_URL`.
- For local testing you can temporarily set `ALLOWED_ORIGIN='*'`, but lock it down before going public.
