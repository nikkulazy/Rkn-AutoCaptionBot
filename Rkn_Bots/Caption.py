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
    
@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(bot, message):
    user_id = int(message.from_user.id)
    await insert(user_id)
    await message.reply_photo(photo=Rkn_Bots.RKN_PIC,
        caption=f"<b>Hey, {message.from_user.mention}\n\nI'm an auto-caption bot. I automatically edit captions for videos, audio files, and documents posted on channels.\n\nuse <code>/set_caption</code> to set caption\nUse<code>/delcaption</code> To delete caption and set caption to default.\n\nNote:All commands works on channels only</b>",
        reply_markup=types.InlineKeyboardMarkup([[
            types.InlineKeyboardButton('Main Channel', url='https://t.me/wolverine273'),
            types.InlineKeyboardButton('Help Group', url='https://t.me/WOLVERIN_P')
            ],[
            types.InlineKeyboardButton('♻️ MOVIE GROUP ♻️', url= 'https://t.me/thinkfilmy')
    ]]))
    

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
        # If no buttons provided, show guide with "Add Buttons" button
        return await message.reply(
            "**❌ No buttons provided!**\n\n"
            "**Usage:**\n"
            "`/set_buttons [text]:[url] | [text]:[url]`\n\n"
            "**Example:**\n"
            "`/set_buttons 📢 Channel:https://t.me/wolverine273 | 💬 Group:https://t.me/WOLVERIN_P`\n\n"
            "**To remove all buttons:**\n"
            "`/remove_buttons`\n\n"
            "**📌 Click below to learn how to add buttons:**",
            reply_markup=types.InlineKeyboardMarkup([[
                types.InlineKeyboardButton("➕ Add Buttons Guide", callback_data="add_buttons_guide")
            ]])
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
        # Update existing
        await updateButtons(chnl_id, buttons_data)
    else:
        # Create new with default caption
        await addCap(chnl_id, Rkn_Bots.DEF_CAP, buttons_data)
    
    # Preview buttons
    preview = "\n".join([f"• {btn[0].text} → {btn[0].url}" for btn in buttons_data])
    
    await message.reply(
        f"✅ **Buttons set successfully!**\n\n"
        f"**Your Buttons:**\n{preview}\n\n"
        f"**Total Buttons:** `{len(buttons_data)}`\n\n"
        f"**To remove buttons:** `/remove_buttons`\n"
        f"**To view buttons:** `/view_buttons`",
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


# ==================== CALLBACK QUERY HANDLER ====================

@Client.on_callback_query()
async def callback_handler(bot, callback_query):
    data = callback_query.data
    
    if data == "add_buttons_guide":
        # Send guide on how to add buttons in caption
        guide_text = """
**📌 How to Add Buttons in Caption**

**Step 1:** Use `/set_buttons` command in your channel.

**Step 2:** Format:
