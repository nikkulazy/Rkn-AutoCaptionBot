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
    dets = {
        "user_id": user_id, 
        "chnl_id": chnl_id, 
        "caption": caption,
        "buttons": buttons if buttons else []
    }
    await chnl_ids.insert_one(dets)

async def updateCapByUser(user_id, caption):
    await chnl_ids.update_one(
        {"user_id": user_id}, 
        {"$set": {"caption": caption}}
    )

async def updateButtonsByUser(user_id, buttons):
    buttons_list = []
    for btn in buttons:
        if isinstance(btn, list) and len(btn) > 0:
            buttons_list.append({
                "text": btn[0].text,
                "url": btn[0].url
            })
    await chnl_ids.update_one(
        {"user_id": user_id}, 
        {"$set": {"buttons": buttons_list}}
    )

async def deleteButtonsByUser(user_id):
    await chnl_ids.update_one(
        {"user_id": user_id}, 
        {"$set": {"buttons": []}}
    )

async def getChannelDataByUser(user_id):
    data = await chnl_ids.find_one({"user_id": user_id})
    if data:
        if data.get("buttons") and len(data["buttons"]) > 0:
            from pyrogram.types import InlineKeyboardButton
            buttons = []
            for btn in data["buttons"]:
                if isinstance(btn, dict) and "text" in btn and "url" in btn:
                    buttons.append([InlineKeyboardButton(btn["text"], url=btn["url"])])
            data["buttons"] = buttons
        else:
            data["buttons"] = []
    return data

# ============ CHANNEL-BASED FUNCTIONS ============

async def addCap(chnl_id, caption, buttons=None):
    dets = {
        "chnl_id": chnl_id, 
        "caption": caption,
        "buttons": buttons if buttons else []
    }
    await chnl_ids.insert_one(dets)

async def updateCap(chnl_id, caption):
    await chnl_ids.update_one(
        {"chnl_id": chnl_id}, 
        {"$set": {"caption": caption}}
    )

async def updateButtons(chnl_id, buttons):
    buttons_list = []
    for btn in buttons:
        if isinstance(btn, list) and len(btn) > 0:
            buttons_list.append({
                "text": btn[0].text,
                "url": btn[0].url
            })
    await chnl_ids.update_one(
        {"chnl_id": chnl_id}, 
        {"$set": {"buttons": buttons_list}}
    )

async def getChannelData(chnl_id):
    data = await chnl_ids.find_one({"chnl_id": chnl_id})
    if data:
        if data.get("buttons") and len(data["buttons"]) > 0:
            from pyrogram.types import InlineKeyboardButton
            buttons = []
            for btn in data["buttons"]:
                if isinstance(btn, dict) and "text" in btn and "url" in btn:
                    buttons.append([InlineKeyboardButton(btn["text"], url=btn["url"])])
            data["buttons"] = buttons
        else:
            data["buttons"] = []
    return data

async def deleteButtons(chnl_id):
    await chnl_ids.update_one(
        {"chnl_id": chnl_id}, 
        {"$set": {"buttons": []}}
    )

# ============ RESET FUNCTIONS ============

async def resetChannelData(chnl_id):
    await chnl_ids.delete_many({"chnl_id": chnl_id})

async def resetUserData(user_id):
    await chnl_ids.delete_many({"user_id": user_id})
