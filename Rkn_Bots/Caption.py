from pyrogram import Client, filters, errors, types, enums
from config import Rkn_Bots
import asyncio, re, time, sys, os
from .database import total_user, getid, delete, insert, chnl_ids, users
from .database import addCap, updateCap, updateButtons, deleteButtons, getChannelData
from .database import addCapByUser, updateCapByUser, updateButtonsByUser, deleteButtonsByUser, getChannelDataByUser
from .database import resetChannelData, resetUserData
from pyrogram.errors import FloodWait
from .logger import Logger

# ✅ WATERMARK IMPORT
try:
    from .thumbnail_watermark import ThumbnailWatermark
    from pyrogram.types import InputMediaPhoto
    WATERMARK_AVAILABLE = True
    print("✅ Watermark module loaded!")
except:
    WATERMARK_AVAILABLE = False
    class ThumbnailWatermark:
        def __init__(self, bot): pass
        async def process_thumbnail(self, message, text): return None
    print("⚠️ Watermark module not available")

print("🔄 Loading Caption.py...")

# ✅ DUPLICATE MESSAGE TRACKING
processed_messages = set()
processed_messages_max = 1000

async def main_menu_buttons():
    buttons = types.InlineKeyboardMarkup([
        [
            types.InlineKeyboardButton("📝 Set Caption", callback_data="set_caption"),
            types.InlineKeyboardButton("📎 Add Button", callback_data="add_button")
        ], 
        [
            types.InlineKeyboardButton("📢 Main Channel", url="https://t.me/wolverine273"),
            types.InlineKeyboardButton("💬 Help Group", url="https://t.me/WOLVERIN_P")
        ]
    ])
    return buttons

