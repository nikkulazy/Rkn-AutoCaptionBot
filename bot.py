# (c) @RknDeveloperr
# Rkn Developer 
# Don't Remove Credit 😔

from aiohttp import web
from pyrogram import Client
from config import Rkn_Bots as Rkn_Botz
from web_support import web_server

# ✅ Logger
try:
    from logger import Logger
except ImportError:
    print("⚠️ Logger not found, creating dummy logger")
    class Logger:
        def __init__(self, bot):
            self.bot = bot
        async def bot_started(self):
            print("🚀 Bot Started!")
        async def bot_stopped(self):
            print("🛑 Bot Stopped!")
        async def user_start(self, *args, **kwargs):
            pass
        async def channel_setup(self, *args, **kwargs):
            pass
        async def channel_removed(self, *args, **kwargs):
            pass
        async def caption_set(self, *args, **kwargs):
            pass
        async def caption_deleted(self, *args, **kwargs):
            pass
        async def buttons_set(self, *args, **kwargs):
            pass
        async def buttons_removed(self, *args, **kwargs):
            pass
        async def caption_edited(self, *args, **kwargs):
            pass
        async def broadcast_started(self, *args, **kwargs):
            pass
        async def broadcast_completed(self, *args, **kwargs):
            pass
        async def admin_action(self, *args, **kwargs):
            pass
        async def system_error(self, *args, **kwargs):
            pass
        async def forward_file_to_log(self, *args, **kwargs):
            pass

class Rkn_AutoCaptionBot(Client):
    def __init__(self):
        super().__init__(
            name="Rkn-Advance-Caption-Bot",
            api_id=Rkn_Botz.API_ID,
            api_hash=Rkn_Botz.API_HASH,
            bot_token=Rkn_Botz.BOT_TOKEN,
            workers=200,
            plugins={"root": "."},
            sleep_threshold=15,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.uptime = Rkn_Botz.BOT_UPTIME
        self.force_channel = Rkn_Botz.FORCE_SUB
        
        # 🟢 Initialize Logger
        self.logger = Logger(self)
        
        # 🟢 Send Bot Started Log to Channel
        try:
            await self.logger.bot_started()
        except Exception as e:
            print(f"⚠️ Bot start log error: {e}")
        
        # Force Sub Channel Setup
        if Rkn_Botz.FORCE_SUB:
            try:
                link = await self.export_chat_invite_link(Rkn_Botz.FORCE_SUB)
                self.invitelink = link
            except Exception as e:
                print(e)
                print("Make Sure Bot admin in force sub channel")
                self.force_channel = None
        
        # Web Server Setup
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, Rkn_Botz.PORT).start()
        
        # Console Output
        print(f"\n{'='*50}")
        print(f"✅ {me.first_name} Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️")
        print(f"📋 Log Channel: {Rkn_Botz.LOG_CHANNEL or 'Not Set'}")
        print(f"{'='*50}\n")
        
        # Notify Admins
        for admin_id in Rkn_Botz.ADMIN:
            try:
                await self.send_message(
                    admin_id, 
                    f"**🚀 {me.first_name} Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️**\n\n"
                    f"✅ Bot is now LIVE!\n"
                    f"📋 Log Channel: {Rkn_Botz.LOG_CHANNEL or 'Not Set'}"
                )
            except:
                pass
        
    async def stop(self, *args):
        # 🟢 Send Bot Stopped Log
        if hasattr(self, 'logger'):
            try:
                await self.logger.bot_stopped()
            except Exception as e:
                print(f"⚠️ Bot stop log error: {e}")
        await super().stop()
        print("Bot Stopped 🙄")
        
Rkn_AutoCaptionBot().run()

# Rkn Developer 
# Don't Remove Credit 😔
