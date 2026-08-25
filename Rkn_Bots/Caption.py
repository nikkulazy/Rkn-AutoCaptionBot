from pyrogram import Client, filters, errors, types, enums
from config import Rkn_Bots
import asyncio, re, time, sys, os
from .database import total_user, getid, delete, insert, chnl_ids, users
from .database import addCap, updateCap, updateButtons, deleteButtons, getChannelData
from .database import addCapByUser, updateCapByUser, updateButtonsByUser, deleteButtonsByUser, getChannelDataByUser
from .database import resetChannelData, resetUserData
from .database import getWatermarkSettings, updateWatermarkText, updateWatermarkStatus, removeWatermark
from pyrogram.errors import FloodWait

# ==================== ADD LOGGER IMPORT ====================
from .logger import Logger

print("🔄 Loading Caption.py...")

# ==================== WATERMARK IMPORT ====================
from .thumbnail_watermark import ThumbnailWatermark, init_thumb_watermark

# Global watermark instance
thumb_watermark = None

async def get_watermark_instance(bot):
    global thumb_watermark
    if thumb_watermark is None:
        thumb_watermark = await init_thumb_watermark(bot)
    return thumb_watermark

# ==================== MAIN MENU BUTTONS ====================

async def main_menu_buttons():
    """Main menu with buttons"""
    buttons = types.InlineKeyboardMarkup([
        [
            types.InlineKeyboardButton("📝 Set Caption", callback_data="set_caption"),
            types.InlineKeyboardButton("📎 Add Button", callback_data="add_button")
        ],
        [
            types.InlineKeyboardButton("📊 Status", callback_data="status")
        ],
        [
            types.InlineKeyboardButton("📢 Main Channel", url="https://t.me/wolverine273"),
            types.InlineKeyboardButton("💬 Help Group", url="https://t.me/WOLVERIN_P")
        ]
    ])
    return buttons

