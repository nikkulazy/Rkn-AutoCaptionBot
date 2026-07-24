# (c) @RknDeveloperr
# Rkn Developer 
# Don't Remove Credit 😔

from aiohttp import web
from pyrogram import Client
from config import Rkn_Bots, Rkn_Bots as Rkn_Botz
from Rkn_Bots.web_support import web_server
import asyncio
import signal
import sys
import os

# ✅ Logger ko import karo
try:
    from Rkn_Bots.logger import Logger
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

# ✅ Thumbnail Watermark import
try:
    from Rkn_Bots.thumbnail_watermark import init_thumb_watermark
    THUMB_WATERMARK_AVAILABLE = True
except ImportError:
    print("⚠️ Thumbnail Watermark not found, continuing without it")
    THUMB_WATERMARK_AVAILABLE = False
    async def init_thumb_watermark(bot):
        return None

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
        self.is_running = True
        self.web_app = None
        self.web_runner = None
        self.thumb_watermark = None

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.uptime = Rkn_Botz.BOT_UPTIME
        self.force_channel = Rkn_Bots.FORCE_SUB
        
        # 🟢 Initialize Logger
        self.logger = Logger(self)
        
        # 🟢 Initialize Thumbnail Watermark
        if THUMB_WATERMARK_AVAILABLE:
            try:
                self.thumb_watermark = await init_thumb_watermark(self)
                print("✅ Thumbnail Watermark initialized successfully!")
            except Exception as e:
                print(f"⚠️ Thumbnail Watermark init error: {e}")
        else:
            print("ℹ️ Thumbnail Watermark is not available")
        
        # 🟢 Send Bot Started Log to Channel
        try:
            await self.logger.bot_started()
        except Exception as e:
            print(f"⚠️ Bot start log error: {e}")
        
        # Force Sub Channel Setup
        if Rkn_Bots.FORCE_SUB:
            try:
                link = await self.export_chat_invite_link(Rkn_Bots.FORCE_SUB)
                self.invitelink = link
            except Exception as e:
                print(e)
                print("Make Sure Bot admin in force sub channel")
                self.force_channel = None
        
        # Web Server Setup with error handling
        try:
            self.web_app = web.AppRunner(await web_server())
            await self.web_app.setup()
            bind_address = "0.0.0.0"
            site = web.TCPSite(self.web_app, bind_address, Rkn_Bots.PORT)
            await site.start()
            print(f"✅ Web server started on port {Rkn_Bots.PORT}")
        except Exception as e:
            print(f"⚠️ Web server error: {e}")
        
        # Setup signal handlers for graceful shutdown
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                signal.signal(sig, lambda s, f: asyncio.create_task(self.shutdown()))
            except Exception as e:
                print(f"⚠️ Signal handler error: {e}")
        
        # Console Output
        print(f"\n{'='*50}")
        print(f"✅ {me.first_name} Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️")
        print(f"📋 Log Channel: {Rkn_Bots.LOG_CHANNEL or 'Not Set'}")
        if THUMB_WATERMARK_AVAILABLE and hasattr(Rkn_Bots, 'THUMB_WATERMARK_ENABLED'):
            wm_status = "✅ Enabled" if Rkn_Bots.THUMB_WATERMARK_ENABLED else "❌ Disabled"
            print(f"🖼️ Thumbnail Watermark: {wm_status}")
        print(f"{'='*50}\n")
        
        # Notify Admins
        for admin_id in Rkn_Bots.ADMIN:
            try:
                wm_status = ""
                if THUMB_WATERMARK_AVAILABLE and hasattr(Rkn_Bots, 'THUMB_WATERMARK_ENABLED'):
                    wm_status = f"\n🖼️ Thumb Watermark: {'✅' if Rkn_Bots.THUMB_WATERMARK_ENABLED else '❌'}"
                
                await self.send_message(
                    admin_id, 
                    f"**🚀 {me.first_name} Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️**\n\n"
                    f"✅ Bot is now LIVE!\n"
                    f"📋 Log Channel: {Rkn_Bots.LOG_CHANNEL or 'Not Set'}{wm_status}\n\n"
                    f"📌 **Thumbnail Watermark Commands:**\n"
                    f"• `/setthumbwm` - Set watermark text\n"
                    f"• `/thumbwmsettings` - Open settings\n"
                    f"• `/thumbwmpreview` - Preview watermark"
                )
            except Exception as e:
                print(f"⚠️ Could not notify admin {admin_id}: {e}")
        
    async def shutdown(self):
        """Graceful shutdown handler"""
        if not self.is_running:
            return
        self.is_running = False
        print("🔄 Shutting down gracefully...")
        
        # 🟢 Send Bot Stopped Log
        if hasattr(self, 'logger'):
            try:
                await self.logger.bot_stopped()
            except Exception as e:
                print(f"⚠️ Bot stop log error: {e}")
        
        # Stop web server
        if self.web_app:
            try:
                await self.web_app.cleanup()
                print("✅ Web server stopped")
            except Exception as e:
                print(f"⚠️ Web server stop error: {e}")
        
        # Clean temp files
        try:
            import shutil
            if os.path.exists("thumb_watermark"):
                shutil.rmtree("thumb_watermark")
                print("✅ Cleaned thumbnail temp files")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")
        
        # Stop bot
        try:
            await super().stop()
            print("✅ Bot stopped successfully")
        except Exception as e:
            print(f"⚠️ Bot stop error: {e}")
        
        sys.exit(0)
        
    async def stop(self, *args):
        await self.shutdown()

# ==================== RUN BOT ====================

if __name__ == "__main__":
    try:
        print("🚀 Starting Rkn-AutoCaptionBot...")
        print("📌 Press Ctrl+C to stop")
        Rkn_AutoCaptionBot().run()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

# Rkn Developer 
# Don't Remove Credit 😔
