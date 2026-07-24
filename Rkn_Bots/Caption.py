# Caption.py - Complete with Simple 2 Command Watermark
# (c) @RknDeveloperr

from pyrogram import Client, filters, errors, types, enums
from config import Rkn_Bots
import asyncio, re, time, sys, os
from .database import total_user, getid, delete, insert, chnl_ids, users
from .database import addCap, updateCap, updateButtons, deleteButtons, getChannelData
from .database import addCapByUser, updateCapByUser, updateButtonsByUser, deleteButtonsByUser, getChannelDataByUser
from .database import resetChannelData, resetUserData
from pyrogram.errors import FloodWait

# ==================== ADD LOGGER IMPORT ====================
from .logger import Logger

# ==================== THUMBNAIL WATERMARK IMPORT ====================
try:
    from .thumbnail_watermark import thumb_watermark, init_thumb_watermark
    THUMB_WATERMARK_AVAILABLE = True
    print("✅ Thumbnail Watermark loaded successfully!")
except ImportError as e:
    print(f"⚠️ Thumbnail Watermark not found: {e}")
    THUMB_WATERMARK_AVAILABLE = False

print("🔄 Loading Caption.py...")

# ==================== WATERMARK DATABASE FUNCTIONS ====================

async def get_channel_watermark(channel_id):
    """Get watermark text for channel"""
    try:
        data = await chnl_ids.find_one({"chnl_id": channel_id})
        if data:
            return data.get("watermark_text", "")
        return ""
    except Exception as e:
        print(f"❌ Get watermark error: {e}")
        return ""

async def save_channel_watermark(channel_id, text):
    """Save watermark text for channel"""
    try:
        await chnl_ids.update_one(
            {"chnl_id": channel_id},
            {"$set": {"watermark_text": text}},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"❌ Save watermark error: {e}")
        return False

async def remove_channel_watermark(channel_id):
    """Remove watermark text for channel"""
    try:
        await chnl_ids.update_one(
            {"chnl_id": channel_id},
            {"$unset": {"watermark_text": ""}}
        )
        return True
    except Exception as e:
        print(f"❌ Remove watermark error: {e}")
        return False

# ==================== MAIN MENU BUTTONS ====================

