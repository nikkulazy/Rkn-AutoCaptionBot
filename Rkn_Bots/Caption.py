# (c) @RknDeveloperr
# Rkn Developer 
# Don't Remove Credit 😔
# Telegram Channel @RknDeveloper & @Rkn_Bots
# Developer @RknDeveloperr

from pyrogram import Client, filters, errors, types
from config import Rkn_Bots
import asyncio, re, time, sys, os
from .database import total_user, getid, delete, insert, chnl_ids
from .database import addCap, updateCap, updateButtons, deleteButtons, getChannelData
from .database import addCapByUser, updateCapByUser, updateButtonsByUser, deleteButtonsByUser, getChannelDataByUser
from pyrogram.errors import FloodWait

# ============ CHECK KAREN KE YE FUNCTION REGISTER HO RAHE HAIN ============
print("🔄 Loading Caption.py...")

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
    if (message.reply_to_message):
        rkn = await message.reply_text("Bot Processing.\nI am checking all bot users.")
        all_users = await getid()
        tot = await total_user()
        success = 0
        failed = 0
        deactivated = 0
        blocked = 0
        await rkn.edit(f"bot ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ started...")
        async for user in all_users:
            try:
                time.sleep(1)
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
        await rkn.edit(f"<u>ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</u>\n\n• ᴛᴏᴛᴀʟ ᴜsᴇʀs: {tot}\n• sᴜᴄᴄᴇssғᴜʟ: {success}\n• ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs: {blocked}\n• ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs: {deactivated}\n• ᴜɴsᴜᴄᴄᴇssғᴜʟ: {failed}")
        

# Restart to cancell all process 
@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command("restart"))
async def restart_bot(b, m):
    rkn_msg = await b.send_message(text="**🔄 𝙿𝚁𝙾𝙲𝙴𝚂𝚂𝙴𝚂 𝚂𝚃𝙾𝙿𝙴𝙳. 𝙱𝙾𝚃 𝙸𝚂 𝚁𝙴𝚂𝚃𝙰𝚁𝚃𝙸𝙽𝙶...**", chat_id=m.chat.id)       
    await asyncio.sleep(3)
    await rkn_msg.edit("**✅️ 𝙱𝙾𝚃 𝙸𝚂 𝚁𝙴𝚂𝚃𝙰𝚁𝚃𝙴𝙳. 𝙽𝙾𝚆 𝚈𝙾𝚄 𝙲𝙰𝙽 𝚄𝚂𝙴 𝙼𝙴**")
    os.execl(sys.executable, sys.executable, *sys.argv)


# ==================== START COMMAND ====================

@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(bot, message):
    print("✅ /start command triggered!")  # Debug log
    user_id = int(message.from_user.id)
    await insert(user_id)
    
    await message.reply_photo(
        photo=Rkn_Bots.RKN_PIC,
        caption=f"<b>Hey, {message.from_user.mention}\n\nI'm an auto-caption bot.\n\nUse these commands in bot (private):</b>\n\n"
        f"📌 `/set_channel -1001234567890` - Set channel ID\n"
        f"📝 `/set_caption Your caption {file_name}` - Set caption\n"
        f"📎 `/set_buttons [Text]:[URL] | [Text]:[URL]` - Set buttons\n"
        f"👁️ `/view_buttons` - View buttons\n"
        f"🗑️ `/remove_buttons` - Remove buttons\n"
        f"❌ `/delcaption` - Delete caption\n"
        f"📊 `/status` - Check settings",
        reply_markup=types.InlineKeyboardMarkup([
            [
                types.InlineKeyboardButton('📢 Main Channel', url='https://t.me/wolverine273'),
                types.InlineKeyboardButton('💬 Help Group', url='https://t.me/WOLVERIN_P')
            ]
        ])
    )


# ==================== SET CHANNEL ====================

