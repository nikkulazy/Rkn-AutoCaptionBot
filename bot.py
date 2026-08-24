# (c) @RknDeveloperr
# Rkn Developer 
# Don't Remove Credit 😔

import sys
import os
import asyncio
import aiohttp
from aiohttp import web
from pyrogram import Client
from config import Rkn_Bots as Rkn_Botz

try:
    from web_support import web_server
except ImportError:
    print("⚠️ web_support not found, using dummy web server")
    async def web_server():
        web_app = web.Application()
        async def root_handler(request):
            return web.json_response({"status": "running", "bot": "Rkn-AutoCaptionBot"})
        web_app.router.add_get("/", root_handler)
        web_app.router.add_get("/health", root_handler)
        return web_app

class Rkn_AutoCaptionBot(Client):
    def __init__(self):
        super().__init__(
            name="Rkn-Advance-Caption-Bot",
            api_id=Rkn_Botz.API_ID,
            api_hash=Rkn_Botz.API_HASH,
            bot_token=Rkn_Botz.BOT_TOKEN,
            workers=200,
            plugins={"root": "."},  # ✅ Root se load karein
            sleep_threshold=15,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.uptime = Rkn_Botz.BOT_UPTIME
        self.force_channel = Rkn_Botz.FORCE_SUB
        
        # Web Server Setup
        app_runner = web.AppRunner(await web_server())
        await app_runner.setup()
        bind_address = "0.0.0.0"
        port = int(os.environ.get("PORT", "8080"))
        site = web.TCPSite(app_runner, bind_address, port)
        await site.start()
        print(f"🌐 Web server started on port {port}")
        
        # Console Output
        print(f"\n{'='*50}")
        print(f"✅ {me.first_name} Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️")
        print(f"📋 Bot ID: {me.id}")
        print(f"📋 Log Channel: {Rkn_Botz.LOG_CHANNEL or 'Not Set'}")
        print(f"🌐 Port: {port}")
        print(f"{'='*50}\n")
        
        # Notify Admins
        for admin_id in Rkn_Botz.ADMIN:
            try:
                await self.send_message(
                    admin_id, 
                    f"**🚀 {me.first_name} Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️**\n\n"
                    f"✅ Bot is now LIVE!\n"
                    f"📋 Bot ID: {me.id}\n"
                    f"📋 Log Channel: {Rkn_Botz.LOG_CHANNEL or 'Not Set'}"
                )
            except:
                pass
        
    async def stop(self, *args):
        await super().stop()
        print("Bot Stopped 🙄")
        
if __name__ == "__main__":
    Rkn_AutoCaptionBot().run()