async def main_menu_buttons():
    """Main menu with buttons"""
    buttons = types.InlineKeyboardMarkup([
        [
            types.InlineKeyboardButton("📝 Set Caption", callback_data="set_caption"),
            types.InlineKeyboardButton("📎 Add Button", callback_data="add_button")
        ],
        [
            types.InlineKeyboardButton("📊 Status", callback_data="view_status")
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
    
    # ==================== BACK TO MENU ====================
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
    
    # ==================== SET CAPTION ====================
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
    
    # ==================== ADD BUTTON ====================
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
    
    # ==================== VIEW STATUS ====================
    elif data == "view_status":
        await status_cmd(bot, callback_query.message)
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

# ==================== AUTO SET CHANNEL ====================

async def auto_set_channel(bot, message):
    """Auto set channel when user sends command in channel"""
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
    
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
    
    if not user_id:
        owner_id = await get_channel_owner_or_admin(bot, channel_id)
        if owner_id:
            user_id = owner_id
            print(f"👤 Found channel owner/admin: {user_id}")
    
    if not user_id:
        user_id = channel_id
        print(f"⚠️ Using channel ID as user ID: {user_id}")
    
    print(f"👤 Final User ID: {user_id}")
    
    chkData = await getChannelDataByUser(user_id)
    
    if chkData and chkData.get("chnl_id") == channel_id:
        return channel_id
    
    if chkData:
        await chnl_ids.delete_many({"user_id": user_id})
        await chnl_ids.delete_many({"chnl_id": chkData.get("chnl_id")})
    
    await addCapByUser(user_id, channel_id, Rkn_Bots.DEF_CAP)
    await addCap(channel_id, Rkn_Bots.DEF_CAP)
    
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
        f"**Channel Name:** {channel_title or 'Unknown'}\n\n"
        f"Now you can use:\n"
        f"• `/set_caption` - Set your caption\n"
        f"• `/set_buttons` - Set your buttons"
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

# ==================== WATERMARK COMMANDS ====================

@Client.on_message(filters.command("setwatermark") & (filters.channel | filters.private))
async def set_watermark(bot, message):
    """Set watermark - CHANNEL ONLY"""
    
    # Agar private me aaya hai toh guide karo
    if message.chat.type == enums.ChatType.PRIVATE:
        return await message.reply(
            f"❌ **Please use this command in your channel!**\n\n"
            f"📌 **How to use:**\n"
            f"1. Add me as admin in your channel\n"
            f"2. Go to your channel\n"
            f"3. Send: `/setwatermark Your Text Here`\n\n"
            f"**Example:**\n"
            f"`/setwatermark @wolverine273`\n"
            f"`/setwatermark © 2024 MyChannel`"
        )
    
    try:
        await message.delete()
    except:
        pass
    
    if not THUMB_WATERMARK_AVAILABLE:
        return await message.reply("❌ Watermark module not available!")
    
    # Check bot is admin
    channel_id = message.chat.id
    is_admin = await check_bot_admin(bot, channel_id)
    if not is_admin:
        return await message.reply(
            f"❌ **I'm not admin in this channel!**\n\n"
            f"Please add me as admin first."
        )
    
    # Check if text provided
    if len(message.command) < 2:
        current_text = await get_channel_watermark(channel_id)
        if current_text:
            return await message.reply(
                f"📝 **Current Watermark:**\n`{current_text}`\n\n"
                f"**To Change:** `/setwatermark New Text`\n"
                f"**To Remove:** `/removewatermark`\n\n"
                f"**Example:** `/setwatermark @wolverine273`"
            )
        else:
            return await message.reply(
                f"📝 **Set Watermark**\n\n"
                f"**Usage:** `/setwatermark Your Text Here`\n\n"
                f"**Example:**\n"
                f"`/setwatermark @wolverine273`\n"
                f"`/setwatermark © 2024 MyChannel`\n\n"
                f"⚠️ Watermark will appear **center** in **white** color on all video thumbnails."
            )
    
    watermark_text = message.text.split(" ", 1)[1]
    
    # Save watermark
    success = await save_channel_watermark(channel_id, watermark_text)
    
    if not success:
        return await message.reply("❌ Failed to save watermark!")
    
    # Update global instance
    if THUMB_WATERMARK_AVAILABLE and thumb_watermark:
        thumb_watermark.settings["text"] = watermark_text
        thumb_watermark.settings["enabled"] = True
    
    await message.reply(
        f"✅ **Watermark Set Successfully!**\n\n"
        f"**Text:** `{watermark_text}`\n\n"
        f"📍 Position: **Center**\n"
        f"🎨 Color: **White**\n\n"
        f"Now all video thumbnails will have this watermark."
    )

@Client.on_message(filters.command("removewatermark") & (filters.channel | filters.private))
async def remove_watermark(bot, message):
    """Remove watermark - CHANNEL ONLY"""
    
    if message.chat.type == enums.ChatType.PRIVATE:
        return await message.reply(
            f"❌ **Please use this command in your channel!**\n\n"
            f"Go to your channel and send: `/removewatermark`"
        )
    
    try:
        await message.delete()
    except:
        pass
    
    if not THUMB_WATERMARK_AVAILABLE:
        return await message.reply("❌ Watermark module not available!")
    
    channel_id = message.chat.id
    
    # Check bot is admin
    is_admin = await check_bot_admin(bot, channel_id)
    if not is_admin:
        return await message.reply(
            f"❌ **I'm not admin in this channel!**\n\n"
            f"Please add me as admin first."
        )
    
    # Check if watermark exists
    current_text = await get_channel_watermark(channel_id)
    if not current_text:
        return await message.reply(
            f"❌ **No watermark found!**\n\n"
            f"Use `/setwatermark Text` to add one."
        )
    
    # Remove watermark
    success = await remove_channel_watermark(channel_id)
    
    if not success:
        return await message.reply("❌ Failed to remove watermark!")
    
    # Update global instance
    if THUMB_WATERMARK_AVAILABLE and thumb_watermark:
        thumb_watermark.settings["text"] = ""
        thumb_watermark.settings["enabled"] = False
    
    await message.reply(
        f"✅ **Watermark Removed Successfully!**\n\n"
        f"No more watermarks will be added to video thumbnails."
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
    btn_preview = "\n".join([f"• {btn[0].text} → {btn[0].url}" for btn in buttons_data]) if buttons_data else "No buttons set"
    
    # Get watermark status
    wm_text = await get_channel_watermark(chnl_id)
    if wm_text:
        wm_status = f"\n\n🖼️ **Watermark:** ✅ Enabled\n📝 **Text:** `{wm_text}`\n📍 **Position:** Center\n🎨 **Color:** White"
    else:
        wm_status = "\n\n🖼️ **Watermark:** ❌ Not Set\n📝 Use `/setwatermark` in your channel to add one!"
    
    await message.reply_text(
        f"**📊 Your Settings**\n\n"
        f"🔹 **Channel ID:** `{chnl_id}`\n\n"
        f"🔹 **Caption:**\n`{caption}`\n\n"
        f"🔹 **Buttons:** ({btn_count})\n{btn_preview}{wm_status}"
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
    
    help_text = f"""
**🤖 Auto Caption Bot Help**

**Setup Guide:**
1️⃣ Add me as admin in your channel
2️⃣ Go to your channel
3️⃣ Send `/set_caption Your caption {{file_name}}`
4️⃣ Send `/set_buttons Text:URL | Text:URL`

**📋 Commands (Send in your channel):**
📝 `/set_caption` - Set caption
📎 `/set_buttons` - Set buttons
❌ `/delcaption` - Delete caption
🗑️ `/remove_buttons` - Remove buttons

**🖼️ Watermark Commands (Send in your channel):**
✅ `/setwatermark Text` - Set watermark (Center, White)
❌ `/removewatermark` - Remove watermark

**📋 Commands (Private):**
📊 `/status` - Check settings
📢 `/help` - Show this help

**🔒 Admin Only Commands:**
👥 `/rknusers` - Show total users
📢 `/broadcast` - Broadcast message
🔄 `/restart` - Restart bot
🗑️ `/reset_db` - Reset database

**📌 Variables in Caption:**
`{{file_name}}` - Original file name

**📌 Button Format:**
`[Text]:[URL]` separated by ` | `
"""
    
    await message.reply_text(help_text, reply_markup=buttons)

# ==================== AUTO EDIT CAPTION + WATERMARK ====================

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
                    
                    # ============ WATERMARK FOR VIDEOS ============
                    if file_type == "video" and THUMB_WATERMARK_AVAILABLE:
                        try:
                            # Get channel-specific watermark
                            watermark_text = await get_channel_watermark(chnl_id)
                            
                            if watermark_text and hasattr(bot, 'thumb_watermark') and bot.thumb_watermark:
                                print(f"🖼️ Adding watermark for channel {chnl_id}: {watermark_text}")
                                
                                # Process thumbnail
                                watermarked_thumb = await bot.thumb_watermark.process_thumbnail(message, watermark_text)
                                
                                if watermarked_thumb and os.path.exists(watermarked_thumb):
                                    print(f"✅ Thumbnail watermarked: {watermarked_thumb}")
                                    
                                    # 🔥 IMPORTANT: Replace video thumbnail
                                    success = await bot.thumb_watermark.replace_thumbnail(message, watermarked_thumb)
                                    
                                    if success:
                                        print("✅ Video thumbnail replaced with watermarked version!")
                                    else:
                                        print("⚠️ Could not replace thumbnail, sending as document")
                                        # Fallback: send as document
                                        await message.reply_document(
                                            document=watermarked_thumb,
                                            caption="🖼️ Watermarked Thumbnail"
                                        )
                                    
                                    # Cleanup
                                    try:
                                        os.remove(watermarked_thumb)
                                    except:
                                        pass
                        except Exception as e:
                            print(f"❌ Thumbnail watermark error: {e}")
                            import traceback
                            traceback.print_exc()
                    
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

# ==================== ADMIN COMMANDS (ADMIN ONLY) ====================

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
