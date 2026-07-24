# config.py - Simple Configuration
# (c) @RknDeveloperr

import re, os, time
id_pattern = re.compile(r'^.\d+$') 

class Rkn_Bots(object):
    
    API_ID = os.environ.get("API_ID", "")
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    RKN_PIC = os.environ.get("RKN_PIC", "https://envs.sh/Nob.jpg")
    BOT_UPTIME = time.time()
    PORT = int(os.environ.get("PORT", "8080"))
    FORCE_SUB = os.environ.get("FORCE_SUB", "wolverine273") 
    DB_NAME = os.environ.get("DB_NAME", "AutoCaption_V05_Bot")     
    DB_URL = os.environ.get("DB_URL", "")
    DEF_CAP = os.environ.get("DEF_CAP", "<b><a href='telegram.me/WOLVERIN_P'>{file_name}</a></b>")
    STICKER_ID = os.environ.get("STICKER_ID", "CAACAgIAAxkBAAELFqBllhB70i13m-woXeIWDXU6BD2j7wAC9gcAAkb7rAR7xdjVOS5ziTQE")
    ADMIN = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '5346278816').split()]
    LOG_CHANNEL = os.environ.get("LOG_CHANNEL", "-1001521000125")

# Rkn Developer 
# Don't Remove Credit 😔
