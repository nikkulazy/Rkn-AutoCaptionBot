# (c) @RknDeveloperr
# Rkn Developer 
# Don't Remove Credit 😔

from pyrogram import Client, filters, errors, types
from config import Rkn_Bots
import asyncio, re, time, sys, os
from .database import total_user, getid, delete, insert, chnl_ids
from .database import addCap, updateCap, updateButtons, deleteButtons, getChannelData
from .database import addCapByUser, updateCapByUser, updateButtonsByUser, deleteButtonsByUser, getChannelDataByUser
from .database import resetChannelData, resetUserData
from .logger import Logger
from pyrogram.errors import FloodWait

print("🔄 Loading Caption.py...")

# ==================== MAIN MENU BUTTONS ====================

async def main_menu_buttons():
    """Main menu with buttons"""
    buttons = types.InlineKeyboardMarkup([
        [
            types.InlineKeyboardButton("📝 Set Caption", callback_data="set_caption"),
            types.InlineKeyboardButton("📎 Add Button", callback_data="add_button")
        ],
        [
            types.InlineKeyboardButton("📊 Status", callback_data="status"),
            types.InlineKeyboardButton("🗑️ Remove Channel", callback_data="remove_channel")
        ],
        [
            types.InlineKeyboardButton("📢 Main Channel", url="https://t.me/wolverine273"),
            types.InlineKeyboardButton("💬 Help Group", url="https://t.me/WOLVERIN_P")
        ]
    ])
    return buttons

