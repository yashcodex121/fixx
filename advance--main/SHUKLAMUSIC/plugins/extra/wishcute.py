# -----------------------------------------------
# 🔸 StrangerMusic Project
# 🔹 Developed & Maintained by: Shashank Shukla (https://github.com/itzshukla)
# 📅 Copyright © 2022 – All Rights Reserved
#
# 📖 License:
# This source code is open for educational and non-commercial use ONLY.
# You are required to retain this credit in all copies or substantial portions of this file.
# Commercial use, redistribution, or removal of this notice is strictly prohibited
# without prior written permission from the author.
#
# ❤️ Made with dedication and love by ItzShukla
# -----------------------------------------------
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import random
import config
import requests
from SHUKLAMUSIC import app

# ── AttractivePack emoji IDs ──
_AP_PINK   = 5208942800514596941   # 🩷
_AP_LOVE   = 5220157149103023925   # 💖
_AP_FLOWER = 5366458509892276868   # 🌸
_AP_STAR   = 5413351005779672594   # ⭐
_AP_BOW    = 5379869575338812919   # 🎀
_AP_YELLOW = 5363897614167199267   # 💛
_AP_LILAC  = 5366119022792294762   # 💜
_AP_SPARK  = 5343528160535270636   # ⚡️

def ap(eid, fb):
    return f'<emoji id={eid}>{fb}</emoji>' 


@app.on_message(filters.command("wish"))
async def wish(_, m):
    if len(m.command) < 2:
        await m.reply("ᴀᴅᴅ ᴡɪꜱʜ ʙᴀʙʏ🥀!")
        return 

    api = requests.get("https://nekos.best/api/v2/happy").json()
    url = api["results"][0]['url']
    text = m.text.split(None, 1)[1]
    wish_count = random.randint(1, 100)
    wish = (
        f"{ap(_AP_LOVE,'💖')} {ap(_AP_FLOWER,'🌸')} <b>ʜᴇʏ! {m.from_user.first_name}!</b>\n\n"
        f"{ap(_AP_PINK,'🩷')} <b>ʏᴏᴜʀ ᴡɪꜱʜ :</b> {text}\n"
        f"{ap(_AP_STAR,'⭐')} <b>ᴘᴏꜱꜱɪʙʟᴇ ᴛᴏ :</b> <code>{wish_count}%</code> {ap(_AP_BOW,'🎀')}"
    )
    
    await app.send_animation(
        chat_id=m.chat.id,
        animation=url,
        caption=wish,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("ꜱᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_CHAT)]])
    )
            
    
BUTTON = [[InlineKeyboardButton("ꜱᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_CHAT)]]
CUTIE = "https://64.media.tumblr.com/d701f53eb5681e87a957a547980371d2/tumblr_nbjmdrQyje1qa94xto1_500.gif"

@app.on_message(filters.command("cute"))
async def cute(_, message):
    if not message.reply_to_message:
        user_id = message.from_user.id
        user_name = message.from_user.first_name
    else:
        user_id = message.reply_to_message.from_user.id
        user_name = message.reply_to_message.from_user.first_name

    mention = f"[{user_name}](tg://user?id={str(user_id)})"
    mm = random.randint(1, 100)
    CUTE = (
        f"{ap(_AP_LOVE,'💖')} {ap(_AP_PINK,'🩷')} {mention}\n\n"
        f"{ap(_AP_FLOWER,'🌸')} <b>ᴄᴜᴛᴇɴᴇss ʟᴇᴠᴇʟ :</b> <code>{mm}%</code>\n"
        f"{ap(_AP_BOW,'🎀')} <b>ᴄᴜᴛᴇ ʙᴀʙʏ</b> {ap(_AP_STAR,'⭐')}"
    )

    await app.send_document(
        chat_id=message.chat.id,
        document=CUTIE,
        caption=CUTE,
        reply_markup=InlineKeyboardMarkup(BUTTON),
        reply_to_message_id=message.reply_to_message.message_id if message.reply_to_message else None,
    )
