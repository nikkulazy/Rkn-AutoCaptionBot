# logger.py - Logger Utility
# (c) @RknDeveloperr

import asyncio
from datetime import datetime
from pyrogram import enums
from pyrogram.errors import FloodWait, ChatWriteForbidden, PeerIdInvalid

class Logger:
    def __init__(self, bot):
        self.bot = bot
        self.log_channel = None
        self.enabled = False
        
        try:
            from config import Rkn_Bots
            self.log_channel = str(Rkn_Bots.LOG_CHANNEL) if Rkn_Bots.LOG_CHANNEL else None
            self.enabled = bool(self.log_channel)
            print(f"📋 Logger initialized with channel: {self.log_channel}")
        except Exception as e:
            print(f"⚠️ Logger init error: {e}")
        
        self.bot_start_time = datetime.now()
    
    async def send_log(self, message: str):
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
    
    async def forward_file_to_log(self, message, channel_id: int, channel_title: str = None, file_name: str = None):
        if not self.enabled or not self.log_channel:
            print(f"[LOG] File forward disabled - no log channel")
            return
        
        try:
            chat_id = int(self.log_channel)
            title_str = f"{channel_title}" if channel_title else f"Channel {channel_id}"
            
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
            
            caption = f"📁 **New File Received in Channel**\n\n"
            caption += f"• **Channel:** {title_str}\n"
            caption += f"• **Channel ID:** `{channel_id}`\n"
            caption += f"• **File Type:** {file_type}\n"
            caption += f"• **File Name:** `{file_name or 'Unknown'}`\n"
            caption += f"• **Message ID:** `{message.id}`\n"
            caption += f"• **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            if message.caption:
                caption += f"\n\n📝 **Original Caption:**\n`{message.caption[:200]}{'...' if len(message.caption) > 200 else ''}`"
            
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
    
    async def bot_started(self):
        try:
            me = await self.bot.get_me()
            msg = f"🚀 Bot Started Successfully!\n📌 Bot Username: @{me.username}"
            await self.send_log(msg)
            print("✅ Bot started log sent successfully!")
        except Exception as e:
            print(f"❌ Error sending bot started log: {e}")
    
    async def bot_stopped(self):
        uptime = str(datetime.now() - self.bot_start_time).split('.')[0]
        msg = f"🛑 **Bot Stopped**\n\n• **Uptime:** {uptime}\n• **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        await self.send_log(msg)
    
    async def user_start(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        username_str = f"@{username}" if username else "No username"
        full_name = f"{first_name or ''} {last_name or ''}".strip() or "Unknown"
        msg = f"👤 **New User Started Bot**\n\n• **User ID:** `{user_id}`\n• **Name:** {full_name}\n• **Username:** {username_str}\n• **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        await self.send_log(msg)
    
    async def channel_setup(self, user_id: int, channel_id: int, channel_title: str = None):
        title_str = f" ({channel_title})" if channel_title else ""
        msg = f"✅ **Channel Setup**\n\n• **User ID:** `{user_id}`\n• **Channel ID:** `{channel_id}`{title_str}\n• **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        await self.send_log(msg)
    
    async def caption_set(self, user_id: int, channel_id: int, caption: str):
        caption_preview = caption[:150].replace('\n', ' ')
        if len(caption) > 150:
            caption_preview += "..."
        msg = f"📝 **Caption Set**\n\n• **User ID:** `{user_id}`\n• **Channel ID:** `{channel_id}`\n• **Caption:** `{caption_preview}`\n• **Length:** `{len(caption)}` characters\n• **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        await self.send_log(msg)
    
    async def caption_deleted(self, user_id: int, channel_id: int):
        msg = f"❌ **Caption Deleted**\n\n• **User ID:** `{user_id}`\n• **Channel ID:** `{channel_id}`\n• **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        await self.send_log(msg)
    
    async def buttons_set(self, user_id: int, channel_id: int, button_count: int):
        msg = f"🔘 **Buttons Set**\n\n• **User ID:** `{user_id}`\n• **Channel ID:** `{channel_id}`\n• **Buttons Count:** `{button_count}`\n• **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        await self.send_log(msg)
    
    async def buttons_removed(self, user_id: int, channel_id: int):
        msg = f"🗑️ **Buttons Removed**\n\n• **User ID:** `{user_id}`\n• **Channel ID:** `{channel_id}`\n• **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        await self.send_log(msg)
    
    async def broadcast_started(self, admin_id: int, total_users: int):
        msg = f"📢 **Broadcast Started**\n\n• **Admin ID:** `{admin_id}`\n• **Total Users:** `{total_users}`\n• **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        await self.send_log(msg)
    
    async def broadcast_completed(self, admin_id: int, success: int, failed: int, blocked: int, deactivated: int, total: int):
        msg = f"📢 **Broadcast Completed**\n\n• **Admin ID:** `{admin_id}`\n• **Total:** `{total}`\n• **Success:** `{success}` ✅\n• **Failed:** `{failed}` ❌\n• **Blocked Users:** `{blocked}` 🚫\n• **Deleted Accounts:** `{deactivated}` 🗑️\n• **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        await self.send_log(msg)
