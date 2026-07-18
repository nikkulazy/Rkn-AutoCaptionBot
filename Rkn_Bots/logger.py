# (c) @RknDeveloperr
# Logger Utility for Auto Caption Bot

import asyncio
from datetime import datetime
from pyrogram import enums
from pyrogram.errors import FloodWait, ChatWriteForbidden, PeerIdInvalid

class Logger:
    def __init__(self, bot):
        self.bot = bot
        self.log_channel = None
        self.enabled = False
        
        # Get log channel from config
        try:
            from config import Rkn_Bots
            self.log_channel = str(Rkn_Bots.LOG_CHANNEL) if Rkn_Bots.LOG_CHANNEL else None
            self.enabled = bool(self.log_channel)
            print(f"📋 Logger initialized with channel: {self.log_channel}")
        except Exception as e:
            print(f"⚠️ Logger init error: {e}")
        
        self.bot_start_time = datetime.now()
    
    async def send_log(self, message: str):
        """Send log message to log channel"""
        if not self.enabled or not self.log_channel:
            print(f"[LOG] {message}")
            return
        
        try:
            chat_id = int(self.log_channel)
            formatted_msg = f"📋 **LOG | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**\n\n{message}"
            await self.bot.send_message(
                chat_id=chat_id,
                text=formatted_msg,
                parse_mode=enums.ParseMode.HTML,
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
            await self.send_log(message)
        except Exception as e:
            print(f"❌ Failed to send log: {e}")
    
    # ==================== 🆕 FILE FORWARD TO LOG CHANNEL ====================
    
    async def forward_file_to_log(self, message, channel_id: int, channel_title: str = None, file_name: str = None):
        """Forward file from any channel to log channel"""
        if not self.enabled or not self.log_channel:
            print(f"[LOG] File forward disabled - no log channel")
            return
        
        try:
            chat_id = int(self.log_channel)
            
            # ✅ Channel Title
            title_str = f"{channel_title}" if channel_title else f"Channel {channel_id}"
            
            # ✅ File Type Detect
            file_type = "📄 Document"
            if message.video:
                file_type = "🎬 Video"
            elif message.audio:
                file_type = "🎵 Audio"
            elif message.document:
                file_type = "📄 Document"
            elif message.photo:
                file_type = "🖼️ Photo"
            elif message.voice:
                file_type = "🎤 Voice"
            
            # ✅ Caption banayein
            caption = f"📁 **New File Received in Channel**\n\n"
            caption += f"• **Channel:** {title_str}\n"
            caption += f"• **Channel ID:** `{channel_id}`\n"
            caption += f"• **File Type:** {file_type}\n"
            caption += f"• **File Name:** `{file_name or 'Unknown'}`\n"
            caption += f"• **Message ID:** `{message.id}`\n"
            caption += f"• **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # ✅ Check if message has caption
            if message.caption:
                caption += f"\n\n📝 **Original Caption:**\n`{message.caption[:200]}{'...' if len(message.caption) > 200 else ''}`"
            
            # ✅ File ko forward karein log channel me
            await message.copy(
                chat_id=chat_id,
                caption=caption,
                parse_mode=enums.ParseMode.HTML
            )
            print(f"✅ File forwarded to log channel: {self.log_channel}")
            
        except ChatWriteForbidden:
            print(f"❌ Bot is not admin in log channel {self.log_channel}")
            self.enabled = False
        except FloodWait as e:
            print(f"⏳ FloodWait: {e.x} seconds")
            await asyncio.sleep(e.x)
            await self.forward_file_to_log(message, channel_id, channel_title, file_name)
        except Exception as e:
            print(f"❌ Failed to forward file: {e}")
    
    # ==================== BOT LOGS ====================
    
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
                f"• **Log Channel:** `{Rkn_Bots.LOG_CHANNEL}`\n"
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
    
    async def channel_removed(self, user_id: int, channel_id: int):
        """🗑️ Log channel removed"""
        msg = (
            f"🗑️ **Channel Removed**\n\n"
            f"• **User ID:** `{user_id}`\n"
            f"• **Channel ID:** `{channel_id}`\n"
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
            f"• **Length:** `{len(caption)}` characters\n"
            f"• **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await self.send_log(msg)
    
    async def caption_deleted(self, user_id: int, channel_id: int):
        """❌ Log caption deleted"""
        msg = (
            f"❌ **Caption Deleted**\n\n"
            f"• **User ID:** `{user_id}`\n"
            f"• **Channel ID:** `{channel_id}`\n"
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
    
    async def buttons_removed(self, user_id: int, channel_id: int):
        """🗑️ Log buttons removed"""
        msg = (
            f"🗑️ **Buttons Removed**\n\n"
            f"• **User ID:** `{user_id}`\n"
            f"• **Channel ID:** `{channel_id}`\n"
            f"• **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await self.send_log(msg)
    
    async def caption_edited(self, channel_id: int, message_id: int, file_name: str):
        """✏️ Log caption auto-edited"""
        msg = (
            f"✏️ **Caption Auto-Edited**\n\n"
            f"• **Channel ID:** `{channel_id}`\n"
            f"• **Message ID:** `{message_id}`\n"
            f"• **File Name:** `{file_name}`\n"
            f"• **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await self.send_log(msg)
    
    async def broadcast_started(self, admin_id: int, total_users: int):
        """📢 Log broadcast started"""
        msg = (
            f"📢 **Broadcast Started**\n\n"
            f"• **Admin ID:** `{admin_id}`\n"
            f"• **Total Users:** `{total_users}`\n"
            f"• **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await self.send_log(msg)
    
    async def broadcast_completed(self, admin_id: int, success: int, failed: int, blocked: int, deactivated: int, total: int):
        """📢 Log broadcast completed"""
        msg = (
            f"📢 **Broadcast Completed**\n\n"
            f"• **Admin ID:** `{admin_id}`\n"
            f"• **Total:** `{total}`\n"
            f"• **Success:** `{success}` ✅\n"
            f"• **Failed:** `{failed}` ❌\n"
            f"• **Blocked Users:** `{blocked}` 🚫\n"
            f"• **Deleted Accounts:** `{deactivated}` 🗑️\n"
            f"• **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await self.send_log(msg)
    
    async def admin_action(self, admin_id: int, action: str, details: str = ""):
        """🔧 Log admin action"""
        msg = (
            f"🔧 **Admin Action**\n\n"
            f"• **Admin ID:** `{admin_id}`\n"
            f"• **Action:** {action}\n"
            f"• **Details:** {details}\n"
            f"• **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await self.send_log(msg)
    
    async def system_error(self, error: str, context: str = ""):
        """⚠️ Log system error"""
        msg = (
            f"⚠️ **System Error**\n\n"
            f"• **Error:** `{error}`\n"
            f"• **Context:** {context}\n"
            f"• **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await self.send_log(msg)
