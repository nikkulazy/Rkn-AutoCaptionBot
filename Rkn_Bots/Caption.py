from pyrogram import Client, filters, errors, types, enums
from config import Rkn_Bots
import asyncio, re, time, sys, os
from .database import total_user, getid, delete, insert, chnl_ids, users
from .database import addCap, updateCap, updateButtons, deleteButtons, getChannelData
from .database import addCapByUser, updateCapByUser, updateButtonsByUser, deleteButtonsByUser, getChannelDataByUser
from .database import resetChannelData, resetUserData
from pyrogram.errors import FloodWait

print("🔄 Loading Caption.py...")

# ==================== MAIN MENU BUTTONS ====================

async def main_menu_buttons():
    buttons = types.InlineKeyboardMarkup([
        [
            types.InlineKeyboardButton("📝 Set Caption", callback_data="set_caption"),
            types.InlineKeyboardButton("📎 Add Button", callback_data="add_button")
        ], 
        [
            types.InlineKeyboardButton("📊 My Status", callback_data="my_status"),
            types.InlineKeyboardButton("❌ Reset Data", callback_data="reset_data")
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

# ==================== GET HOME CAPTION ====================

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

# ==================== CHECK BOT ADMIN ====================

async def check_bot_admin(bot, channel_id):
    try:
        chat_member = await bot.get_chat_member(channel_id, (await bot.get_me()).id)
        if chat_member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            return True
        return False
    except Exception as e:
        print(f"❌ Bot admin check failed: {e}")
        return False

# ==================== AUTO SET CHANNEL ====================

async def auto_set_channel(bot, message):
    channel_id = message.chat.id
    
    is_admin = await check_bot_admin(bot, channel_id)
    if not is_admin:
        await message.reply_text(
            f"❌ **I'm not admin in this channel!**\n\n"
            f"Please add me as admin in this channel first."
        )
        return None
    
    user_id = None
    try:
        admins = await bot.get_chat_members(channel_id, filter=enums.ChatMembersFilter.ADMINISTRATORS)
        async for admin in admins:
            if admin.user and not admin.user.is_bot:
                user_id = admin.user.id
                break
    except:
        pass
    
    if not user_id:
        user_id = channel_id
    
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
    
    await message.reply_text(
        f"✅ **Channel Set Successfully!**\n\n"
        f"**Channel ID:** `{channel_id}`\n"
        f"**Channel Name:** {channel_title or 'Unknown'}\n\n"
        f"Now you can use:\n"
        f"• `/set_caption` - Set your caption\n"
        f"• `/set_buttons` - Set your buttons\n"
        f"• `/delcaption` - Delete caption\n"
        f"• `/remove_buttons` - Remove buttons"
    )
    return channel_id

# ==================== START COMMAND ====================

@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(bot, message):
    print("✅ /start command triggered!")
    user_id = int(message.from_user.id)
    first_name = message.from_user.first_name or "User"
    
    user_exists = await users.find_one({"_id": user_id})
    if not user_exists:
        await insert(user_id)
    
    buttons = await main_menu_buttons()
    caption = await get_home_caption(user_id, first_name)
    
    await message.reply_photo(
        photo=Rkn_Bots.RKN_PIC,
        caption=caption,
        reply_markup=buttons
    )

# ==================== CALLBACK HANDLER ====================

@Client.on_callback_query()
async def callback_handler(bot, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data
    first_name = callback_query.from_user.first_name or "User"
    
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
        except:
            await callback_query.message.reply_text(caption, reply_markup=buttons)
        await callback_query.answer()
        return
    
    elif data == "my_status":
        chkData = await getChannelDataByUser(user_id)
        if not chkData:
            await callback_query.message.reply_text(
                f"❌ **No settings found!**\n\n"
                f"Send `/set_caption` in your channel to connect.",
                reply_markup=await back_button_only()
            )
            await callback_query.answer()
            return
        
        chnl_id = chkData.get("chnl_id")
        channel_data = await getChannelData(chnl_id)
        caption = channel_data.get("caption", "Not set") if channel_data else "Not set"
        buttons_data = channel_data.get("buttons", []) if channel_data else []
        btn_count = len(buttons_data)
        btn_preview = "\n".join([f"• {btn[0].text} → {btn[0].url}" for btn in buttons_data]) if buttons_data else "No buttons set"
        
        await callback_query.message.reply_text(
            f"**📊 Your Settings**\n\n"
            f"🔹 **Channel ID:** `{chnl_id}`\n\n"
            f"🔹 **Caption:**\n`{caption}`\n\n"
            f"🔹 **Buttons:** ({btn_count})\n{btn_preview}",
            reply_markup=await back_button_only()
        )
        await callback_query.answer()
    
    elif data == "reset_data":
        await resetUserData(user_id)
        await callback_query.message.reply_text(
            f"✅ **Data Reset Successfully!**\n\n"
            f"Your channel data has been cleared.\n"
            f"Send `/set_caption` in your channel to set up again.",
            reply_markup=await back_button_only()
        )
        await callback_query.answer()
    
    elif data == "set_caption":
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
            reply_markup=await back_button_only()
        )
        await callback_query.answer()
    
    elif data == "add_button":
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
            reply_markup=await back_button_only()
        )
        await callback_query.answer()

# ==================== SET CAPTION ====================

@Client.on_message(filters.command("set_caption") & (filters.channel | filters.private))
async def setCaption(bot, message):
    print("✅ /set_caption command triggered!")
    
    if message.chat.type == enums.ChatType.PRIVATE:
        await message.reply_text(
            f"❌ **Please use this command in your channel!**\n\n"
            f"📌 **How to use:**\n"
            f"1. Add me as admin in your channel\n"
            f"2. Go to your channel\n"
            f"3. Send: `/set_caption Your caption here {{file_name}}`",
            reply_markup=await back_button_only()
        )
        return
    
    try:
        await message.delete()
    except:
        pass
    
    channel_id = await auto_set_channel(bot, message)
    if channel_id is None:
        return
    
    if len(message.command) < 2:
        await message.reply_text(
            f"❌ **Please provide caption!**\n\n"
            f"**Usage:** `/set_caption Your caption here {{file_name}}`\n\n"
            f"**Example:** `/set_caption 📁 File: {{file_name}}\nJoin @wolverine273`"
        )
        return
    
    caption = message.text.split(" ", 1)[1]
    
    user_id = None
    try:
        admins = await bot.get_chat_members(channel_id, filter=enums.ChatMembersFilter.ADMINISTRATORS)
        async for admin in admins:
            if admin.user and not admin.user.is_bot:
                user_id = admin.user.id
                break
    except:
        pass
    if not user_id:
        user_id = channel_id
    
    await updateCapByUser(user_id, caption)
    await updateCap(channel_id, caption)
    
    await message.reply_text(
        f"✅ **Caption Updated Successfully!**\n\n"
        f"**Channel ID:** `{channel_id}`\n\n"
        f"**Your New Caption:**\n`{caption}`"
    )

# ==================== SET BUTTONS ====================

@Client.on_message(filters.command("set_buttons") & (filters.channel | filters.private))
async def setButtons(bot, message):
    print("✅ /set_buttons command triggered!")
    
    if message.chat.type == enums.ChatType.PRIVATE:
        await message.reply_text(
            f"❌ **Please use this command in your channel!**\n\n"
            f"📌 **How to use:**\n"
            f"1. Add me as admin in your channel\n"
            f"2. Go to your channel\n"
            f"3. Send: `/set_buttons [Text]:[URL] | [Text]:[URL]`",
            reply_markup=await back_button_only()
        )
        return
    
    try:
        await message.delete()
    except:
        pass
    
    channel_id = await auto_set_channel(bot, message)
    if channel_id is None:
        return
    
    if len(message.command) < 2:
        await message.reply_text(
            f"❌ **Please provide buttons!**\n\n"
            f"**Usage:** `/set_buttons [Text]:[URL] | [Text]:[URL]`\n"
            f"**Example:** `/set_buttons 📢 Join:https://t.me/wolverine273`"
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
                if text and url and url.startswith(("https://", "http://", "t.me/")):
                    buttons_data.append([types.InlineKeyboardButton(text, url=url)])
    
    if not buttons_data:
        return await message.reply_text(
            f"❌ **No valid buttons found!**\n\n"
            f"**Format:** `[Text]:[URL]` separated by ` | `"
        )
    
    user_id = None
    try:
        admins = await bot.get_chat_members(channel_id, filter=enums.ChatMembersFilter.ADMINISTRATORS)
        async for admin in admins:
            if admin.user and not admin.user.is_bot:
                user_id = admin.user.id
                break
    except:
        pass
    if not user_id:
        user_id = channel_id
    
    await updateButtons(channel_id, buttons_data)
    await updateButtonsByUser(user_id, buttons_data)
    
    preview = "\n".join([f"• {btn[0].text} → {btn[0].url}" for btn in buttons_data])
    
    await message.reply_text(
        f"✅ **Buttons Set Successfully!**\n\n"
        f"📌 **Channel ID:** `{channel_id}`\n"
        f"🔢 **Buttons Saved:** `{len(buttons_data)}`\n\n"
        f"**Your Buttons:**\n{preview}\n\n"
        f"📌 Now post a file in this channel to see buttons!",
        reply_markup=types.InlineKeyboardMarkup(buttons_data)
    )

# ==================== DELETE CAPTION ====================

@Client.on_message(filters.command(["delcaption", "del_caption", "delete_caption"]) & (filters.channel | filters.private))
async def delCaption(bot, message):
    print("✅ /delcaption command triggered!")
    
    if message.chat.type == enums.ChatType.PRIVATE:
        await message.reply_text(
            f"❌ **Please use this command in your channel!**",
            reply_markup=await back_button_only()
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
    try:
        admins = await bot.get_chat_members(channel_id, filter=enums.ChatMembersFilter.ADMINISTRATORS)
        async for admin in admins:
            if admin.user and not admin.user.is_bot:
                user_id = admin.user.id
                break
    except:
        pass
    if not user_id:
        user_id = channel_id
    
    await updateCapByUser(user_id, Rkn_Bots.DEF_CAP)
    await updateCap(channel_id, Rkn_Bots.DEF_CAP)
    
    await message.reply_text(
        f"✅ **Caption Deleted Successfully!**\n\n"
        f"**Channel ID:** `{channel_id}`\n"
        f"Now using default caption."
    )

# ==================== REMOVE BUTTONS ====================

@Client.on_message(filters.command("remove_buttons") & (filters.channel | filters.private))
async def removeButtons(bot, message):
    print("✅ /remove_buttons command triggered!")
    
    if message.chat.type == enums.ChatType.PRIVATE:
        await message.reply_text(
            f"❌ **Please use this command in your channel!**",
            reply_markup=await back_button_only()
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
    try:
        admins = await bot.get_chat_members(channel_id, filter=enums.ChatMembersFilter.ADMINISTRATORS)
        async for admin in admins:
            if admin.user and not admin.user.is_bot:
                user_id = admin.user.id
                break
    except:
        pass
    if not user_id:
        user_id = channel_id
    
    await deleteButtonsByUser(user_id)
    await deleteButtons(channel_id)
    
    await message.reply_text(
        f"✅ **Buttons Removed Successfully!**\n\n"
        f"**Channel ID:** `{channel_id}`\n"
        f"No buttons will be shown now."
    )

# ==================== AUTO EDIT CAPTION ====================

@Client.on_message(filters.channel)
async def auto_edit_caption(bot, message):
    chnl_id = message.chat.id
    print(f"📩 New message in channel: {chnl_id}")
    
    cap_dets = await getChannelData(chnl_id)
    
    if not cap_dets:
        print("❌ No data found for channel")
        return
    
    if not message.media:
        return
    
    for file_type in ("video", "audio", "document", "voice", "photo"):
        obj = getattr(message, file_type, None)
        if obj:
            file_name = None
            if hasattr(obj, "file_name"):
                file_name = obj.file_name
                file_name_clean = re.sub(r"@\w+\s*", "", file_name).replace("_", " ").replace(".", " ")
            elif file_type == "photo":
                file_name_clean = f"Photo_{message.id}.jpg"
            else:
                file_name_clean = "Unknown_File"
            
            print(f"📁 File: {file_name_clean}")
            
            try:
                cap = cap_dets.get("caption", Rkn_Bots.DEF_CAP)
                buttons = cap_dets.get("buttons", [])
                
                try:
                    replaced_caption = cap.format(file_name=file_name_clean)
                except KeyError:
                    replaced_caption = Rkn_Bots.DEF_CAP.format(file_name=file_name_clean)
                
                if buttons and len(buttons) > 0:
                    reply_markup = types.InlineKeyboardMarkup(buttons)
                    await message.edit(replaced_caption, reply_markup=reply_markup)
                    print("✅ Caption and buttons edited!")
                else:
                    await message.edit(replaced_caption)
                    print("✅ Caption edited!")
                    
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except Exception as e:
                if "MESSAGE_NOT_MODIFIED" not in str(e):
                    print(f"❌ Error: {e}")
            break

# ==================== STATUS COMMAND ====================

@Client.on_message(filters.private & filters.command("status"))
async def status_cmd(bot, message):
    print("✅ /status command triggered!")
    user_id = message.from_user.id
    
    chkData = await getChannelDataByUser(user_id)
    if not chkData:
        await message.reply_text(
            f"❌ **No settings found!**\n\n"
            f"Send `/set_caption` in your channel to set up.",
            reply_markup=await back_button_only()
        )
        return
    
    chnl_id = chkData.get("chnl_id")
    channel_data = await getChannelData(chnl_id)
    caption = channel_data.get("caption", "Not set") if channel_data else "Not set"
    buttons_data = channel_data.get("buttons", []) if channel_data else []
    btn_count = len(buttons_data)
    btn_preview = "\n".join([f"• {btn[0].text} → {btn[0].url}" for btn in buttons_data]) if buttons_data else "No buttons set"
    
    await message.reply_text(
        f"**📊 Your Settings**\n\n"
        f"🔹 **Channel ID:** `{chnl_id}`\n\n"
        f"🔹 **Caption:**\n`{caption}`\n\n"
        f"🔹 **Buttons:** ({btn_count})\n{btn_preview}",
        reply_markup=await back_button_only()
    )

# ==================== HELP COMMAND ====================

@Client.on_message(filters.private & filters.command("help"))
async def help_cmd(bot, message):
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
        f"📊 `/status` - Check settings\n"
        f"📢 `/help` - Show this help\n\n"
        f"**📌 Variables in Caption:**\n"
        f"`{{file_name}}` - Original file name\n\n"
        f"**📌 Button Format:**\n"
        f"`[Text]:[URL]` separated by ` | `",
        reply_markup=await main_menu_buttons()
    )

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
    if message.reply_to_message:
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
                await asyncio.sleep(1)
                await message.reply_to_message.copy(user['_id'])
                success += 1
            except errors.InputUserDeactivated:
                deactivated += 1
                await delete({"_id": user['_id']})
            except errors.UserIsBlocked:
                blocked += 1
                await delete({"_id": user['_id']})
            except Exception as e:
                failed += 1
                await delete({"_id": user['_id']})
            try:
                await rkn.edit(f"<u>ʙʀᴏᴀᴅᴄᴀsᴛ ᴘʀᴏᴄᴇssɪɴɢ</u>\n\n• ᴛᴏᴛᴀʟ ᴜsᴇʀs: {tot}\n• sᴜᴄᴄᴇssғᴜʟ: {success}\n• ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs: {blocked}\n• ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs: {deactivated}\n• ᴜɴsᴜᴄᴄᴇssғᴜʟ: {failed}")
            except FloodWait as e:
                await asyncio.sleep(e.x)
        
        await rkn.edit(f"<u>ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</u>\n\n• ᴛᴏᴛᴀʟ ᴜsᴇʀs: {tot}\n• sᴜᴄᴄᴇssғᴜʟ: {success}\n• ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs: {blocked}\n• ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs: {deactivated}\n• ᴜɴsᴜᴄᴄᴇssғᴜʟ: {failed}")

@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command("restart"))
async def restart_bot(b, m):
    rkn_msg = await b.send_message(text="**🔄 𝙿𝚁𝙾𝙲𝙴𝚂𝚂𝙴𝚂 𝚂𝚃𝙾𝙿𝙴𝙳. 𝙱𝙾𝚃 𝙸𝚂 𝚁𝙴𝚂𝚃𝙰𝚁𝚃𝙸𝙽𝙶...**", chat_id=m.chat.id)       
    await asyncio.sleep(3)
    await rkn_msg.edit("**✅️ 𝙱𝙾𝚃 𝙸𝚂 𝚁𝙴𝚂𝚃𝙰𝚁𝚃𝙴𝙳. 𝙽𝙾𝚆 𝚈𝙾𝚄 𝙲𝙰𝙽 𝚄𝚂𝙴 𝙼𝙴**")
    os.execl(sys.executable, sys.executable, *sys.argv)

@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command("reset_db"))
async def reset_db(bot, message):
    user_id = message.from_user.id
    await resetUserData(user_id)
    await message.reply("✅ Database reset for your channel! Please set up again.")

print("✅ Caption.py loaded successfully!")