async def back_button_only():
    buttons = types.InlineKeyboardMarkup([
        [types.InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ])
    return buttons

async def get_home_caption(user_id, first_name=None):
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

async def check_bot_admin(bot, channel_id):
    try:
        chat_member = await bot.get_chat_member(channel_id, (await bot.get_me()).id)
        if chat_member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            return True
        return False
    except Exception as e:
        print(f"❌ Bot admin check failed: {e}")
        return False

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
            print(f"⚠️ Log error: {e}")
    
    buttons = await main_menu_buttons()
    caption = await get_home_caption(user_id, first_name)
    
    await message.reply_photo(
        photo=Rkn_Bots.RKN_PIC,
        caption=caption,
        reply_markup=buttons
    )

@Client.on_callback_query()
async def callback_handler(bot, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data
    first_name = callback_query.from_user.first_name or "User"
    
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

# ✅ FIXED - No 'await' before get_chat_members
async def get_channel_owner_or_admin(bot, channel_id):
    try:
        admins = bot.get_chat_members(channel_id, filter=enums.ChatMembersFilter.ADMINISTRATORS)
        async for admin in admins:
            if admin.user and not admin.user.is_bot:
                return admin.user.id
    except Exception as e:
        print(f"⚠️ Could not get channel admins: {e}")
    return None

async def auto_set_channel(bot, message):
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

# ✅ WATERMARK COMMANDS
@Client.on_message(filters.command("set_watermark") & (filters.channel | filters.private))
async def set_watermark(bot, message):
    if message.chat.type == enums.ChatType.PRIVATE:
        buttons = await back_button_only()
        await message.reply_text(
            f"❌ **Please use this command in your channel!**\n\n"
            f"Go to your channel and send:\n"
            f"`/set_watermark Your Text Here`\n\n"
            f"**Example:**\n"
            f"`/set_watermark @YourChannel`",
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
    
    if len(message.command) < 2:
        await message.reply_text(
            f"❌ **Please provide watermark text!**\n\n"
            f"**Usage:** `/set_watermark Your Text`\n"
            f"**Example:** `/set_watermark @YourChannel`"
        )
        return
    
    watermark_text = message.text.split(" ", 1)[1]
    
    await chnl_ids.update_one(
        {"user_id": user_id}, 
        {"$set": {"watermark": watermark_text}},
        upsert=True
    )
    await chnl_ids.update_one(
        {"chnl_id": channel_id}, 
        {"$set": {"watermark": watermark_text}},
        upsert=True
    )
    
    await message.reply_text(
        f"✅ **Watermark Set Successfully!**\n\n"
        f"**Channel ID:** `{channel_id}`\n"
        f"**Watermark Text:** `{watermark_text}`"
    )

@Client.on_message(filters.command("remove_watermark") & (filters.channel | filters.private))
async def remove_watermark(bot, message):
    if message.chat.type == enums.ChatType.PRIVATE:
        buttons = await back_button_only()
        await message.reply_text(
            f"❌ **Please use this command in your channel!**\n\n"
            f"Go to your channel and send `/remove_watermark`",
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
    
    await chnl_ids.update_one(
        {"user_id": user_id}, 
        {"$unset": {"watermark": ""}}
    )
    await chnl_ids.update_one(
        {"chnl_id": channel_id}, 
        {"$unset": {"watermark": ""}}
    )
    
    await message.reply_text(
        f"✅ **Watermark Removed Successfully!**\n\n"
        f"**Channel ID:** `{channel_id}`"
    )

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
    watermark = channel_data.get("watermark", "Not set") if channel_data else "Not set"
    
    btn_count = len(buttons_data)
    btn_preview = "\n".join([f"• {btn[0].text} → {btn[0].url}" for btn in buttons_data]) if buttons_data else "No buttons set"
    
    await message.reply_text(
        f"**📊 Your Settings**\n\n"
        f"🔹 **Channel ID:** `{chnl_id}`\n\n"
        f"🔹 **Caption:**\n`{caption}`\n\n"
        f"🔹 **Buttons:** ({btn_count})\n{btn_preview}\n\n"
        f"🔹 **Watermark:** `{watermark}`"
    )

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
        f"4️⃣ Send `/set_buttons Text:URL | Text:URL`\n"
        f"5️⃣ Send `/set_watermark Your Text` for video thumbnails\n\n"
        f"**📋 Commands (Send in your channel):**\n"
        f"📝 `/set_caption` - Set caption\n"
        f"📎 `/set_buttons` - Set buttons\n"
        f"🖼️ `/set_watermark` - Set watermark on thumbnails\n"
        f"❌ `/delcaption` - Delete caption\n"
        f"🗑️ `/remove_buttons` - Remove buttons\n"
        f"🗑️ `/remove_watermark` - Remove watermark\n\n"
        f"**📋 Commands (Private):**\n"
        f"📊 `/status` - Check settings\n"
        f"📢 `/help` - Show this help\n\n"
        f"**📌 Variables in Caption:**\n"
        f"`{{file_name}}` - Original file name\n\n"
        f"**📌 Button Format:**\n"
        f"`[Text]:[URL]` separated by ` | `",
        reply_markup=buttons
    )

# ✅ AUTO EDIT CAPTION WITH WATERMARK - DUPLICATE FIXED
@Client.on_message(filters.channel)
async def auto_edit_caption(bot, message):
    global processed_messages
    
    chnl_id = message.chat.id
    
    # ✅ DUPLICATE CHECK - Skip if already processed
    msg_key = f"{chnl_id}_{message.id}"
    if msg_key in processed_messages:
        print(f"⏭️ Skipping duplicate message: {msg_key}")
        return
    
    # ✅ Add to processed set
    processed_messages.add(msg_key)
    if len(processed_messages) > processed_messages_max:
        processed_messages.clear()
    
    print(f"📩 New message in channel: {chnl_id}")
    
    channel_title = None
    try:
        chat = await bot.get_chat(chnl_id)
        channel_title = chat.title
    except:
        pass
    
    cap_dets = await getChannelData(chnl_id)
    
    if not cap_dets:
        print("❌ No data found for channel")
        if message.media:
            try:
                logger = Logger(bot)
                await logger.forward_file_to_log(message, chnl_id, channel_title, "Unknown")
            except Exception as e:
                print(f"⚠️ Log error: {e}")
        return
    
    if not message.media:
        return
    
    for file_type in ("video", "audio", "document", "voice", "photo"):
        obj = getattr(message, file_type, None)
        if not obj:
            continue
            
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
        
        # ✅ WATERMARK APPLY - ONLY FOR VIDEOS
        watermarked_thumb = None
        if file_type == "video" and WATERMARK_AVAILABLE:
            try:
                channel_data = await chnl_ids.find_one({"chnl_id": chnl_id})
                watermark_text = channel_data.get("watermark") if channel_data else None
                
                if watermark_text:
                    print(f"🖼️ Applying watermark: {watermark_text}")
                    try:
                        thumb_wm = ThumbnailWatermark(bot)
                        watermarked_thumb = await thumb_wm.process_thumbnail(message, watermark_text)
                        if watermarked_thumb and os.path.exists(watermarked_thumb):
                            print(f"✅ Watermark applied: {watermarked_thumb}")
                        else:
                            print("❌ Watermark failed")
                            watermarked_thumb = None
                    except Exception as e:
                        print(f"❌ Watermark error: {e}")
                        watermarked_thumb = None
            except Exception as e:
                print(f"❌ Watermark module error: {e}")
        
        try:
            # ✅ LOG TO CHANNEL - ONLY ONCE
            try:
                logger = Logger(bot)
                await logger.forward_file_to_log(message, chnl_id, channel_title, file_name_clean)
            except Exception as e:
                print(f"⚠️ Log error: {e}")
            
            cap = cap_dets.get("caption", Rkn_Bots.DEF_CAP)
            buttons = cap_dets.get("buttons", None)
            
            try:
                replaced_caption = cap.format(file_name=file_name_clean)
            except KeyError:
                replaced_caption = Rkn_Bots.DEF_CAP.format(file_name=file_name_clean)
            print(f"📝 New caption: {replaced_caption}")
            
            # Edit caption
            if buttons and len(buttons) > 0:
                reply_markup = types.InlineKeyboardMarkup(buttons)
                await message.edit(replaced_caption, reply_markup=reply_markup)
                print("✅ Caption + Buttons edited!")
            else:
                await message.edit(replaced_caption)
                print("✅ Caption edited!")
            
            # ✅ REPLACE THUMBNAIL WITH WATERMARK
            if watermarked_thumb and os.path.exists(watermarked_thumb) and WATERMARK_AVAILABLE:
                try:
                    await message.edit_media(
                        InputMediaPhoto(
                            media=watermarked_thumb,
                            caption=message.caption or replaced_caption
                        )
                    )
                    print("✅ Thumbnail replaced with watermark!")
                    try:
                        os.remove(watermarked_thumb)
                    except:
                        pass
                except Exception as e:
                    print(f"❌ Thumbnail replace error: {e}")
                    
        except FloodWait as e:
            wait_time = e.value if hasattr(e, 'value') else 5
            print(f"⏳ FloodWait: {wait_time} seconds")
            await asyncio.sleep(wait_time)
        except Exception as e:
            if "MESSAGE_NOT_MODIFIED" in str(e):
                print("ℹ️ Message already has same content")
            else:
                print(f"❌ Error: {e}")

# ✅ ADMIN COMMANDS
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
                wait_time = e.value if hasattr(e, 'value') else 5
                await asyncio.sleep(wait_time)
        
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