@Client.on_message(filters.private & filters.command("set_channel"))
async def setChannel(bot, message):
    print("✅ /set_channel command triggered!")  # Debug log
    user_id = message.from_user.id
    
    if len(message.command) < 2:
        return await message.reply(
            "❌ **Please provide channel ID!**\n\n"
            "**Usage:** `/set_channel -1001234567890`\n\n"
            "**How to get channel ID:**\n"
            "1. Add @MissRose_bot to your channel\n"
            "2. Send /id in channel\n"
            "3. Copy the channel ID"
        )
    
    channel_id = message.text.split(" ", 1)[1]
    
    try:
        channel_id = int(channel_id)
    except:
        return await message.reply("❌ Invalid channel ID! Must be a number.")
    
    chkData = await getChannelDataByUser(user_id)
    
    if chkData:
        await chnl_ids.update_one({"user_id": user_id}, {"$set": {"chnl_id": channel_id}})
    else:
        await addCapByUser(user_id, channel_id, Rkn_Bots.DEF_CAP)
    
    await message.reply(
        f"✅ **Channel Set Successfully!**\n\n"
        f"**Channel ID:** `{channel_id}`\n\n"
        f"Now you can use:\n"
        f"• `/set_caption` - Set caption\n"
        f"• `/set_buttons` - Set buttons\n"
        f"• `/status` - View settings"
    )


# ==================== SET BUTTONS ====================

@Client.on_message(filters.private & filters.command("set_buttons"))
async def setButtons(bot, message):
    print("✅ /set_buttons command triggered!")  # Debug log
    user_id = message.from_user.id
    
    # Check if channel exists
    chkData = await getChannelDataByUser(user_id)
    if not chkData:
        return await message.reply(
            "❌ **No channel found!**\n\n"
            "Please set your channel ID first:\n"
            "`/set_channel -1001234567890`"
        )
    
    # Check if command has text
    if len(message.command) < 2:
        return await message.reply(
            "❌ **Please provide buttons!**\n\n"
            "**Usage:** `/set_buttons [Text]:[URL] | [Text]:[URL]`\n"
            "**Example:** `/set_buttons 📢 Join:https://t.me/wolverine273`"
        )
    
    buttons_text = message.text.split(" ", 1)[1]
    if not buttons_text:
        return await message.reply("❌ Please provide buttons data!")
    
    # Parse buttons
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
    
    if not buttons_data:
        return await message.reply(
            "❌ **No valid buttons found!**\n\n"
            "**Format:** `[Text]:[URL]` separated by ` | `\n"
            "**Example:** `/set_buttons 📢 Join:https://t.me/wolverine273`"
        )
    
    # Save buttons
    await updateButtonsByUser(user_id, buttons_data)
    
    # Preview
    preview = "\n".join([f"• {btn[0].text} → {btn[0].url}" for btn in buttons_data])
    
    await message.reply(
        f"✅ **Buttons Set Successfully!**\n\n"
        f"**Your Buttons:**\n{preview}\n\n"
        f"**Total:** `{len(buttons_data)}` button(s)",
        reply_markup=types.InlineKeyboardMarkup(buttons_data)
    )


# ==================== VIEW BUTTONS ====================

@Client.on_message(filters.private & filters.command("view_buttons"))
async def viewButtons(bot, message):
    print("✅ /view_buttons command triggered!")  # Debug log
    user_id = message.from_user.id
    
    chkData = await getChannelDataByUser(user_id)
    if not chkData or "buttons" not in chkData or not chkData["buttons"]:
        return await message.reply("❌ No buttons set for your channel!")
    
    buttons = chkData["buttons"]
    preview = "\n".join([f"• {btn[0].text} → {btn[0].url}" for btn in buttons])
    
    await message.reply(
        f"**📎 Your Current Buttons:**\n\n{preview}\n\n"
        f"**Total Buttons:** `{len(buttons)}`",
        reply_markup=types.InlineKeyboardMarkup(buttons)
    )


# ==================== REMOVE BUTTONS ====================

@Client.on_message(filters.private & filters.command("remove_buttons"))
async def removeButtons(bot, message):
    print("✅ /remove_buttons command triggered!")  # Debug log
    user_id = message.from_user.id
    
    chkData = await getChannelDataByUser(user_id)
    if not chkData:
        return await message.reply("❌ No data found for your channel!")
    
    if "buttons" not in chkData or not chkData["buttons"]:
        return await message.reply("❌ No buttons are currently set!")
    
    await deleteButtonsByUser(user_id)
    await message.reply(
        "✅ **Buttons Removed Successfully!**\n"
        "Now no buttons will be shown with captions."
    )