async def back_button_only():
    """Only back button"""
    buttons = types.InlineKeyboardMarkup([
        [types.InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ])
    return buttons

# ==================== GET HOME MENU CAPTION ====================

async def get_home_caption(user_id, first_name=None):
    """Get home menu caption with welcome message and user name"""
    
    if first_name:
        welcome = f"**👋 Welcome {first_name}!**\n\n"
    else:
        welcome = f"**👋 Welcome!**\n\n"
    
    chkData = await getChannelDataByUser(user_id)
    
    if chkData:
        channel_status = "✅ **Channel is Connected!**\n\nYou can manage your settings using the buttons below."
    else:
        channel_status = "❌ **No Channel Connected!**\n\n📌 **How to connect:**\n1. Add me as admin in your channel\n2. Send `/set_caption` or `/set_buttons` in your channel\n3. I'll auto-detect your channel!"
    
    caption = f"{welcome}"
    caption += f"**This is powerful Auto caption bot fully customised and easy to use.**\n\n"
    caption += f"<i>Select an option below to manage your settings:</i>"
    
    return caption

# ==================== CHECK IF BOT IS ADMIN IN CHANNEL ====================

async def check_bot_admin(bot, channel_id):
    """Check if bot is admin in the channel"""
    try:
        chat_member = await bot.get_chat_member(channel_id, (await bot.get_me()).id)
        if chat_member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            return True
        return False
    except Exception as e:
        print(f"❌ Bot admin check failed: {e}")
        return False

# ==================== START COMMAND ====================

@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(bot, message):
    print("✅ /start command triggered!")
    user_id = int(message.from_user.id)
    first_name = message.from_user.first_name or "User"
    
    user_exists = await users.find_one({"_id": user_id})
    
    if not user_exists:
        await insert(user_id)
        try:
            logger = Logger(bot)
            await logger.user_start(
                user_id=user_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )
        except Exception as e:
            print(f"⚠️ Log error (non-critical): {e}")
    else:
        print(f"👤 Existing user: {user_id}")
    
    buttons = await main_menu_buttons()
    caption = await get_home_caption(user_id, first_name)
    
    await message.reply_photo(
        photo=Rkn_Bots.RKN_PIC,
        caption=caption,
        reply_markup=buttons
    )

# ==================== CALLBACK QUERY HANDLER ====================

@Client.on_callback_query()
async def callback_handler(bot, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data
    first_name = callback_query.from_user.first_name or "User"
    
    try:
        logger = Logger(bot)
    except Exception as e:
        print(f"⚠️ Logger error: {e}")
        logger = None
    
    if not callback_query.message:
        await callback_query.answer("Message not found!")
        return
    
    try:
        await callback_query.message.delete()
    except:
        pass
    
    if data == "back_to_menu":
        buttons = await main_menu_buttons()
        caption = await get_home_caption(user_id, first_name)
        
        try:
            await callback_query.message.reply_photo(
                photo=Rkn_Bots.RKN_PIC,
                caption=caption,
                reply_markup=buttons
            )
        except Exception as e:
            await callback_query.message.reply_text(
                caption,
                reply_markup=buttons
            )
        await callback_query.answer()
        return
    
    elif data == "set_caption":
        buttons = await back_button_only()
        await callback_query.message.reply_text(
            f"**📝 How to Set Caption**\n\n"
            f"1️⃣ Add me as **admin** in your channel\n"
            f"2️⃣ Go to your **channel**\n"
            f"3️⃣ Send this command:\n\n"
            f"`/set_caption Your caption here {{file_name}}`\n\n"
            f"**📌 Example:**\n"
            f"`/set_caption 📁 File: {{file_name}}\nJoin @wolverine273`\n\n"
            f"**📌 Variables:**\n"
            f"• `{{file_name}}` - Original file name\n\n"
            f"⚠️ This command only works in **channel**, not in private chat!",
            reply_markup=buttons
        )
        await callback_query.answer()
    
    elif data == "add_button":
        buttons = await back_button_only()
        await callback_query.message.reply_text(
            f"**📎 How to Add Buttons**\n\n"
            f"1️⃣ Add me as **admin** in your channel\n"
            f"2️⃣ Go to your **channel**\n"
            f"3️⃣ Send this command:\n\n"
            f"`/set_buttons [Text]:[URL] | [Text]:[URL]`\n\n"
            f"**📌 Example 1 (Single):**\n"
            f"`/set_buttons 📢 Join:https://t.me/wolverine273`\n\n"
            f"**📌 Example 2 (Multiple):**\n"
            f"`/set_buttons 📢 Channel:https://t.me/wolverine273 | 💬 Group:https://t.me/WOLVERIN_P`\n\n"
            f"⚠️ This command only works in **channel**, not in private chat!",
            reply_markup=buttons
        )
        await callback_query.answer()
    
    elif data == "status":
        chkData = await getChannelDataByUser(user_id)
        if not chkData:
            await callback_query.message.reply_text(
                f"❌ **No settings found!**\n\n"
                f"First set up your channel."
            )
        else:
            chnl_id = chkData.get("chnl_id")
            channel_data = await getChannelData(chnl_id)
            caption = channel_data.get("caption", "Not set") if channel_data else "Not set"
            buttons_data = channel_data.get("buttons", []) if channel_data else []
            btn_count = len(buttons_data)
            
            # Get watermark status
            wm_settings = await getWatermarkSettings(user_id)
            wm_status = "✅ Enabled" if wm_settings.get("enabled") else "❌ Disabled"
            wm_text = wm_settings.get("text") or "Not set"
            
            await callback_query.message.reply_text(
                f"**📊 Your Settings**\n\n"
                f"🔹 **Channel ID:** `{chnl_id}`\n\n"
                f"🔹 **Caption:**\n`{caption}`\n\n"
                f"🔹 **Buttons:** ({btn_count})\n"
                f"{'✅ Set' if btn_count > 0 else '❌ Not set'}\n\n"
                f"🔹 **Watermark:** {wm_status}\n"
                f"📝 **Text:** `{wm_text}`\n"
                f"📌 **Applied on:** Video Thumbnail Only"
            )
        await callback_query.answer()

# ==================== CHECK CHANNEL OWNER/ADMIN ====================

async def get_channel_owner_or_admin(bot, channel_id):
    """Get the owner or admin of a channel"""
    try:
        admins = await bot.get_chat_members(channel_id, filter=enums.ChatMembersFilter.ADMINISTRATORS)
        async for admin in admins:
            if admin.user and not admin.user.is_bot:
                return admin.user.id
    except Exception as e:
        print(f"⚠️ Could not get channel admins: {e}")
    
    return None

# ==================== AUTO SET CHANNEL WITH OWNER DETECTION ====================

async def auto_set_channel(bot, message):
    """Auto set channel when user sends command in channel - detects channel owner/admin"""
    channel_id = message.chat.id
    
    is_admin = await check_bot_admin(bot, channel_id)
    
    if not is_admin:
        await message.reply_text(
            f"❌ **I'm not admin in this channel!**\n\n"
            f"Please add me as admin in this channel first.\n\n"
            f"**How to add:**\n"
            f"1. Open channel settings\n"
            f"2. Go to Administrators\n"
            f"3. Add this bot as admin"
        )
        return None
    
    user_id = None
    
    try:
        async for admin in bot.get_chat_members(channel_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            if admin.user and not admin.user.is_bot:
                user_id = admin.user.id
                print(f"👤 Found admin: {user_id}")
                break
    except Exception as e:
        print(f"⚠️ Could not get admins: {e}")
    
    if not user_id and message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
        print(f"👤 Found from reply: {user_id}")
    
    if not user_id and message.from_user:
        user_id = message.from_user.id
        print(f"👤 Found from sender: {user_id}")
    
    if not user_id:
        user_id = channel_id
        print(f"⚠️ Using channel ID as user ID: {user_id}")
    
    print(f"👤 Final User ID: {user_id}")
    print(f"📢 Channel ID: {channel_id}")
    
    chkData = await getChannelDataByUser(user_id)
    
    if chkData and chkData.get("chnl_id") == channel_id:
        print(f"✅ Channel already set for user {user_id}")
        return channel_id
    
    if chkData:
        await chnl_ids.delete_many({"user_id": user_id})
        await chnl_ids.delete_many({"chnl_id": chkData.get("chnl_id")})
        print(f"🗑️ Deleted old data for user: {user_id}")
    
    try:
        await addCapByUser(user_id, channel_id, Rkn_Bots.DEF_CAP)
        await addCap(channel_id, Rkn_Bots.DEF_CAP)
        print(f"✅ Saved channel {channel_id} for user {user_id}")
    except Exception as e:
        print(f"❌ Database save error: {e}")
        await message.reply_text(f"❌ Database error: {e}")
        return None
    
    channel_title = None
    try:
        chat = await bot.get_chat(channel_id)
        channel_title = chat.title
    except:
        pass
    
    try:
        logger = Logger(bot)
        await logger.channel_setup(user_id, channel_id, channel_title)
    except Exception as e:
        print(f"⚠️ Log error: {e}")
    
    print(f"✅ Channel {channel_id} auto-set for user {user_id}")
    
    await message.reply_text(
        f"✅ **Channel Set Successfully!**\n\n"
        f"**Channel ID:** `{channel_id}`\n"
        f"**Channel Name:** {channel_title or 'Unknown'}\n"
        f"**User ID:** `{user_id}`\n\n"
        f"Now you can use:\n"
        f"• `/set_caption` - Set your caption\n"
        f"• `/set_buttons` - Set your buttons\n"
        f"• `/set_watermark` - Set watermark text"
    )
    
    return channel_id

# ==================== SET CAPTION COMMAND ====================

@Client.on_message(filters.command("set_caption") & (filters.channel | filters.private))
async def setCaption(bot, message):
    print("✅ /set_caption command triggered!")
    
    if message.chat.type == enums.ChatType.PRIVATE:
        buttons = await back_button_only()
        await message.reply_text(
            f"❌ **Please use this command in your channel!**\n\n"
            f"📌 **How to use:**\n"
            f"1. Add me as admin in your channel\n"
            f"2. Go to your channel\n"
            f"3. Send: `/set_caption Your caption here {{file_name}}`\n\n"
            f"**Example:**\n"
            f"`/set_caption 📁 File: {{file_name}}\nJoin @wolverine273`",
            reply_markup=buttons
        )
        return
    
    try:
        await message.delete()
    except:
        pass
    
    channel_id = await auto_set_channel(bot, message)
    
    if channel_id is None:
        return
    
    user_id = None
    
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
    
    if not user_id:
        owner_id = await get_channel_owner_or_admin(bot, channel_id)
        if owner_id:
            user_id = owner_id
    
    if not user_id:
        user_id = channel_id
    
    print(f"👤 User ID for caption: {user_id}")
    
    if len(message.command) < 2:
        await message.reply_text(
            f"❌ **Please provide caption!**\n\n"
            f"**Usage:** `/set_caption Your caption here {file_name}`\n\n"
            f"**Example:** `/set_caption 📁 File: {file_name}\nJoin @wolverine273`\n\n"
            f"**{file_name}** - Shows original file name"
        )
        return
    
    caption = message.text.split(" ", 1)[1]
    
    await updateCapByUser(user_id, caption)
    await updateCap(channel_id, caption)
    
    try:
        logger = Logger(bot)
        await logger.caption_set(user_id, channel_id, caption)
    except Exception as e:
        print(f"⚠️ Log error: {e}")
    
    await message.reply_text(
        f"✅ **Caption Updated Successfully!**\n\n"
        f"**Channel ID:** `{channel_id}`\n\n"
        f"**Your New Caption:**\n`{caption}`"
    )

# ==================== SET BUTTONS COMMAND ====================

@Client.on_message(filters.command("set_buttons") & (filters.channel | filters.private))
async def setButtons(bot, message):
    print("✅ /set_buttons command triggered!")
    
    if message.chat.type == enums.ChatType.PRIVATE:
        buttons = await back_button_only()
        await message.reply_text(
            f"❌ **Please use this command in your channel!**\n\n"
            f"📌 **How to use:**\n"
            f"1. Add me as admin in your channel\n"
            f"2. Go to your channel\n"
            f"3. Send: `/set_buttons [Text]:[URL] | [Text]:[URL]`\n\n"
            f"**Example:**\n"
            f"`/set_buttons 📢 Join:https://t.me/wolverine273 | 💬 Group:https://t.me/WOLVERIN_P`",
            reply_markup=buttons
        )
        return
    
    try:
        await message.delete()
    except:
        pass
    
    channel_id = await auto_set_channel(bot, message)
    
    if channel_id is None:
        return
    
    user_id = None
    
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
    
    if not user_id:
        owner_id = await get_channel_owner_or_admin(bot, channel_id)
        if owner_id:
            user_id = owner_id
    
    if not user_id:
        user_id = channel_id
    
    print(f"👤 User ID for buttons: {user_id}")
    
    if len(message.command) < 2:
        await message.reply_text(
            f"❌ **Please provide buttons!**\n\n"
            f"**Usage:** `/set_buttons [Text]:[URL] | [Text]:[URL]`\n"
            f"**Example:** `/set_buttons 📢 Join:https://t.me/wolverine273`\n\n"
            f"**Multiple Buttons:**\n"
            f"`/set_buttons 📢 Channel:https://t.me/wolverine273 | 💬 Group:https://t.me/WOLVERIN_P`"
        )
        return
    
    buttons_text = message.text.split(" ", 1)[1]
    if not buttons_text:
        return await message.reply_text("❌ Please provide buttons data!")
    
    buttons_data = []
    for btn in buttons_text.split("|"):
        btn = btn.strip()
        if ":" in btn:
            parts = btn.split(":", 1)
            if len(parts) == 2:
                text = parts[0].strip()
                url = parts[1].strip()
                if text and url:
                    if url.startswith(("https://", "http://", "t.me/")):
                        buttons_data.append([types.InlineKeyboardButton(text, url=url)])
                    else:
                        return await message.reply_text(f"❌ Invalid URL: `{url}`")
    
    if not buttons_data:
        return await message.reply_text(
            f"❌ **No valid buttons found!**\n\n"
            f"**Format:** `[Text]:[URL]` separated by ` | `\n"
            f"**Example:** `/set_buttons 📢 Join:https://t.me/wolverine273 | 💬 Group:https://t.me/WOLVERIN_P`"
        )
    
    print(f"📌 Setting buttons for Channel: {channel_id}")
    print(f"📌 Buttons: {len(buttons_data)} button(s)")
    
    await updateButtons(channel_id, buttons_data)
    await updateButtonsByUser(user_id, buttons_data)
    
    try:
        logger = Logger(bot)
        await logger.buttons_set(user_id, channel_id, len(buttons_data))
    except Exception as e:
        print(f"⚠️ Log error: {e}")
    
    verify_data = await getChannelData(channel_id)
    saved_buttons = verify_data.get("buttons", [])
    print(f"✅ Verified: {len(saved_buttons)} buttons saved for channel {channel_id}")
    
    preview = "\n".join([f"• {btn[0].text} → {btn[0].url}" for btn in buttons_data])
    
    await message.reply_text(
        f"✅ **Buttons Set Successfully!**\n\n"
        f"📌 **Channel ID:** `{channel_id}`\n"
        f"🔢 **Buttons Saved:** `{len(saved_buttons)}` button(s)\n\n"
        f"**Your Buttons:**\n{preview}\n\n"
        f"📌 Now post a file in this channel to see buttons!",
        reply_markup=types.InlineKeyboardMarkup(buttons_data)
    )

# ==================== WATERMARK COMMANDS ====================

@Client.on_message(filters.command("set_watermark") & filters.private)
async def set_watermark_cmd(bot, message):
    """Set watermark text"""
    user_id = message.from_user.id
    
    chkData = await getChannelDataByUser(user_id)
    if not chkData:
        buttons = await back_button_only()
        await message.reply_text(
            f"❌ **No channel connected!**\n\n"
            f"First set up your channel:\n"
            f"1. Add me as admin in your channel\n"
            f"2. Send `/set_caption` in your channel",
            reply_markup=buttons
        )
        return
    
    if len(message.command) < 2:
        return await message.reply_text(
            f"**🖼️ Set Watermark**\n\n"
            f"**Position:** Center + Thoda Down\n"
            f"**Text Color:** White\n"
            f"**Background:** Black (80% opacity)\n"
            f"**Applied on:** Video Thumbnail Only\n\n"
            f"**Usage:** `/set_watermark Your Text Here`\n\n"
            f"**Example:** `/set_watermark @wolverine273`\n\n"
            f"**Commands:**\n"
            f"• `/set_watermark` - Set watermark text\n"
            f"• `/remove_watermark` - Remove watermark\n"
            f"• `/watermark_status` - Check watermark status\n\n"
            f"⚠️ Watermark will be added to **video thumbnails** only."
        )
    
    text = message.text.split(" ", 1)[1]
    
    await updateWatermarkText(user_id, text)
    await updateWatermarkStatus(user_id, True)
    
    await message.reply_text(
        f"✅ **Watermark Text Saved & Enabled!**\n\n"
        f"📝 **Text:** `{text}`\n\n"
        f"**Position:** Center + Thoda Down\n"
        f"**Text Color:** White\n"
        f"**Background:** Black (80% opacity)\n"
        f"**Applied on:** Video Thumbnail Only\n\n"
        f"Now watermarks will be added to **video thumbnails**.\n\n"
        f"To remove: `/remove_watermark`"
    )

@Client.on_message(filters.command("remove_watermark") & filters.private)
async def remove_watermark_cmd(bot, message):
    """Remove watermark"""
    user_id = message.from_user.id
    
    chkData = await getChannelDataByUser(user_id)
    if not chkData:
        buttons = await back_button_only()
        await message.reply_text(
            f"❌ **No channel connected!**\n\n"
            f"First set up your channel.",
            reply_markup=buttons
        )
        return
    
    # Remove watermark from database
    await removeWatermark(user_id)
    
    await message.reply_text(
        f"✅ **Watermark Removed Successfully!**\n\n"
        f"Watermark has been removed.\n"
        f"No more watermarks will be added to video thumbnails.\n\n"
        f"To set again: `/set_watermark Your Text`"
    )

@Client.on_message(filters.command("watermark_status") & filters.private)
async def watermark_status_cmd(bot, message):
    """Check watermark status"""
    user_id = message.from_user.id
    
    settings = await getWatermarkSettings(user_id)
    
    status = "✅ Enabled" if settings.get("enabled") else "❌ Disabled / Not Set"
    text = settings.get("text") or "Not set"
    
    await message.reply_text(
        f"**🖼️ Watermark Status**\n\n"
        f"• **Status:** {status}\n"
        f"• **Text:** `{text}`\n\n"
        f"**Position:** Center + Thoda Down\n"
        f"**Text Color:** White\n"
        f"**Background:** Black (80% opacity)\n"
        f"**Applied on:** Video Thumbnail Only\n\n"
        f"**Commands:**\n"
        f"• `/set_watermark` - Set watermark\n"
        f"• `/remove_watermark` - Remove watermark"
    )

# ==================== DELETE CAPTION COMMAND ====================

@Client.on_message(filters.command(["delcaption", "del_caption", "delete_caption"]) & (filters.channel | filters.private))
async def delCaption(bot, message):
    print("✅ /delcaption command triggered!")
    
    if message.chat.type == enums.ChatType.PRIVATE:
        buttons = await back_button_only()
        await message.reply_text(
            f"❌ **Please use this command in your channel!**\n\n"
            f"Go to your channel and send `/delcaption`",
            reply_markup=buttons
        )
        return
    
    try:
        await message.delete()
    except:
        pass
    
    channel_id = await auto_set_channel(bot, message)
    
    if channel_id is None:
        return
    
    user_id = None
    
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
    
    if not user_id:
        owner_id = await get_channel_owner_or_admin(bot, channel_id)
        if owner_id:
            user_id = owner_id
    
    if not user_id:
        user_id = channel_id
    
    chkData = await getChannelDataByUser(user_id)
    if not chkData:
        return await message.reply_text("❌ No data found for your channel!")
    
    await updateCapByUser(user_id, Rkn_Bots.DEF_CAP)
    await updateCap(channel_id, Rkn_Bots.DEF_CAP)
    
    try:
        logger = Logger(bot)
        await logger.caption_deleted(user_id, channel_id)
    except Exception as e:
        print(f"⚠️ Log error: {e}")
    
    await message.reply_text(
        f"✅ **Caption Deleted Successfully!**\n\n"
        f"**Channel ID:** `{channel_id}`\n"
        f"Now I will use default caption.\n\n"
        f"**Default Caption:**\n`{Rkn_Bots.DEF_CAP}`"
    )

# ==================== REMOVE BUTTONS COMMAND ====================

@Client.on_message(filters.command("remove_buttons") & (filters.channel | filters.private))
async def removeButtons(bot, message):
    print("✅ /remove_buttons command triggered!")
    
    if message.chat.type == enums.ChatType.PRIVATE:
        buttons = await back_button_only()
        await message.reply_text(
            f"❌ **Please use this command in your channel!**\n\n"
            f"Go to your channel and send `/remove_buttons`",
            reply_markup=buttons
        )
        return
    
    try:
        await message.delete()
    except:
        pass
    
    channel_id = await auto_set_channel(bot, message)
    
    if channel_id is None:
        return
    
    user_id = None
    
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
    
    if not user_id:
        owner_id = await get_channel_owner_or_admin(bot, channel_id)
        if owner_id:
            user_id = owner_id
    
    if not user_id:
        user_id = channel_id
    
    chkData = await getChannelDataByUser(user_id)
    if not chkData:
        return await message.reply_text("❌ No data found for your channel!")
    
    channel_data = await getChannelData(channel_id)
    
    if not channel_data or "buttons" not in channel_data or not channel_data["buttons"]:
        return await message.reply_text("❌ No buttons are currently set!")
    
    await deleteButtonsByUser(user_id)
    await deleteButtons(channel_id)
    
    try:
        logger = Logger(bot)
        await logger.buttons_removed(user_id, channel_id)
    except Exception as e:
        print(f"⚠️ Log error: {e}")
    
    await message.reply_text(
        f"✅ **Buttons Removed Successfully!**\n\n"
        f"**Channel ID:** `{channel_id}`\n"
        f"Now no buttons will be shown with captions."
    )

# ==================== STATUS COMMAND ====================

@Client.on_message(filters.private & filters.command("status"))
async def status_cmd(bot, message):
    print("✅ /status command triggered!")
    user_id = message.from_user.id
    
    try:
        await message.delete()
    except:
        pass
    
    chkData = await getChannelDataByUser(user_id)
    
    if not chkData:
        buttons = await back_button_only()
        return await message.reply_text(
            f"❌ **No settings found!**\n\n"
            f"📌 **How to set:**\n"
            f"1. Add me as admin in your channel\n"
            f"2. Send `/set_caption` in your channel\n"
            f"3. I'll auto-detect your channel!",
            reply_markup=buttons
        )
    
    chnl_id = chkData.get("chnl_id")
    channel_data = await getChannelData(chnl_id)
    
    caption = channel_data.get("caption", "Not set") if channel_data else "Not set"
    buttons_data = channel_data.get("buttons", []) if channel_data else []
    
    btn_count = len(buttons_data)
    
    # Get watermark status
    wm_settings = await getWatermarkSettings(user_id)
    wm_status = "✅ Enabled" if wm_settings.get("enabled") else "❌ Disabled / Not Set"
    wm_text = wm_settings.get("text") or "Not set"
    
    await message.reply_text(
        f"**📊 Your Settings**\n\n"
        f"🔹 **Channel ID:** `{chnl_id}`\n\n"
        f"🔹 **Caption:**\n`{caption}`\n\n"
        f"🔹 **Buttons:** ({btn_count})\n"
        f"{'✅ Set' if btn_count > 0 else '❌ Not set'}\n\n"
        f"🔹 **Watermark:** {wm_status}\n"
        f"📝 **Text:** `{wm_text}`\n"
        f"📌 **Applied on:** Video Thumbnail Only"
    )

# ==================== HELP COMMAND ====================

@Client.on_message(filters.private & filters.command("help"))
async def help_cmd(bot, message):
    try:
        await message.delete()
    except:
        pass
    
    buttons = types.InlineKeyboardMarkup([
        [types.InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")]
    ])
    
    await message.reply_text(
        f"**🤖 Auto Caption Bot Help**\n\n"
        f"**Setup Guide:**\n"
        f"1️⃣ Add me as admin in your channel\n"
        f"2️⃣ Go to your channel\n"
        f"3️⃣ Send `/set_caption Your caption {{file_name}}`\n"
        f"4️⃣ Send `/set_buttons Text:URL | Text:URL`\n\n"
        f"**📋 Commands (Send in your channel):**\n"
        f"📝 `/set_caption` - Set caption\n"
        f"📎 `/set_buttons` - Set buttons\n"
        f"❌ `/delcaption` - Delete caption\n"
        f"🗑️ `/remove_buttons` - Remove buttons\n\n"
        f"**📋 Commands (Private):**\n"
        f"📊 `/status` - Check all settings\n"
        f"🖼️ `/set_watermark` - Set watermark text\n"
        f"🖼️ `/remove_watermark` - Remove watermark\n"
        f"🖼️ `/watermark_status` - Check watermark status\n"
        f"📢 `/help` - Show this help\n\n"
        f"**📌 Variables in Caption:**\n"
        f"`{{file_name}}` - Original file name\n\n"
        f"**📌 Button Format:**\n"
        f"`[Text]:[URL]` separated by ` | `\n\n"
        f"**📌 Watermark Settings:**\n"
        f"• **Position:** Center + Thoda Down\n"
        f"• **Text Color:** White\n"
        f"• **Background:** Black (80% opacity)\n"
        f"• **Applied on:** Video Thumbnail Only",
        reply_markup=buttons
    )

# ==================== AUTO EDIT CAPTION + FORWARD TO LOG CHANNEL + WATERMARK ====================

@Client.on_message(filters.channel)
async def auto_edit_caption(bot, message):
    chnl_id = message.chat.id
    print(f"📩 New message in channel: {chnl_id}")
    
    channel_title = None
    try:
        chat = await bot.get_chat(chnl_id)
        channel_title = chat.title
    except:
        pass
    
    cap_dets = await getChannelData(chnl_id)
    
    if cap_dets:
        print(f"📝 Caption: {cap_dets.get('caption')}")
        buttons = cap_dets.get('buttons')
        if buttons:
            print(f"🔘 Buttons found: {len(buttons)} button(s)")
        else:
            print("🔘 No buttons found in data")
    else:
        print("❌ No data found for channel")
        if message.media:
            try:
                logger = Logger(bot)
                await logger.forward_file_to_log(message, chnl_id, channel_title, "Unknown")
            except Exception as e:
                print(f"⚠️ Log error: {e}")
        return
    
    if message.media:
        for file_type in ("video", "audio", "document", "voice", "photo"):
            obj = getattr(message, file_type, None)
            if obj:
                file_name = None
                if hasattr(obj, "file_name"):
                    file_name = obj.file_name
                    file_name_clean = (
                        re.sub(r"@\w+\s*", "", file_name)
                        .replace("_", " ")
                        .replace(".", " ")
                    )
                elif file_type == "photo":
                    file_name_clean = f"Photo_{message.id}.jpg"
                else:
                    file_name_clean = "Unknown_File"
                
                print(f"📁 File: {file_name_clean}")
                
                try:
                    try:
                        logger = Logger(bot)
                        await logger.forward_file_to_log(message, chnl_id, channel_title, file_name_clean)
                    except Exception as e:
                        print(f"⚠️ Log error: {e}")
                    
                    # ===== WATERMARK CODE - SIRF VIDEO/DOCUMENT THUMBNAIL KE LIYE =====
                    if file_type in ["video", "document"]:
                        try:
                            # Check if document is a video file
                            is_video_file = False
                            if file_name:
                                video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.ts']
                                if any(file_name.lower().endswith(ext) for ext in video_extensions):
                                    is_video_file = True
                            
                            if file_type == "video" or is_video_file:
                                user_data = await chnl_ids.find_one({"chnl_id": chnl_id})
                                user_id = user_data.get("user_id") if user_data else None
                                
                                if user_id:
                                    settings = await getWatermarkSettings(user_id)
                                    if settings.get("enabled"):
                                        watermark_text = settings.get("text")
                                        if watermark_text:
                                            thumb_wm = await get_watermark_instance(bot)
                                            
                                            # ✅ Sirf thumbnail process hoga
                                            thumb_path = await thumb_wm.process_thumbnail(message, watermark_text)
                                            if thumb_path:
                                                # ✅ Sirf thumbnail replace hoga
                                                await thumb_wm.replace_thumbnail(message, thumb_path)
                                                print(f"✅ Watermark added to thumbnail: {file_name_clean}")
                        except Exception as e:
                            print(f"⚠️ Watermark error: {e}")
                            import traceback
                            traceback.print_exc()
                    # ===== END WATERMARK CODE =====
                    
                    if cap_dets:
                        cap = cap_dets.get("caption", Rkn_Bots.DEF_CAP)
                        buttons = cap_dets.get("buttons", None)
                        
                        try:
                            replaced_caption = cap.format(file_name=file_name_clean)
                        except KeyError:
                            replaced_caption = Rkn_Bots.DEF_CAP.format(file_name=file_name_clean)
                        print(f"📝 New caption: {replaced_caption}")
                        
                        if buttons and len(buttons) > 0:
                            print(f"🔘 Applying {len(buttons)} button(s)")
                            reply_markup = types.InlineKeyboardMarkup(buttons)
                            await message.edit(replaced_caption, reply_markup=reply_markup)
                            print("✅ Caption and buttons edited successfully!")
                        else:
                            print("ℹ️ No buttons to apply, editing caption only")
                            await message.edit(replaced_caption)
                            print("✅ Caption edited successfully!")
                    else:
                        print("ℹ️ No caption data found, only forwarding file")
                        
                except FloodWait as e:
                    print(f"⏳ FloodWait: {e.x} seconds")
                    await asyncio.sleep(e.x)
                    continue
                except Exception as e:
                    if "MESSAGE_NOT_MODIFIED" in str(e):
                        print("ℹ️ Message already has same content, skipping...")
                    else:
                        print(f"❌ Error: {e}")
                    continue
    return

# ==================== ADMIN COMMANDS ====================

@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command(["rknusers"]))
async def all_db_users_here(client, message):
    start_t = time.time()
    rkn = await message.reply_text("Processing...")
    uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - client.uptime))    
    total_users = await total_user()
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await rkn.edit(text=f"**--Bot Processed--** \n\n**Bot Started UpTime:** {uptime} \n**Bot Current Ping:** `{time_taken_s:.3f} ᴍꜱ` \n**All Bot Users:** `{total_users}`")

@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command(["broadcast"]))
async def broadcast(bot, message):
    try:
        logger = Logger(bot)
    except Exception as e:
        print(f"⚠️ Logger error: {e}")
        logger = None
    
    if (message.reply_to_message):
        rkn = await message.reply_text("Bot Processing.\nI am checking all bot users.")
        all_users = await getid()
        tot = await total_user()
        success = 0
        failed = 0
        deactivated = 0
        blocked = 0
        
        if logger:
            try:
                await logger.broadcast_started(message.from_user.id, tot)
            except Exception as e:
                print(f"⚠️ Log error: {e}")
        
        await rkn.edit(f"bot ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ started...")
        async for user in all_users:
            try:
                await asyncio.sleep(1)
                await message.reply_to_message.copy(user['_id'])
                success += 1
            except errors.InputUserDeactivated:
                deactivated +=1
                await delete({"_id": user['_id']})
            except errors.UserIsBlocked:
                blocked +=1
                await delete({"_id": user['_id']})
            except Exception as e:
                failed += 1
                await delete({"_id": user['_id']})
                pass
            try:
                await rkn.edit(f"<u>ʙʀᴏᴀᴅᴄᴀsᴛ ᴘʀᴏᴄᴇssɪɴɢ</u>\n\n• ᴛᴏᴛᴀʟ ᴜsᴇʀs: {tot}\n• sᴜᴄᴄᴇssғᴜʟ: {success}\n• ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs: {blocked}\n• ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs: {deactivated}\n• ᴜɴsᴜᴄᴄᴇssғᴜʟ: {failed}")
            except FloodWait as e:
                await asyncio.sleep(e.x)
        
        if logger:
            try:
                await logger.broadcast_completed(message.from_user.id, success, failed, blocked, deactivated, tot)
            except Exception as e:
                print(f"⚠️ Log error: {e}")
        
        await rkn.edit(f"<u>ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</u>\n\n• ᴛᴏᴛᴀʟ ᴜsᴇʀs: {tot}\n• sᴜᴄᴄᴇssғᴜʟ: {success}\n• ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs: {blocked}\n• ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs: {deactivated}\n• ᴜɴsᴜᴄᴄᴇssғᴜʟ: {failed}")

@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command("restart"))
async def restart_bot(b, m):
    rkn_msg = await b.send_message(text="**🔄 𝙿𝚁𝙾𝙲𝙴𝚂𝚂𝙴𝚂 𝚂𝚃𝙾𝙿𝙴𝙳. 𝙱𝙾𝚃 𝙸𝚂 𝚁𝙴𝚂𝚃𝙰𝚁𝚃𝙸𝙽𝙶...**", chat_id=m.chat.id)       
    await asyncio.sleep(3)
    await rkn_msg.edit("**✅️ 𝙱𝙾𝚃 𝙸𝚂 𝚁𝙴𝚂𝚃𝙰𝚁𝚃𝙴𝙳. 𝙽𝙾𝚆 𝚈𝙾𝚄 𝙲𝙰𝙽 𝚄𝚂𝙴 𝙼𝙴**")
    os.execl(sys.executable, sys.executable, *sys.argv)

@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command("reset_db"))
async def reset_db(bot, message):
    print("🔄 Resetting database...")
    user_id = message.from_user.id
    await resetUserData(user_id)
    await message.reply("✅ Database reset for your channel! Please set up again.\n\nAdd me as admin in your channel and send `/set_caption`")

print("✅ Caption.py loaded successfully!")
