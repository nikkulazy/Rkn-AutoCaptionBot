# (c) @RknDeveloperr
# Rkn Developer 
# Don't Remove Credit 😔
# Telegram Channel @RknDeveloper & @Rkn_Bots
# Developer @RknDeveloperr

from pyrogram import Client, filters, errors, types
from config import Rkn_Bots
import asyncio, re, time, sys, os
from .database import total_user, getid, delete, addCap, updateCap, insert, chnl_ids, updateButtons, deleteButtons, getChannelData
from pyrogram.errors import FloodWait

@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN)  & filters.command(["rknusers"]))
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
    user_id = int(message.from_user.id)
    await insert(user_id)
    
    # User ko buttons ke saath welcome message
    await message.reply_photo(
        photo=Rkn_Bots.RKN_PIC,
        caption=f"<b>Hey, {message.from_user.mention}\n\nI'm an auto-caption bot. I automatically edit captions for videos, audio files, and documents posted on channels.\n\nSelect an option below:</b>",
        reply_markup=types.InlineKeyboardMarkup([
            [
                types.InlineKeyboardButton('📝 Set Caption', callback_data="set_caption_guide"),
                types.InlineKeyboardButton('📎 Set Buttons', callback_data="set_buttons_guide")
            ],
            [
                types.InlineKeyboardButton('❌ Delete Caption', callback_data="del_caption_guide"),
                types.InlineKeyboardButton('🗑️ Remove Buttons', callback_data="remove_buttons_guide")
            ],
            [
                types.InlineKeyboardButton('👁️ View Buttons', callback_data="view_buttons_guide"),
                types.InlineKeyboardButton('📊 Status', callback_data="status_check")
            ],
            [
                types.InlineKeyboardButton('📢 Main Channel', url='https://t.me/wolverine273'),
                types.InlineKeyboardButton('💬 Help Group', url='https://t.me/WOLVERIN_P')
            ],
            [
                types.InlineKeyboardButton('♻️ MOVIE GROUP ♻️', url='https://t.me/thinkfilmy')
            ]
        ])
    )


# ==================== CALLBACK QUERY HANDLER ====================

