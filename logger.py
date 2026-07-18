# (c) @RknDeveloperr
# Logger Utility for Auto Caption Bot

import asyncio
from datetime import datetime
from pyrogram.errors import FloodWait, ChatWriteForbidden, PeerIdInvalid

class Logger:
    def __init__(self, bot):
        self.bot = bot
        self.log_channel = None
        self.enabled = False
        
        # Get log channel from config
        try:
            from config import Rkn_Bots
            self.log_channel = Rkn_Bots.LOG_CHANNEL
            self.enabled = bool(self.log_channel)
        except:
            pass
        
        self.bot_start_time = datetime.now()
    
    async def send_log(self, message: str, parse_mode: str = "html"):
        """Send log message to log channel"""
        if not self.enabled or not self.log_channel:
            print(f"[LOG] {message}")
            return
        
        try:
            formatted_msg = f"📋 **LOG | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**\n\n{message}"
            await self.bot.send_message(
                chat_id=self.log_channel,
                text=formatted_msg,
                parse_mode=parse_mode,
                disable_web_page_preview=True
            )
            print(f"✅ Log sent to channel: {self.log_channel}")
        except ChatWriteForbidden:
            print(f"❌ Bot is not admin in log channel {self.log_channel}")
            self.enabled = False
        except PeerIdInvalid:
            print(f"❌ Invalid log channel ID: {self.log_channel}")
            self.enabled = False
        except FloodWait as e:
            print(f"⏳ FloodWait: {e.x} seconds")
            await asyncio.sleep(e.x)
            await self.send_log(message, parse_mode)
        except Exception as e:
            print(f"❌ Failed to send log: {e}")
    
    async def bot_started(self):
        """🚀 Send bot started log"""
        try:
            me = await self.bot.get_me()
            from config import Rkn_Bots
            
            msg = (
                f"🚀 **Bot Started Successfully!**\n\n"
                f"• **Bot Name:** {me.first_name}\n"
                f"• **Bot Username:** @{me.username}\n"
                f"• **Bot ID:** `{me.id}`\n"
                f"• **API ID:** `{Rkn_Bots.API_ID}`\n"
                f"• **Force Sub:** {Rkn_Bots.FORCE_SUB or 'Disabled'}\n"
                f"• **Log Channel:** {Rkn_Bots.LOG_CHANNEL or 'Disabled'}\n"
                f"• **Admins:** `{Rkn_Bots.ADMIN}`\n"
                f"• **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            await self.send_log(msg)
            print("✅ Bot started log sent successfully!")
        except Exception as e:
            print(f"❌ Error sending bot started log: {e}")
    
    async def bot_stopped(self):
        """🛑 Send bot stopped log"""
        uptime = str(datetime.now() - self.bot_start_time).split('.')[0]
        msg = (
            f"🛑 **Bot Stopped**\n\n"
            f"• **Uptime:** {uptime}\n"
            f"• **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await self.send_log(msg)
    
    async def user_start(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """👤 Log user start"""
        username_str = f"@{username}" if username else "No username"
        full_name = f"{first_name or ''} {last_name or ''}".strip() or "Unknown"
        
        msg = (
            f"👤 **New User Started Bot**\n\n"
            f"• **User ID:** `{user_id}`\n"
            f"• **Name:** {full_name}\n"
            f"• **Username:** {username_str}\n"
            f"• **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await self.send_log(msg)
    
    async def channel_setup(self, user_id: int, channel_id: int, channel_title: str = None):
        """✅ Log channel setup"""
        title_str = f" ({channel_title})" if channel_title else ""
        msg = (
            f"✅ **Channel Setup**\n\n"
            f"• **User ID:** `{user_id}`\n"
            f"• **Channel ID:** `{channel_id}`{title_str}\n"
            f"• **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await self.send_log(msg)
    
    async def caption_set(self, user_id: int, channel_id: int, caption: str):
        """📝 Log caption set"""
        caption_preview = caption[:150].replace('\n', ' ')
        if len(caption) > 150:
            caption_preview += "..."
        
        msg = (
            f"📝 **Caption Set**\n\n"
            f"• **User ID:** `{user_id}`\n"
            f"• **Channel ID:** `{channel_id}`\n"
            f"• **Caption:** `{caption_preview}`\n"
            f"• **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await self.send_log(msg)
    
    async def buttons_set(self, user_id: int, channel_id: int, button_count: int):
        """🔘 Log buttons set"""
        msg = (
            f"🔘 **Buttons Set**\n\n"
            f"• **User ID:** `{user_id}`\n"
            f"• **Channel ID:** `{channel_id}`\n"
            f"• **Buttons Count:** `{button_count}`\n"
            f"• **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await self.send_log(msg)
