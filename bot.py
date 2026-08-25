# (c) @RknDeveloperr
# Rkn Developer 
# Don't Remove Credit 😔

import os, sys, asyncio, gc, traceback
from aiohttp import web
from pyrogram import Client, enums
from config import Rkn_Bots, Rkn_Bots as Rkn_Botz

# ✅ Memory optimization
try:
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, -1))
except:
    pass

gc.set_threshold(700, 10, 5)

# ✅ Global exception handler
def global_exception_handler(exc_type, exc_value, exc_traceback):
    print("❌ Unhandled Exception:")
    traceback.print_exception(exc_type, exc_value, exc_traceback)

sys.excepthook = global_exception_handler

# ✅ Logger
try:
    from Rkn_Bots.logger import Logger
except ImportError:
    class Logger:
        def __init__(self, bot): self.bot = bot
        async def bot_started(self): print("🚀 Bot Started!")
        async def bot_stopped(self): print("🛑 Bot Stopped!")
        async def user_start(self, *args, **kwargs): pass
        async def channel_setup(self, *args, **kwargs): pass
        async def channel_removed(self, *args, **kwargs): pass
        async def caption_set(self, *args, **kwargs): pass
        async def caption_deleted(self, *args, **kwargs): pass
        async def buttons_set(self, *args, **kwargs): pass
        async def buttons_removed(self, *args, **kwargs): pass
        async def caption_edited(self, *args, **kwargs): pass
        async def broadcast_started(self, *args, **kwargs): pass
        async def broadcast_completed(self, *args, **kwargs): pass
        async def admin_action(self, *args, **kwargs): pass
        async def system_error(self, *args, **kwargs): pass
        async def forward_file_to_log(self, *args, **kwargs): pass

class Rkn_AutoCaptionBot(Client):
    def __init__(self):
        super().__init__(
            name="Rkn-Advance-Caption-Bot",
            api_id=Rkn_Bots.API_ID,
            api_hash=Rkn_Bots.API_HASH,
            bot_token=Rkn_Bots.BOT_TOKEN,
            workers=100,  # ✅ Reduced
            plugins={"root": "Rkn_Bots"},
            sleep_threshold=15,
            parse_mode=enums.ParseMode.HTML,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.uptime = Rkn_Botz.BOT_UPTIME
        self.force_channel = Rkn_Bots.FORCE_SUB
        
        self.logger = Logger(self)
        
        try:
            await self.logger.bot_started()
        except Exception as e:
            print(f"⚠️ Bot start log error: {e}")
        
        if Rkn_Bots.FORCE_SUB:
            try:
                link = await self.export_chat_invite_link(Rkn_Bots.FORCE_SUB)
                self.invitelink = link
            except Exception as e:
                print(e)
                print("Make Sure Bot admin in force sub channel")
                self.force_channel = None
        
        # ✅ Web Server - Simple and Fast
        try:
            app = web.Application()
            app.router.add_get("/", lambda r: web.Response(text="OK"))
            app.router.add_get("/health", lambda r: web.Response(text="OK"))
            
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, "0.0.0.0", Rkn_Bots.PORT)
            await site.start()
            print(f"✅ Web server on port {Rkn_Bots.PORT}")
        except Exception as e:
            print(f"⚠️ Web server error: {e}")
        
        print(f"\n{'='*50}")
        print(f"✅ {me.first_name} Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️")
        print(f"📋 Log Channel: {Rkn_Bots.LOG_CHANNEL or 'Not Set'}")
        print(f"{'='*50}\n")
        
        for admin_id in Rkn_Bots.ADMIN:
            try:
                await self.send_message(
                    admin_id, 
                    f"**🚀 {me.first_name} Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️**\n\n"
                    f"✅ Bot is now LIVE!\n"
                    f"📋 Log Channel: {Rkn_Bots.LOG_CHANNEL or 'Not Set'}"
                )
            except:
                pass
        
    async def stop(self, *args):
        if hasattr(self, 'logger'):
            try:
                await self.logger.bot_stopped()
            except Exception as e:
                print(f"⚠️ Bot stop log error: {e}")
        await super().stop()
        print("Bot Stopped 🙄")

# ✅ Main with error handling
async def main():
    try:
        Rkn_AutoCaptionBot().run()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        traceback.print_exc()
        await asyncio.sleep(5)
        os.execl(sys.executable, sys.executable, *sys.argv)

if __name__ == "__main__":
    asyncio.run(main())
