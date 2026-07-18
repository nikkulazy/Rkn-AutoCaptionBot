# (c) @RknDeveloperr
# Rkn Developer 
# Don't Remove Credit 😔
# Telegram Channel @RknDeveloper & @Rkn_Bots
# Developer @RknDeveloperr

import motor.motor_asyncio
from config import Rkn_Bots

client = motor.motor_asyncio.AsyncIOMotorClient(Rkn_Bots.DB_URL)
db = client[Rkn_Bots.DB_NAME]
chnl_ids = db.chnl_ids
users = db.users

#insert user data
async def insert(user_id):
    user_det = {"_id": user_id}
    try:
        await users.insert_one(user_det)
    except:
        pass
        
# Total User
async def total_user():
    user = await users.count_documents({})
    return user

async def getid():
    all_users = users.find({})
    return all_users

async def delete(id):
    await users.delete_one(id)

# ============ CHANNEL FUNCTIONS ============

# Add channel data with user_id
async def addCapByUser(user_id, chnl_id, caption, buttons=None):
    dets = {"user_id": user_id, "chnl_id": chnl_id, "caption": caption}
    if buttons:
        dets["buttons"] = buttons
    await chnl_ids.insert_one(dets)

# Update caption by user_id
async def updateCapByUser(user_id, caption):
    await chnl_ids.update_one({"user_id": user_id}, {"$set": {"caption": caption}})

# Update buttons by user_id
async def updateButtonsByUser(user_id, buttons):
    await chnl_ids.update_one({"user_id": user_id}, {"$set": {"buttons": buttons}})

# Delete buttons by user_id
async def deleteButtonsByUser(user_id):
    await chnl_ids.update_one({"user_id": user_id}, {"$unset": {"buttons": ""}})

# Get channel data by user_id
async def getChannelDataByUser(user_id):
    return await chnl_ids.find_one({"user_id": user_id})

# ============ BACKWARD COMPATIBILITY (Old functions) ============

# Add channel data (old)
async def addCap(chnl_id, caption, buttons=None):
    dets = {"chnl_id": chnl_id, "caption": caption}
    if buttons:
        dets["buttons"] = buttons
    await chnl_ids.insert_one(dets)

# Update caption (old)
async def updateCap(chnl_id, caption, buttons=None):
    update_data = {"caption": caption}
    if buttons is not None:
        update_data["buttons"] = buttons
    await chnl_ids.update_one({"chnl_id": chnl_id}, {"$set": update_data})

# Update buttons (old)
async def updateButtons(chnl_id, buttons):
    await chnl_ids.update_one({"chnl_id": chnl_id}, {"$set": {"buttons": buttons}})

# Get channel data (old)
async def getChannelData(chnl_id):
    return await chnl_ids.find_one({"chnl_id": chnl_id})

# Delete buttons (old)
async def deleteButtons(chnl_id):
    await chnl_ids.update_one({"chnl_id": chnl_id}, {"$unset": {"buttons": ""}})

# Rkn Developer 
# Don't Remove Credit 😔
# Telegram Channel @RknDeveloper & @Rkn_Bots
# Developer @RknDeveloperr
