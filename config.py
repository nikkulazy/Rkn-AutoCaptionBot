# (c) @RknDeveloperr
# Rkn Developer 
# Don't Remove Credit 😔
# Telegram Channel @RknDeveloper & @Rkn_Botz
# Developer @RknDeveloperr

import re, os, time
id_pattern = re.compile(r'^.\d+$') 

class Rkn_Bots(object):
    
    # Rkn client config  ( required.. 😥)
    API_ID = os.environ.get("API_ID", "22384370")
    API_HASH = os.environ.get("API_HASH", "05e2be75292ecbec3f7a29bf13b1e29e")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

    # start_pic
    RKN_PIC = os.environ.get("RKN_PIC", "https://envs.sh/Nob.jpg")

    # wes response configuration
    BOT_UPTIME = time.time()
    PORT = int(os.environ.get("PORT", "8080"))

    # force subs channel ( required.. 😥)
    FORCE_SUB = os.environ.get("FORCE_SUB", "wolverine273") 
    
    # database config ( required.. 😥)
    DB_NAME = os.environ.get("DB_NAME", "AutoCaption_V05_Bot")     
    DB_URL = os.environ.get("DB_URL", "")

    # default caption 
    DEF_CAP = os.environ.get("DEF_CAP", "<b><a href='telegram.me/WOLVERIN_P'>{file_name} Telegram : @WOLVERIN_P\n\nForward the file before Downloading.</a></b>",
    )

    # sticker Id
    STICKER_ID = os.environ.get("STICKER_ID", "CAACAgIAAxkBAAELFqBllhB70i13m-woXeIWDXU6BD2j7wAC9gcAAkb7rAR7xdjVOS5ziTQE")

    # admin id  ( required.. 😥)
    ADMIN = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '5346278816').split()]
    LOG_CHANNEL = os.environ.get("LOG_CHANNEL", "1521000125")  #

# Rkn Developer 
# Don't Remove Credit 😔
# Telegram Channel @RknDeveloper & @Rkn_Botz
# Developer @RknDeveloperr




