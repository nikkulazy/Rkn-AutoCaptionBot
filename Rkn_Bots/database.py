import motor.motor_asyncio
from config import Rkn_Bots

client = motor.motor_asyncio.AsyncIOMotorClient(Rkn_Bots.DB_URL)
db = client[Rkn_Bots.DB_NAME]
chnl_ids = db.chnl_ids
users = db.users

async def insert(user_id):
    user_det = {"_id": user_id}
    try:
        await users.insert_one(user_det)
    except:
        pass
        
async def total_user():
    user = await users.count_documents({})
    return user

async def getid():
    all_users = users.find({})
    return all_users

async def delete(id):
    await users.delete_one(id)

# ============ USER-BASED FUNCTIONS ============

async def addCapByUser(user_id, chnl_id, caption, buttons=None):
    dets = {"user_id": user_id, "chnl_id": chnl_id, "caption": caption}
    if buttons:
        dets["buttons"] = []
        for btn in buttons:
            btn_data = {"text": btn[0].text, "url": btn[0].url}
            if hasattr(btn[0], 'style'):
                btn_data["style"] = {
                    'bg_primary': getattr(btn[0].style, 'bg_primary', False),
                    'bg_danger': getattr(btn[0].style, 'bg_danger', False),
                    'bg_success': getattr(btn[0].style, 'bg_success', False),
                }
            dets["buttons"].append(btn_data)
    await chnl_ids.insert_one(dets)

async def updateCapByUser(user_id, caption):
    await chnl_ids.update_one({"user_id": user_id}, {"$set": {"caption": caption}})

async def updateButtonsByUser(user_id, buttons):
    buttons_dict = []
    for btn in buttons:
        btn_data = {"text": btn[0].text, "url": btn[0].url}
        if hasattr(btn[0], 'style'):
            btn_data["style"] = {
                'bg_primary': getattr(btn[0].style, 'bg_primary', False),
                'bg_danger': getattr(btn[0].style, 'bg_danger', False),
                'bg_success': getattr(btn[0].style, 'bg_success', False),
            }
        buttons_dict.append(btn_data)
    
    doc = await chnl_ids.find_one({"user_id": user_id})
    if doc:
        await chnl_ids.update_one({"user_id": user_id}, {"$set": {"buttons": buttons_dict}})
    else:
        await chnl_ids.insert_one({"user_id": user_id, "buttons": buttons_dict})

async def deleteButtonsByUser(user_id):
    await chnl_ids.update_one({"user_id": user_id}, {"$unset": {"buttons": ""}})

async def getChannelDataByUser(user_id):
    data = await chnl_ids.find_one({"user_id": user_id})
    if data and "buttons" in data and data["buttons"]:
        from pyrogram.types import InlineKeyboardButton
        
        # Custom Style Class
        class KeyboardButtonStyle:
            def __init__(self, bg_primary=False, bg_danger=False, bg_success=False):
                self.bg_primary = bg_primary
                self.bg_danger = bg_danger
                self.bg_success = bg_success
        
        restored_buttons = []
        for btn in data["buttons"]:
            style = None
            if "style" in btn:
                style = KeyboardButtonStyle(
                    bg_primary=btn["style"].get("bg_primary", False),
                    bg_danger=btn["style"].get("bg_danger", False),
                    bg_success=btn["style"].get("bg_success", False),
                )
            button = InlineKeyboardButton(text=btn["text"], url=btn["url"])
            if style:
                button.style = style
            restored_buttons.append([button])
        data["buttons"] = restored_buttons
    return data

# ============ CHANNEL-BASED FUNCTIONS ============

async def addCap(chnl_id, caption, buttons=None):
    dets = {"chnl_id": chnl_id, "caption": caption}
    if buttons:
        dets["buttons"] = []
        for btn in buttons:
            btn_data = {"text": btn[0].text, "url": btn[0].url}
            if hasattr(btn[0], 'style'):
                btn_data["style"] = {
                    'bg_primary': getattr(btn[0].style, 'bg_primary', False),
                    'bg_danger': getattr(btn[0].style, 'bg_danger', False),
                    'bg_success': getattr(btn[0].style, 'bg_success', False),
                }
            dets["buttons"].append(btn_data)
    await chnl_ids.insert_one(dets)

async def updateCap(chnl_id, caption, buttons=None):
    update_data = {"caption": caption}
    if buttons is not None:
        buttons_dict = []
        for btn in buttons:
            btn_data = {"text": btn[0].text, "url": btn[0].url}
            if hasattr(btn[0], 'style'):
                btn_data["style"] = {
                    'bg_primary': getattr(btn[0].style, 'bg_primary', False),
                    'bg_danger': getattr(btn[0].style, 'bg_danger', False),
                    'bg_success': getattr(btn[0].style, 'bg_success', False),
                }
            buttons_dict.append(btn_data)
        update_data["buttons"] = buttons_dict
    await chnl_ids.update_one({"chnl_id": chnl_id}, {"$set": update_data})

async def updateButtons(chnl_id, buttons):
    buttons_dict = []
    for btn in buttons:
        btn_data = {"text": btn[0].text, "url": btn[0].url}
        if hasattr(btn[0], 'style'):
            btn_data["style"] = {
                'bg_primary': getattr(btn[0].style, 'bg_primary', False),
                'bg_danger': getattr(btn[0].style, 'bg_danger', False),
                'bg_success': getattr(btn[0].style, 'bg_success', False),
            }
        buttons_dict.append(btn_data)
    
    doc = await chnl_ids.find_one({"chnl_id": chnl_id})
    if doc:
        await chnl_ids.update_one({"chnl_id": chnl_id}, {"$set": {"buttons": buttons_dict}})
    else:
        await chnl_ids.insert_one({"chnl_id": chnl_id, "buttons": buttons_dict})

async def getChannelData(chnl_id):
    data = await chnl_ids.find_one({"chnl_id": chnl_id})
    if data and "buttons" in data and data["buttons"]:
        from pyrogram.types import InlineKeyboardButton
        
        class KeyboardButtonStyle:
            def __init__(self, bg_primary=False, bg_danger=False, bg_success=False):
                self.bg_primary = bg_primary
                self.bg_danger = bg_danger
                self.bg_success = bg_success
        
        restored_buttons = []
        for btn in data["buttons"]:
            style = None
            if "style" in btn:
                style = KeyboardButtonStyle(
                    bg_primary=btn["style"].get("bg_primary", False),
                    bg_danger=btn["style"].get("bg_danger", False),
                    bg_success=btn["style"].get("bg_success", False),
                )
            button = InlineKeyboardButton(text=btn["text"], url=btn["url"])
            if style:
                button.style = style
            restored_buttons.append([button])
        data["buttons"] = restored_buttons
    return data

async def deleteButtons(chnl_id):
    await chnl_ids.update_one({"chnl_id": chnl_id}, {"$unset": {"buttons": ""}})

# ============ RESET FUNCTIONS ============

async def resetChannelData(chnl_id):
    await chnl_ids.delete_many({"chnl_id": chnl_id})
    print(f"✅ Reset data for channel: {chnl_id}")

async def resetUserData(user_id):
    await chnl_ids.delete_many({"user_id": user_id})
    print(f"✅ Reset data for user: {user_id}")