@Client.on_callback_query()
async def callback_handler(bot, callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # ============ SET CAPTION GUIDE ============
    if data == "set_caption_guide":
        await callback_query.message.edit(
            "**📝 How to Set Caption**\n\n"
            "1️⃣ Add bot as admin in your channel\n"
            "2️⃣ Send this command in your channel:\n"
            "`/set_caption Your caption here {file_name}`\n\n"
            "**Example:**\n"
            "`/set_caption 📁 File: {file_name}\nJoin @wolverine273`\n\n"
            "**{file_name}** - Shows original file name\n\n"
            "🔄 **To update caption:** Send command again\n"
            "❌ **To delete:** Click 'Delete Caption' button",
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
            ])
        )
        await callback_query.answer()
    
    # ============ SET BUTTONS GUIDE ============
    elif data == "set_buttons_guide":
        await callback_query.message.edit(
            "**📎 How to Set Buttons**\n\n"
            "1️⃣ Add bot as admin in your channel\n"
            "2️⃣ Send this command in your channel:\n"
            "`/set_buttons [Text]:[URL] | [Text]:[URL]`\n\n"
            "**Examples:**\n\n"
            "🔹 **Single Button:**\n"
            "`/set_buttons 📢 Join:https://t.me/wolverine273`\n\n"
            "🔹 **Multiple Buttons:**\n"
            "`/set_buttons 📢 Channel:https://t.me/wolverine273 | 💬 Group:https://t.me/WOLVERIN_P | 🎬 Movies:https://t.me/thinkfilmy`\n\n"
            "🔹 **t.me link:**\n"
            "`/set_buttons Support:https://t.me/WOLVERIN_P`\n\n"
            "⚠️ Use `|` to separate multiple buttons\n"
            "⚠️ URL must start with https:// or http://",
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
            ])
        )
        await callback_query.answer()
    
    # ============ DELETE CAPTION GUIDE ============
    elif data == "del_caption_guide":
        await callback_query.message.edit(
            "**❌ How to Delete Caption**\n\n"
            "1️⃣ Add bot as admin in your channel\n"
            "2️⃣ Send this command in your channel:\n"
            "`/delcaption` or `/delete_caption`\n\n"
            "✅ After this, bot will use default caption\n\n"
            "📌 **Default Caption:**\n"
            f"`{Rkn_Bots.DEF_CAP}`",
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
            ])
        )
        await callback_query.answer()
    
    # ============ REMOVE BUTTONS GUIDE ============
    elif data == "remove_buttons_guide":
        await callback_query.message.edit(
            "**🗑️ How to Remove Buttons**\n\n"
            "1️⃣ Add bot as admin in your channel\n"
            "2️⃣ Send this command in your channel:\n"
            "`/remove_buttons`\n\n"
            "✅ All buttons will be removed from captions",
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
            ])
        )
        await callback_query.answer()
    
    # ============ VIEW BUTTONS GUIDE ============
    elif data == "view_buttons_guide":
        await callback_query.message.edit(
            "**👁️ How to View Buttons**\n\n"
            "1️⃣ Add bot as admin in your channel\n"
            "2️⃣ Send this command in your channel:\n"
            "`/view_buttons`\n\n"
            "📌 Bot will show all currently set buttons",
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
            ])
        )
        await callback_query.answer()
    
    # ============ STATUS CHECK ============
    elif data == "status_check":
        total_users = await total_user()
        uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(time.time() - bot.uptime))
        start_t = time.time()
        end_t = time.time()
        ping = (end_t - start_t) * 1000
        
        await callback_query.message.edit(
            f"**📊 Bot Status**\n\n"
            f"🟢 **Status:** Online\n"
            f"⏱️ **Uptime:** {uptime}\n"
            f"📡 **Ping:** `{ping:.2f}ms`\n"
            f"👥 **Total Users:** `{total_users}`\n\n"
            f"🤖 **Bot:** @{bot.me.username}",
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
            ])
        )
        await callback_query.answer()
    
    # ============ BACK TO START ============
    elif data == "back_to_start":
        await callback_query.message.edit(
            f"<b>Hey, {callback_query.from_user.mention}\n\nI'm an auto-caption bot. I automatically edit captions for videos, audio files, and documents posted on channels.\n\nSelect an option below:</b>",
            reply_markup=types.InlineKeyboardMarkup([
                [
                    types.InlineKeyboardButton('📝 Set Caption', callback_data="set_caption_guide"),
                    types.InlineKeyboardButton('📎 Set Buttons', callback_data="set_buttons_guide")
                ],
                [
                    types.InlineKeyboardButton('❌ Delete Caption', callback_data="del_caption_guide"),
                    types.InlineKeyboardButton('🗑️ Remove Buttons', callback_data="remove_buttons_guide")
                ],
                [
                    types.InlineKeyboardButton('👁️ View Buttons', callback_data="view_buttons_guide"),
                    types.InlineKeyboardButton('📊 Status', callback_data="status_check")
                ],
                [
                    types.InlineKeyboardButton('📢 Main Channel', url='https://t.me/wolverine273'),
                    types.InlineKeyboardButton('💬 Help Group', url='https://t.me/WOLVERIN_P')
                ],
                [
                    types.InlineKeyboardButton('♻️ MOVIE GROUP ♻️', url='https://t.me/thinkfilmy')
                ]
            ])
        )
        await callback_query.answer()


# ==================== CHANNEL COMMANDS ====================

# this command works on channels only 
@Client.on_message(filters.command("set_caption") & filters.channel)
async def setCaption(bot, message):
    if len(message.command) < 2:
        return await message.reply(
            "Exam.: /set_caption <code> set your caption ( use {file_name} to show file name</code>)"
        )
    chnl_id = message.chat.id
    caption = (
        message.text.split(" ", 1)[1] if len(message.text.split(" ", 1)) > 1 else None
    )
    chkData = await chnl_ids.find_one({"chnl_id": chnl_id})
    if chkData:
        await updateCap(chnl_id, caption)
        return await message.reply(f"Successfully Updated Your Caption.\n\nYour New Caption: `{caption}`")
    else:
        await addCap(chnl_id, caption)
        return await message.reply(f"Successfully Updated Your Caption.\n\nYour New Caption: `{caption}`")


