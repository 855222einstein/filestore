import os
from aiohttp import web


async def _health(request):
    return web.Response(text="Bot is running.")


async def start_webserver():
    """Bind Render's $PORT so the Web Service health check passes."""
    app = web.Application()
    app.router.add_get("/", _health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
