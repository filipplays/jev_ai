// Simple Cloudflare Worker to fetch weather and forward to JEV AI securely.
// Expects a POST JSON body: { "lat": <num>, "lon": <num> }
// Requires two secrets set in Cloudflare: JEV_API_KEY and JEV_API_URL

addEventListener('fetch', event => {
    event.respondWith(handle(event.request, event));
});

async function handle(request, event) {
    if (request.method === 'OPTIONS') {
        return new Response(null, { status: 204, headers: corsHeaders() });
    }

    if (request.method !== 'POST') {
        return new Response(JSON.stringify({ error: 'Use POST' }), { status: 405, headers: htmlCors() });
    }

    try {
        const body = await request.json();
        const { lat, lon } = body;
        if (typeof lat !== 'number' || typeof lon !== 'number') {
            return new Response(JSON.stringify({ error: 'Provide numeric lat and lon' }), { status: 400, headers: jsonCors() });
        }

        // Example public weather API (no key required)
        const weatherUrl = `https://api.open-meteo.com/v1/forecast?latitude=${encodeURIComponent(lat)}&longitude=${encodeURIComponent(lon)}&current_weather=true`;
        const wRes = await fetch(weatherUrl);
        const weatherJson = await wRes.json();

        // Forward weather to JEV AI protected by secret key
        const jevUrl = JEV_API_URL || (typeof JEV_API_URL === 'string' ? JEV_API_URL : undefined);
        // In Wrangler/Workers you should set a secret named JEV_API_KEY and a secret or env var JEV_API_URL.
        // Access them via global bindings when using Modules or via env in newer setups.
        // Here we read from global scope name (will work when you bind secrets with Wrangler as global bindings).

        const JEV_URL = typeof JEV_API_URL !== 'undefined' ? JEV_API_URL : null;
        const JEV_KEY = typeof JEV_API_KEY !== 'undefined' ? JEV_API_KEY : null;

        if (!JEV_URL || !JEV_KEY) {
            return new Response(JSON.stringify({ error: 'JEV_API_URL and JEV_API_KEY must be configured as Worker secrets' }), { status: 500, headers: jsonCors() });
        }

        const jevRes = await fetch(JEV_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${JEV_KEY}`
            },
            body: JSON.stringify({ weather: weatherJson })
        });

        const jevJson = await jevRes.json();

        return new Response(JSON.stringify({ weather: weatherJson, jev: jevJson }), {
            status: 200,
            headers: jsonCors()
        });
    } catch (err) {
        return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: jsonCors() });
    }
}

function corsHeaders() {
    // Use ALLOWED_ORIGIN binding if provided (set in wrangler.toml [vars] or dashboard),
    // otherwise fall back to '*' for quick testing.
    const allowed = (typeof ALLOWED_ORIGIN !== 'undefined' && ALLOWED_ORIGIN) ? ALLOWED_ORIGIN : '*';
    return {
        'Access-Control-Allow-Origin': allowed,
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    };
}

function jsonCors() {
    return Object.assign({ 'Content-Type': 'application/json' }, corsHeaders());
}

function htmlCors() {
    return Object.assign({ 'Content-Type': 'text/plain' }, corsHeaders());
}
