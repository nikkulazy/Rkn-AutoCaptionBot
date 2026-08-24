# web_support.py - Web Server Support
# (c) @RknDeveloperr

from aiohttp import web
import time

Rkn_AutoCaptionBot = web.RouteTableDef()
START_TIME = time.time()

@Rkn_AutoCaptionBot.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response({
        "status": "running",
        "bot": "Rkn-AutoCaptionBot",
        "uptime": round(time.time() - START_TIME, 2)
    })

@Rkn_AutoCaptionBot.get("/health")
async def health_check(request):
    return web.json_response({
        "status": "healthy",
        "uptime": round(time.time() - START_TIME, 2)
    })

async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(Rkn_AutoCaptionBot)
    return web_app
