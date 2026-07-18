# (c) @RknDeveloperr
# Rkn Developer 
# Don't Remove Credit 😔

from aiohttp import web
from pyrogram import Client
from config import Rkn_Bots, Rkn_Bots as Rkn_Botz
from Rkn_Bots.web_support import web_server
from Rkn_Bots.logger import Logger

class Rkn_AutoCaptionBot(Client):
    def __init__(self):
        super().__init__(
            name="Rkn-Advance-Caption-Bot",
            api_id=Rkn_Bots.API_ID,
            api_hash=Rkn_Bots.API_HASH,
            bot_token=Rkn_Bots.BOT_TOKEN,
            workers=200,
            plugins={"root": "Rkn_Bots"},
            sleep_threshold=15,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.uptime = Rkn_Botz.BOT_UPTIME
        self.force_channel = Rkn_Bots.FORCE_SUB
        
        # 🟢 Initialize Logger
        self.logger = Logger(self)
        
        # 🟢 Send Bot Started Log to Channel
        await self.logger.bot_started()
        
        # Force Sub Channel Setup
        if Rkn_Bots.FORCE_SUB:
            try:
                link = await self.export_chat_invite_link(Rkn_Bots.FORCE_SUB)
                self.invitelink = link
            except Exception as e:
                print(e)
                print("Make Sure Bot admin in force sub channel")
                self.force_channel = None
        
        # Web Server Setup
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, Rkn_Bots.PORT).start()
        
        # Console Output
        print(f"\n{'='*50}")
        print(f"✅ {me.first_name} Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️")
        print(f"📋 Log Channel: {Rkn_Bots.LOG_CHANNEL or 'Not Set'}")
        print(f"{'='*50}\n")
        
        # Notify Admins
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
        # 🟢 Send Bot Stopped Log
        if hasattr(self, 'logger'):
            await self.logger.bot_stopped()
        await super().stop()
        print("Bot Stopped 🙄")
        
Rkn_AutoCaptionBot().run()

# Rkn Developer 
# Don't Remove Credit 😔
