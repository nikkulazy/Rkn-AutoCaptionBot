from pyrogram import Client, filters, enums 
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserNotParticipant
from config import Rkn_Bots as Config
from .database import insert

# ✅ Custom Style Class - Pyrofork ke liye
class KeyboardButtonStyle:
    def __init__(self, bg_primary=False, bg_danger=False, bg_success=False):
        self.bg_primary = bg_primary
        self.bg_danger = bg_danger
        self.bg_success = bg_success

def create_styled_button(text, url=None, callback_data=None, style_type="primary"):
    """Create a styled button for Pyrofork"""
    if style_type == "primary":
        style = KeyboardButtonStyle(bg_primary=True)
    elif style_type == "danger":
        style = KeyboardButtonStyle(bg_danger=True)
    elif style_type == "success":
        style = KeyboardButtonStyle(bg_success=True)
    else:
        style = KeyboardButtonStyle(bg_primary=True)
    
    if callback_data:
        btn = InlineKeyboardButton(text=text, callback_data=callback_data)
    elif url:
        btn = InlineKeyboardButton(text=text, url=url)
    else:
        btn = InlineKeyboardButton(text=text)
    
    # Style ko button mein store karein
    btn.style = style
    return btn

async def not_subscribed(_, client, message):
    user_id = int(message.from_user.id)
    await insert(user_id)
    if not Config.FORCE_SUB:
        return False
    try:             
        user = await client.get_chat_member(Config.FORCE_SUB, message.from_user.id) 
        if user.status == enums.ChatMemberStatus.BANNED:
            return True 
        else:
            return False                
    except UserNotParticipant:
        pass
    return True


@Client.on_message(filters.private & filters.create(not_subscribed))
async def forces_sub(client, message):
    buttons = [[
        create_styled_button(
            "📢 Join Update Channel 📢", 
            url=f"https://t.me/{Config.FORCE_SUB}",
            style_type="primary"
        )
    ]]
    text = "**Sᴏʀʀy Dᴜᴅᴇ Yᴏᴜ'ʀᴇ Nᴏᴛ Jᴏɪɴᴇᴅ My Cʜᴀɴɴᴇʟ 😐. Sᴏ Pʟᴇᴀꜱᴇ Jᴏɪɴ Oᴜʀ Uᴩᴅᴀᴛᴇ Cʜᴀɴɴᴇʟ Tᴏ Cᴄᴏɴᴛɪɴᴜᴇ**"
    try:
        user = await client.get_chat_member(Config.FORCE_SUB, message.from_user.id)    
        if user.status == enums.ChatMemberStatus.BANNED:                                   
            return await client.send_message(message.from_user.id, text="Sᴏʀʀy Yᴏᴜ'ʀᴇ Bᴀɴɴᴇᴅ Tᴏ Uꜱᴇ Mᴇ")  
    except UserNotParticipant:                       
        return await message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
    return await message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
