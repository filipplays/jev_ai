# Cloudflare Worker: JEV proxy

This Worker fetches a public weather API (no key needed) and forwards the weather payload to your JEV AI endpoint using a secret API key.

Quick steps to deploy

1. Install Wrangler (Cloudflare CLI):

```bash
npm install -g wrangler
# or: corepack enable && corepack prepare pnpm@latest --activate
```

2. Login and set account id:

```bash
wrangler login
# optional: wrangler whoami  # shows account details
```

3. Add secrets (do NOT commit these):

```bash
wrangler secret put JEV_API_KEY
wrangler secret put JEV_API_URL
```

Set `JEV_API_URL` to your JEV AI endpoint (example: `https://api.your-jev.com/decide`).

4. Publish the Worker:

```bash
wrangler publish
```

Notes
- The script uses Open-Meteo (example) for current weather based on `lat` and `lon` you POST.
- The Worker returns both the `weather` and the `jev` response JSON.
- For production, replace `Access-Control-Allow-Origin: *` with your frontend origin.

Example client call (from your frontend):

```js
const res = await fetch('https://<your-worker-subdomain>.workers.dev', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ lat: 51.5074, lon: -0.1278 })
});
const data = await res.json();
console.log(data.jev); // JEV AI decision
```

Security
- Never commit your `JEV_API_KEY` to git. Use `wrangler secret put` or the Cloudflare dashboard to set secrets.
- Limit CORS to your site in the Worker before going public.