async def caption_page_buttons():
    """Caption page with Delete Caption and Back buttons"""
    buttons = types.InlineKeyboardMarkup([
        [types.InlineKeyboardButton("❌ Delete Caption", callback_data="delete_caption")],
        [types.InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ])
    return buttons

async def button_page_buttons():
    """Button page with Remove Button and Back buttons"""
    buttons = types.InlineKeyboardMarkup([
        [types.InlineKeyboardButton("🗑️ Remove Button", callback_data="remove_button")],
        [types.InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ])
    return buttons

async def back_button_only():
    """Only back button"""
    buttons = types.InlineKeyboardMarkup([
        [types.InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ])
    return buttons

# ==================== GET HOME MENU CAPTION ====================

async def get_home_caption(user_id):
    """Get home menu caption with channel status"""
    chkData = await getChannelDataByUser(user_id)
    
    if chkData:
        channel_id = chkData.get("chnl_id", "Not set")
        channel_status = f"✅ **Channel ID:** `{channel_id}`"
    else:
        channel_status = "❌ **Channel ID:** `Not saved yet!`\n\n📌 Please set your channel first:\n`/set_channel -1001234567890`"
    
    caption = f"<b>🏠 Main Menu</b>\n\n"
    caption += f"{channel_status}\n\n"
    caption += f"<i>Select an option below to manage your settings:</i>"
    
    return caption

# ==================== START COMMAND ====================

@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(bot, message):
    print("✅ /start command triggered!")
    user_id = int(message.from_user.id)
    await insert(user_id)
    
    # 🟢 Log user start
    logger = Logger(bot)
    await logger.user_start(
        user_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    buttons = await main_menu_buttons()
    caption = await get_home_caption(user_id)
    
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
    logger = Logger(bot)
    
    # ✅ OLD MESSAGE DELETE KARO
    try:
        await callback_query.message.delete()
    except:
        pass
    
    # ========== BACK TO MENU ==========
    if data == "back_to_menu":
        buttons = await main_menu_buttons()
        caption = await get_home_caption(user_id)
        
        await callback_query.message.reply_photo(
            photo=Rkn_Bots.RKN_PIC,
            caption=caption,
            reply_markup=buttons
        )
        await callback_query.answer()
        return
    
    # ========== SET CAPTION PAGE ==========
    elif data == "set_caption":
        # 🟢 Log command
        await logger.user_command(
            user_id=user_id,
            command="set_caption (from menu)",
            username=callback_query.from_user.username,
            first_name=callback_query.from_user.first_name
        )
        
        chkData = await getChannelDataByUser(user_id)
        
        if not chkData:
            buttons = await back_button_only()
            await callback_query.message.reply_text(
                f"❌ **No channel found!**\n\n"
                f"Please set your channel ID first:\n"
                f"`/set_channel -1001234567890`",
                reply_markup=buttons
            )
            await callback_query.answer()
            return
        
        chnl_id = chkData.get("chnl_id")
        channel_data = await getChannelData(chnl_id)
        current_caption = channel_data.get("caption", "Not set") if channel_data else "Not set"
        
        buttons = await caption_page_buttons()
        await callback_query.message.reply_text(
            f"**📝 Set Caption**\n\n"
            f"**Current Caption:**\n`{current_caption}`\n\n"
            f"**How to Set:**\n"
            f"`/set_caption Your caption here {{file_name}}`\n\n"
            f"**Example:**\n"
            f"`/set_caption 📁 File: {{file_name}}\nJoin @wolverine273`\n\n"
            f"**Variables:**\n"
            f"• `{{file_name}}` - Shows original file name\n\n"
            f"<i>Type the command with your new caption.</i>",
            reply_markup=buttons
        )
        await callback_query.answer()
    
    # ========== DELETE CAPTION ==========
    elif data == "delete_caption":
        chkData = await getChannelDataByUser(user_id)
        
        if not chkData:
            buttons = await back_button_only()
            await callback_query.message.reply_text(
                f"❌ **No channel found!**\n\n"
                f"Please set your channel ID first.",
                reply_markup=buttons
            )
            await callback_query.answer()
            return
        
        chnl_id = chkData.get("chnl_id")
        await updateCapByUser(user_id, Rkn_Bots.DEF_CAP)
        await updateCap(chnl_id, Rkn_Bots.DEF_CAP)
        
        # 🟢 Log caption deleted
        await logger.caption_deleted(user_id, chnl_id)
        
        buttons = await back_button_only()
        await callback_query.message.reply_text(
            f"✅ **Caption Deleted Successfully!**\n\n"
            f"Now using default caption.\n\n"
            f"**Default Caption:**\n`{Rkn_Bots.DEF_CAP}`",
            reply_markup=buttons
        )
        await callback_query.answer()
    
    # ========== ADD BUTTON PAGE ==========
    elif data == "add_button":
        # 🟢 Log command
        await logger.user_command(
            user_id=user_id,
            command="add_button (from menu)",
            username=callback_query.from_user.username,
            first_name=callback_query.from_user.first_name
        )
        
        chkData = await getChannelDataByUser(user_id)
        
        if not chkData:
            buttons = await back_button_only()
            await callback_query.message.reply_text(
                f"❌ **No channel found!**\n\n"
                f"Please set your channel ID first:\n"
                f"`/set_channel -1001234567890`",
                reply_markup=buttons
            )
            await callback_query.answer()
            return
        
        chnl_id = chkData.get("chnl_id")
        channel_data = await getChannelData(chnl_id)
        current_buttons = channel_data.get("buttons", []) if channel_data else []
        
        btn_preview = ""
        if current_buttons:
            btn_preview = "\n**Current Buttons:**\n"
            btn_preview += "\n".join([f"• {btn[0].text} → {btn[0].url}" for btn in current_buttons])
            btn_preview += f"\n\n**Total:** `{len(current_buttons)}` button(s)\n"
        else:
            btn_preview = "\n❌ No buttons set yet.\n"
        
        buttons = await button_page_buttons()
        await callback_query.message.reply_text(
            f"**📎 Add Button**\n\n"
            f"{btn_preview}\n"
            f"**How to Add Buttons:**\n"
            f"`/set_buttons [Text]:[URL] | [Text]:[URL]`\n\n"
            f"**Example 1 (Single):**\n"
            f"`/set_buttons 📢 Join:https://t.me/wolverine273`\n\n"
            f"**Example 2 (Multiple):**\n"
            f"`/set_buttons 📢 Channel:https://t.me/wolverine273 | 💬 Group:https://t.me/WOLVERIN_P`\n\n"
            f"<i>Type the command with your buttons.</i>",
            reply_markup=buttons
        )
        await callback_query.answer()
    
    # ========== REMOVE BUTTON ==========
    elif data == "remove_button":
        chkData = await getChannelDataByUser(user_id)
        
        if not chkData:
            buttons = await back_button_only()
            await callback_query.message.reply_text(
                f"❌ **No channel found!**",
                reply_markup=buttons
            )
            await callback_query.answer()
            return
        
        chnl_id = chkData.get("chnl_id")
        channel_data = await getChannelData(chnl_id)
        
        if not channel_data or "buttons" not in channel_data or not channel_data["buttons"]:
            buttons = await back_button_only()
            await callback_query.message.reply_text(
                f"❌ **No buttons to remove!**\n\n"
                f"Use `/set_buttons` to add buttons first.",
                reply_markup=buttons
            )
            await callback_query.answer()
            return
        
        await deleteButtonsByUser(user_id)
        await deleteButtons(chnl_id)
        
        # 🟢 Log buttons removed
        await logger.buttons_removed(user_id, chnl_id)
        
        buttons = await back_button_only()
        await callback_query.message.reply_text(
            f"✅ **Button Removed Successfully!**\n\n"
            f"Now no buttons will be shown with captions.\n\n"
            f"<i>Use Add Button to add new buttons.</i>",
            reply_markup=buttons
        )
        await callback_query.answer()
    
    # ========== REMOVE CHANNEL ==========
    elif data == "remove_channel":
        chkData = await getChannelDataByUser(user_id)
        
        if not chkData:
            buttons = await back_button_only()
            await callback_query.message.reply_text(
                f"❌ **No channel found!**\n\n"
                f"You don't have any channel set.",
                reply_markup=buttons
            )
            await callback_query.answer()
            return
        
        # Confirm removal
        confirm_buttons = types.InlineKeyboardMarkup([
            [
                types.InlineKeyboardButton("✅ Yes, Remove", callback_data="confirm_remove_channel"),
                types.InlineKeyboardButton("❌ Cancel", callback_data="back_to_menu")
            ]
        ])
        
        await callback_query.message.reply_text(
            f"⚠️ **Remove Channel**\n\n"
            f"Are you sure you want to remove your channel?\n"
            f"Channel ID: `{chkData.get('chnl_id')}`\n\n"
            f"This will remove all your settings!",
            reply_markup=confirm_buttons
        )
        await callback_query.answer()
    
    # ========== CONFIRM REMOVE CHANNEL ==========
    elif data == "confirm_remove_channel":
        chkData = await getChannelDataByUser(user_id)
        
        if chkData:
            chnl_id = chkData.get("chnl_id")
            # ✅ DIRECT DATABASE DELETE
            await chnl_ids.delete_many({"user_id": user_id})
            await chnl_ids.delete_many({"chnl_id": chnl_id})
            
            # 🟢 Log channel removed
            await logger.channel_removed(user_id, chnl_id)
            
            print(f"✅ Channel {chnl_id} removed for user {user_id}")
        
        buttons = await main_menu_buttons()
        caption = await get_home_caption(user_id)
        
        await callback_query.message.reply_photo(
            photo=Rkn_Bots.RKN_PIC,
            caption=f"✅ **Channel Removed Successfully!**\n\n"
            f"Your channel has been removed.\n\n"
            f"{caption}",
            reply_markup=buttons
        )
        await callback_query.answer()
    
    # ========== STATUS ==========
    elif data == "status":
        chkData = await getChannelDataByUser(user_id)
        
        if not chkData:
            buttons = await back_button_only()
            await callback_query.message.reply_text(
                f"❌ **No settings found!**\n\n"
                f"Please set your channel first:\n"
                f"`/set_channel -1001234567890`",
                reply_markup=buttons
            )
            await callback_query.answer()
            return
        
        chnl_id = chkData.get("chnl_id")
        channel_data = await getChannelData(chnl_id)
        
        caption = channel_data.get("caption", "Not set") if channel_data else "Not set"
        buttons_data = channel_data.get("buttons", []) if channel_data else []
        
        btn_count = len(buttons_data)
        btn_preview = "\n".join([f"• {btn[0].text} → {btn[0].url}" for btn in buttons_data]) if buttons_data else "No buttons set"
        
        buttons = await back_button_only()
        await callback_query.message.reply_text(
            f"**📊 Your Settings**\n\n"
            f"🔹 **Channel ID:** `{chnl_id}`\n\n"
            f"🔹 **Caption:**\n`{caption}`\n\n"
            f"🔹 **Buttons:** ({btn_count})\n{btn_preview}",
            reply_markup=buttons
        )
        await callback_query.answer()

# ==================== REMOVE CHANNEL COMMAND ====================

@Client.on_message(filters.private & filters.command("remove_channel"))
async def remove_channel_cmd(bot, message):
    print("✅ /remove_channel command triggered!")
    user_id = message.from_user.id
    logger = Logger(bot)
    
    try:
        await message.delete()
    except:
        pass
    
    # Check if channel exists
    chkData = await getChannelDataByUser(user_id)
    
    if not chkData:
        buttons = await back_button_only()
        return await message.reply_text(
            "❌ **No channel found!**\n\n"
            "You don't have any channel set.",
            reply_markup=buttons
        )
    
    # ✅ CHANNEL ID LE LO
    chnl_id = chkData.get("chnl_id")
    
    # ✅ DATABASE SE COMPLETE DELETE KARO
    await chnl_ids.delete_many({"user_id": user_id})
    await chnl_ids.delete_many({"chnl_id": chnl_id})
    
    # 🟢 Log channel removed
    await logger.channel_removed(user_id, chnl_id)
    
    print(f"✅ Channel {chnl_id} removed for user {user_id}")
    
    # ✅ HOME MENU SHOW KARO
    buttons = await main_menu_buttons()
    caption = await get_home_caption(user_id)
    
    await message.reply_photo(
        photo=Rkn_Bots.RKN_PIC,
        caption=f"✅ **Channel Removed Successfully!**\n\n"
        f"Your channel has been removed.\n\n"
        f"{caption}",
        reply_markup=buttons
    )

# ==================== SET CHANNEL ====================

@Client.on_message(filters.private & filters.command("set_channel"))
async def setChannel(bot, message):
    print("✅ /set_channel command triggered!")
    user_id = message.from_user.id
    logger = Logger(bot)
    
    try:
        await message.delete()
    except:
        pass
    
    if len(message.command) < 2:
        buttons = await back_button_only()
        return await message.reply_text(
            "❌ **Please provide channel ID!**\n\n"
            "**Usage:** `/set_channel -1001234567890`\n\n"
            "**How to get channel ID:**\n"
            "1. Add @MissRose_bot to your channel\n"
            "2. Send /id in channel\n"
            "3. Copy the channel ID",
            reply_markup=buttons
        )
    
    channel_id = message.text.split(" ", 1)[1]
    
    try:
        channel_id = int(channel_id)
    except:
        buttons = await back_button_only()
        return await message.reply_text("❌ Invalid channel ID! Must be a number.", reply_markup=buttons)
    
    # Get channel title for log
    channel_title = None
    try:
        chat = await bot.get_chat(channel_id)
        channel_title = chat.title
    except:
        pass
    
    # ✅ PEHLE OLD DATA DELETE KARO
    await chnl_ids.delete_many({"user_id": user_id})
    await chnl_ids.delete_many({"chnl_id": channel_id})
    
    # ✅ NAYA DATA ADD KARO
    await addCapByUser(user_id, channel_id, Rkn_Bots.DEF_CAP)
    await addCap(channel_id, Rkn_Bots.DEF_CAP)
    
    # 🟢 Log channel setup
    await logger.channel_setup(user_id, channel_id, channel_title)
    
    buttons = await main_menu_buttons()
    caption = await get_home_caption(user_id)
    
    await message.reply_photo(
        photo=Rkn_Bots.RKN_PIC,
        caption=caption,
        reply_markup=buttons
    )

# ==================== SET CAPTION ====================

@Client.on_message(filters.private & filters.command("set_caption"))
async def setCaption(bot, message):
    print("✅ /set_caption command triggered!")
    user_id = message.from_user.id
    logger = Logger(bot)
    
    try:
        await message.delete()
    except:
        pass
    
    if len(message.command) < 2:
        buttons = await caption_page_buttons()
        return await message.reply_text(
            "❌ **Please provide caption!**\n\n"
            "**Usage:** `/set_caption Your caption here {file_name}`\n\n"
            "**Example:** `/set_caption 📁 File: {file_name}\nJoin @wolverine273`\n\n"
            "**{file_name}** - Shows original file name",
            reply_markup=buttons
        )
    
    caption = message.text.split(" ", 1)[1]
    
    chkData = await getChannelDataByUser(user_id)
    
    if chkData:
        chnl_id = chkData.get("chnl_id")
        await updateCapByUser(user_id, caption)
        await updateCap(chnl_id, caption)
        
        # 🟢 Log caption set
        await logger.caption_set(user_id, chnl_id, caption)
        
        buttons = await caption_page_buttons()
        return await message.reply_text(
            f"✅ **Caption Updated Successfully!**\n\n"
            f"**Your New Caption:**\n`{caption}`",
            reply_markup=buttons
        )
    else:
        buttons = await back_button_only()
        return await message.reply_text(
            "❌ **No channel found!**\n\n"
            "Please set your channel ID first:\n"
            "`/set_channel -1001234567890`",
            reply_markup=buttons
        )

# ==================== SET BUTTONS ====================

@Client.on_message(filters.private & filters.command("set_buttons"))
async def setButtons(bot, message):
    print("✅ /set_buttons command triggered!")
    user_id = message.from_user.id
    logger = Logger(bot)
    
    try:
        await message.delete()
    except:
        pass
    
    chkData = await getChannelDataByUser(user_id)
    if not chkData:
        buttons = await back_button_only()
        return await message.reply_text(
            "❌ **No channel found!**\n\n"
            "Please set your channel ID first:\n"
            "`/set_channel -1001234567890`",
            reply_markup=buttons
        )
    
    if len(message.command) < 2:
        buttons = await button_page_buttons()
        return await message.reply_text(
            "❌ **Please provide buttons!**\n\n"
            "**Usage:** `/set_buttons [Text]:[URL] | [Text]:[URL]`\n"
            "**Example:** `/set_buttons 📢 Join:https://t.me/wolverine273`\n\n"
            "**Multiple Buttons:**\n"
            "`/set_buttons 📢 Channel:https://t.me/wolverine273 | 💬 Group:https://t.me/WOLVERIN_P`",
            reply_markup=buttons
        )
    
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
        buttons = await button_page_buttons()
        return await message.reply_text(
            "❌ **No valid buttons found!**\n\n"
            "**Format:** `[Text]:[URL]` separated by ` | `\n"
            "**Example:** `/set_buttons 📢 Join:https://t.me/wolverine273 | 💬 Group:https://t.me/WOLVERIN_P`",
            reply_markup=buttons
        )
    
    chnl_id = chkData.get("chnl_id")
    print(f"📌 Setting buttons for Channel: {chnl_id}")
    print(f"📌 Buttons: {len(buttons_data)} button(s)")
    
    await updateButtons(chnl_id, buttons_data)
    await updateButtonsByUser(user_id, buttons_data)
    
    # 🟢 Log buttons set
    await logger.buttons_set(user_id, chnl_id, len(buttons_data))
    
    verify_data = await getChannelData(chnl_id)
    saved_buttons = verify_data.get("buttons", [])
    print(f"✅ Verified: {len(saved_buttons)} buttons saved for channel {chnl_id}")
    
    preview = "\n".join([f"• {btn[0].text} → {btn[0].url}" for btn in buttons_data])
    
    buttons = await button_page_buttons()
    await message.reply_text(
        f"✅ **Buttons Set Successfully!**\n\n"
        f"📌 **Channel ID:** `{chnl_id}`\n"
        f"🔢 **Buttons Saved:** `{len(saved_buttons)}` button(s)\n\n"
        f"**Your Buttons:**\n{preview}\n\n"
        f"📌 Now post a file in this channel to see buttons!",
        reply_markup=types.InlineKeyboardMarkup(buttons_data)
    )

# ==================== DELETE CAPTION COMMAND ====================

@Client.on_message(filters.private & filters.command(["delcaption", "del_caption", "delete_caption"]))
async def delCaption(bot, message):
    print("✅ /delcaption command triggered!")
    user_id = message.from_user.id
    logger = Logger(bot)
    
    try:
        await message.delete()
    except:
        pass
    
    chkData = await getChannelDataByUser(user_id)
    if not chkData:
        buttons = await back_button_only()
        return await message.reply_text("❌ No data found for your channel!", reply_markup=buttons)
    
    chnl_id = chkData.get("chnl_id")
    await updateCapByUser(user_id, Rkn_Bots.DEF_CAP)
    await updateCap(chnl_id, Rkn_Bots.DEF_CAP)
    
    # 🟢 Log caption deleted
    await logger.caption_deleted(user_id, chnl_id)
    
    buttons = await back_button_only()
    await message.reply_text(
        "✅ **Caption Deleted Successfully!**\n"
        f"Now I will use default caption.",
        reply_markup=buttons
    )

# ==================== REMOVE BUTTONS COMMAND ====================

@Client.on_message(filters.private & filters.command("remove_buttons"))
async def removeButtons(bot, message):
    print("✅ /remove_buttons command triggered!")
    user_id = message.from_user.id
    logger = Logger(bot)
    
    try:
        await message.delete()
    except:
        pass
    
    chkData = await getChannelDataByUser(user_id)
    if not chkData:
        buttons = await back_button_only()
        return await message.reply_text("❌ No data found for your channel!", reply_markup=buttons)
    
    chnl_id = chkData.get("chnl_id")
    channel_data = await getChannelData(chnl_id)
    
    if not channel_data or "buttons" not in channel_data or not channel_data["buttons"]:
        buttons = await back_button_only()
        return await message.reply_text("❌ No buttons are currently set!", reply_markup=buttons)
    
    await deleteButtonsByUser(user_id)
    await deleteButtons(chnl_id)
    
    # 🟢 Log buttons removed
    await logger.buttons_removed(user_id, chnl_id)
    
    buttons = await back_button_only()
    await message.reply_text(
        "✅ **Buttons Removed Successfully!**\n"
        "Now no buttons will be shown with captions.",
        reply_markup=buttons
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
            "❌ **No settings found!**\n\n"
            "Please set your channel first:\n"
            "`/set_channel -1001234567890`",
            reply_markup=buttons
        )
    
    chnl_id = chkData.get("chnl_id")
    channel_data = await getChannelData(chnl_id)
    
    caption = channel_data.get("caption", "Not set") if channel_data else "Not set"
    buttons_data = channel_data.get("buttons", []) if channel_data else []
    
    btn_count = len(buttons_data)
    btn_preview = "\n".join([f"• {btn[0].text} → {btn[0].url}" for btn in buttons_data]) if buttons_data else "No buttons set"
    
    buttons = await back_button_only()
    await message.reply_text(
        f"**📊 Your Settings**\n\n"
        f"🔹 **Channel ID:** `{chnl_id}`\n\n"
        f"🔹 **Caption:**\n`{caption}`\n\n"
        f"🔹 **Buttons:** ({btn_count})\n{btn_preview}",
        reply_markup=buttons
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
        f"1️⃣ `/set_channel -1001234567890` - Set your channel ID\n"
        f"2️⃣ `/set_caption Your caption {{file_name}}` - Set caption\n"
        f"3️⃣ `/set_buttons Text:URL | Text:URL` - Set buttons\n\n"
        f"**📋 Commands:**\n"
        f"📌 `/set_channel` - Set channel ID\n"
        f"📝 `/set_caption` - Set caption\n"
        f"📎 `/set_buttons` - Set buttons\n"
        f"🗑️ `/remove_channel` - Remove channel\n"
        f"❌ `/delcaption` - Delete caption\n"
        f"🗑️ `/remove_buttons` - Remove buttons\n"
        f"📊 `/status` - Check settings\n\n"
        f"**📌 Variables in Caption:**\n"
        f"`{{file_name}}` - Original file name\n\n"
        f"**📌 Button Format:**\n"
        f"`[Text]:[URL]` separated by ` | `",
        reply_markup=buttons
    )

# ==================== AUTO EDIT CAPTION (CHANNEL) ====================

@Client.on_message(filters.channel)
async def auto_edit_caption(bot, message):
    chnl_id = message.chat.id
    print(f"📩 New message in channel: {chnl_id}")
    
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
        return
    
    if message.media:
        for file_type in ("video", "audio", "document", "voice"):
            obj = getattr(message, file_type, None)
            if obj and hasattr(obj, "file_name"):
                file_name = obj.file_name
                file_name = (
                    re.sub(r"@\w+\s*", "", file_name)
                    .replace("_", " ")
                    .replace(".", " ")
                )
                print(f"📁 File: {file_name}")
                
                try:
                    if cap_dets:
                        cap = cap_dets.get("caption", Rkn_Bots.DEF_CAP)
                        buttons = cap_dets.get("buttons", None)
                        
                        try:
                            replaced_caption = cap.format(file_name=file_name)
                        except KeyError:
                            replaced_caption = Rkn_Bots.DEF_CAP.format(file_name=file_name)
                        print(f"📝 New caption: {replaced_caption}")
                        
                        # 🟢 Log caption auto-edited
                        logger = Logger(bot)
                        await logger.caption_edited(chnl_id, message.id, file_name)
                        
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
                        replaced_caption = Rkn_Bots.DEF_CAP.format(file_name=file_name)
                        await message.edit(replaced_caption)
                        print("✅ Default caption edited!")
                        
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
    
    # 🟢 Log admin action
    logger = Logger(client)
    await logger.admin_action(
        admin_id=message.from_user.id,
        action="Checked Users",
        details=f"Total Users: {total_users}"
    )
    
    await rkn.edit(text=f"**--Bot Processed--** \n\n**Bot Started UpTime:** {uptime} \n**Bot Current Ping:** `{time_taken_s:.3f} ᴍꜱ` \n**All Bot Users:** `{total_users}`")

@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command(["broadcast"]))
async def broadcast(bot, message):
    logger = Logger(bot)
    
    if (message.reply_to_message):
        rkn = await message.reply_text("Bot Processing.\nI am checking all bot users.")
        all_users = await getid()
        tot = await total_user()
        success = 0
        failed = 0
        deactivated = 0
        blocked = 0
        
        # 🟢 Log broadcast started
        await logger.broadcast_started(message.from_user.id, tot)
        
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
        
        # 🟢 Log broadcast completed
        await logger.broadcast_completed(message.from_user.id, success, failed, blocked, deactivated, tot)
        
        await rkn.edit(f"<u>ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</u>\n\n• ᴛᴏᴛᴀʟ ᴜsᴇʀs: {tot}\n• sᴜᴄᴄᴇssғᴜʟ: {success}\n• ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs: {blocked}\n• ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs: {deactivated}\n• ᴜɴsᴜᴄᴄᴇssғᴜʟ: {failed}")

@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command("restart"))
async def restart_bot(b, m):
    logger = Logger(b)
    
    # 🟢 Log restart
    await logger.admin_action(
        admin_id=m.from_user.id,
        action="Bot Restart",
        details="Bot is restarting..."
    )
    
    rkn_msg = await b.send_message(text="**🔄 𝙿𝚁𝙾𝙲𝙴𝚂𝚂𝙴𝚂 𝚂𝚃𝙾𝙿𝙴𝙳. 𝙱𝙾𝚃 𝙸𝚂 𝚁𝙴𝚂𝚃𝙰𝚁𝚃𝙸𝙽𝙶...**", chat_id=m.chat.id)       
    await asyncio.sleep(3)
    await rkn_msg.edit("**✅️ 𝙱𝙾𝚃 𝙸𝚂 𝚁𝙴𝚂𝚃𝙰𝚁𝚃𝙴𝙳. 𝙽𝙾𝚆 𝚈𝙾𝚄 𝙲𝙰𝙽 𝚄𝚂𝙴 𝙼𝙴**")
    os.execl(sys.executable, sys.executable, *sys.argv)

@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command("reset_db"))
async def reset_db(bot, message):
    print("🔄 Resetting database...")
    user_id = message.from_user.id
    
    logger = Logger(bot)
    await logger.admin_action(
        admin_id=user_id,
        action="Database Reset",
        details="User data reset"
    )
    
    await resetUserData(user_id)
    await message.reply("✅ Database reset for your channel! Please set up again.\n\n`/set_channel -1001234567890`")

print("✅ Caption.py loaded successfully!")