# this command works on channels only 
@Client.on_message(filters.command(["delcaption", "del_caption", "delete_caption"]) & filters.channel)
async def delCaption(_, msg):
    chnl_id = msg.chat.id
    try:
        await chnl_ids.delete_one({"chnl_id": chnl_id})
        return await msg.reply("<b>Successfully deleted your caption..From now i will use my default caption</b>")
    except Exception as e:
        rkn = await msg.reply(f"Error: {e}")
        await asyncio.sleep(5)
        await rkn.delete()
        return


# ==================== /set_buttons COMMAND ====================

@Client.on_message(filters.command("set_buttons") & filters.channel)
async def setButtons(bot, message):
    chnl_id = message.chat.id
    
    if len(message.command) < 2:
        return await message.reply(
            "**❌ No buttons provided!**\n\n"
            "**Usage:**\n"
            "`/set_buttons [text]:[url] | [text]:[url]`\n\n"
            "**Example:**\n"
            "`/set_buttons 📢 Channel:https://t.me/wolverine273 | 💬 Group:https://t.me/WOLVERIN_P`\n\n"
            "**To remove all buttons:**\n"
            "`/remove_buttons`"
        )
    
    # Parse buttons from command
    buttons_text = message.text.split(" ", 1)[1] if len(message.text.split(" ", 1)) > 1 else ""
    
    if not buttons_text:
        return await message.reply("❌ Please provide buttons data!")
    
    # Parse buttons: text:url | text:url
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
                        return await message.reply(f"❌ Invalid URL: `{url}`\nURL must start with https://, http://, or t.me/")
    
    if not buttons_data:
        return await message.reply("❌ No valid buttons found!\n\nFormat: `[text]:[url] | [text]:[url]`")
    
    # Check channel data
    chkData = await chnl_ids.find_one({"chnl_id": chnl_id})
    
    if chkData:
        await updateButtons(chnl_id, buttons_data)
    else:
        await addCap(chnl_id, Rkn_Bots.DEF_CAP, buttons_data)
    
    # Preview buttons
    preview = "\n".join([f"• {btn[0].text} → {btn[0].url}" for btn in buttons_data])
    
    await message.reply(
        f"✅ **Buttons set successfully!**\n\n"
        f"**Your Buttons:**\n{preview}\n\n"
        f"**Total Buttons:** `{len(buttons_data)}`\n\n"
        f"**To remove buttons:** `/remove_buttons`",
        reply_markup=types.InlineKeyboardMarkup(buttons_data)
    )


@Client.on_message(filters.command("remove_buttons") & filters.channel)
async def removeButtons(bot, message):
    chnl_id = message.chat.id
    
    chkData = await chnl_ids.find_one({"chnl_id": chnl_id})
    if not chkData:
        return await message.reply("❌ No data found for this channel!")
    
    if "buttons" not in chkData or not chkData["buttons"]:
        return await message.reply("❌ No buttons are currently set!")
    
    await deleteButtons(chnl_id)
    await message.reply(
        "✅ **Buttons removed successfully!**\n"
        "Now no buttons will be shown with captions."
    )


@Client.on_message(filters.command("view_buttons") & filters.channel)
async def viewButtons(bot, message):
    chnl_id = message.chat.id
    
    chkData = await chnl_ids.find_one({"chnl_id": chnl_id})
    if not chkData or "buttons" not in chkData or not chkData["buttons"]:
        return await message.reply("❌ No buttons set for this channel!")
    
    buttons = chkData["buttons"]
    preview = "\n".join([f"• {btn[0].text} → {btn[0].url}" for btn in buttons])
    
    await message.reply(
        f"**📎 Your Current Buttons:**\n\n{preview}\n\n"
        f"**Total Buttons:** `{len(buttons)}`",
        reply_markup=types.InlineKeyboardMarkup(buttons)
    )


# ==================== AUTO EDIT CAPTION ====================

@Client.on_message(filters.channel)
async def auto_edit_caption(bot, message):
    chnl_id = message.chat.id
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
                cap_dets = await chnl_ids.find_one({"chnl_id": chnl_id})
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

# Rkn Developer 
# Don't Remove Credit 😔
# Telegram Channel @RknDeveloper & @Rkn_Bots
# Developer @RknDeveloperr