# ==================== DELETE CAPTION ====================

@Client.on_message(filters.private & filters.command(["delcaption", "del_caption", "delete_caption"]))
async def delCaption(bot, message):
    print("✅ /delcaption command triggered!")  # Debug log
    user_id = message.from_user.id
    
    chkData = await getChannelDataByUser(user_id)
    if not chkData:
        return await message.reply("❌ No data found for your channel!")
    
    await updateCapByUser(user_id, Rkn_Bots.DEF_CAP)
    await message.reply(
        "✅ **Caption Deleted Successfully!**\n"
        f"Now I will use default caption."
    )


# ==================== SET CAPTION ====================

@Client.on_message(filters.private & filters.command("set_caption"))
async def setCaption(bot, message):
    print("✅ /set_caption command triggered!")  # Debug log
    user_id = message.from_user.id
    
    if len(message.command) < 2:
        return await message.reply(
            "❌ **Please provide caption!**\n\n"
            "**Usage:** `/set_caption Your caption here {file_name}`\n\n"
            "**Example:** `/set_caption 📁 File: {file_name}\nJoin @wolverine273`"
        )
    
    caption = message.text.split(" ", 1)[1]
    
    chkData = await getChannelDataByUser(user_id)
    
    if chkData:
        await updateCapByUser(user_id, caption)
        return await message.reply(
            f"✅ **Caption Updated Successfully!**\n\n"
            f"**Your New Caption:**\n`{caption}`"
        )
    else:
        return await message.reply(
            "❌ **No channel found!**\n\n"
            "Please set your channel ID first:\n"
            "`/set_channel -1001234567890`"
        )


# ==================== STATUS ====================

@Client.on_message(filters.private & filters.command("status"))
async def status(bot, message):
    print("✅ /status command triggered!")  # Debug log
    user_id = message.from_user.id
    chkData = await getChannelDataByUser(user_id)
    
    if not chkData:
        return await message.reply(
            "❌ **No settings found!**\n\n"
            "Please set your channel first:\n"
            "`/set_channel -1001234567890`"
        )
    
    channel_id = chkData.get("chnl_id", "Not set")
    caption = chkData.get("caption", "Not set")
    buttons = chkData.get("buttons", [])
    
    btn_count = len(buttons)
    btn_preview = "\n".join([f"• {btn[0].text} → {btn[0].url}" for btn in buttons]) if buttons else "No buttons set"
    
    await message.reply(
        f"**📊 Your Settings**\n\n"
        f"🔹 **Channel ID:** `{channel_id}`\n"
        f"🔹 **Caption:**\n`{caption}`\n\n"
        f"🔹 **Buttons:** ({btn_count})\n{btn_preview}"
    )


# ==================== AUTO EDIT CAPTION (CHANNEL) ====================

@Client.on_message(filters.channel)
async def auto_edit_caption(bot, message):
    chnl_id = message.chat.id
    
    cap_dets = await chnl_ids.find_one({"chnl_id": chnl_id})
    
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
                try:
                    if cap_dets:
                        cap = cap_dets.get("caption", Rkn_Bots.DEF_CAP)
                        buttons = cap_dets.get("buttons", None)
                        replaced_caption = cap.format(file_name=file_name)
                        
                        if buttons:
                            button_list = []
                            for btn in buttons:
                                button_list.append(btn)
                            reply_markup = types.InlineKeyboardMarkup(button_list) if button_list else None
                            await message.edit(replaced_caption, reply_markup=reply_markup)
                        else:
                            await message.edit(replaced_caption)
                    else:
                        replaced_caption = Rkn_Bots.DEF_CAP.format(file_name=file_name)
                        await message.edit(replaced_caption)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    continue
                except Exception as e:
                    print(f"Error in auto_edit_caption: {e}")
                    continue
    return

print("✅ Caption.py loaded successfully!")
# Rkn Developer 
# Don't Remove Credit 😔
