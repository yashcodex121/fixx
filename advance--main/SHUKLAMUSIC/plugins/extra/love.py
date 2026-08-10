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
import random
from SHUKLAMUSIC import app

# ── AttractivePack emoji IDs ──
_AP_PINK   = 5208942800514596941   # 🩷
_AP_LOVE   = 5220157149103023925   # 💖
_AP_LILAC  = 5366119022792294762   # 💜
_AP_FLOWER = 5366458509892276868   # 🌸
_AP_STAR   = 5413351005779672594   # ⭐
_AP_BOW    = 5379869575338812919   # 🎀
_AP_YELLOW = 5363897614167199267   # 💛
_AP_GREEN  = 5366596996817766990   # 💚
_AP_ORANGE = 5366238787955347845   # 🧡
_AP_BLUE   = 5379853726909486003   # 💙

def ap(eid, fb):
    return f'<emoji id={eid}>{fb}</emoji>'

def get_random_message(love_percentage):
    if love_percentage <= 30:
        return random.choice([
            "Love is in the air but needs a little spark.",
            "A good start but there's room to grow.",
            "It's just the beginning of something beautiful."
        ])
    elif love_percentage <= 70:
        return random.choice([
            "A strong connection is there. Keep nurturing it.",
            "You've got a good chance. Work on it.",
            "Love is blossoming, keep going."
        ])
    else:
        return random.choice([
            "Wow! It's a match made in heaven!",
            "Perfect match! Cherish this bond.",
            "Destined to be together. Congratulations!"
        ])
        
@app.on_message(filters.command("love", prefixes="/"))
def love_command(client, message):
    command, *args = message.text.split(" ")
    if len(args) >= 2:
        name1 = args[0].strip()
        name2 = args[1].strip()
        
        love_percentage = random.randint(10, 100)
        love_message = get_random_message(love_percentage)

        hearts = [
            ap(_AP_PINK,'🩷'), ap(_AP_LOVE,'💖'), ap(_AP_LILAC,'💜'),
            ap(_AP_BLUE,'💙'), ap(_AP_YELLOW,'💛'), ap(_AP_GREEN,'💚'),
            ap(_AP_ORANGE,'🧡'), ap(_AP_FLOWER,'🌸'),
        ]
        heart_bar = " ".join(hearts[:min(max(1, love_percentage // 13), 8)])
        response = (
            f"{ap(_AP_LOVE,'💖')} <b>ʟᴏᴠᴇ ᴄᴀʟᴄᴜʟᴀᴛᴏʀ</b> {ap(_AP_LOVE,'💖')}\n\n"
            f"{ap(_AP_PINK,'🩷')} <b>{name1}</b> + <b>{name2}</b>\n\n"
            f"{ap(_AP_STAR,'⭐')} <b>ᴄᴏᴍᴘᴀᴛɪʙɪʟɪᴛʏ :</b> <code>{love_percentage}%</code>\n"
            f"{ap(_AP_FLOWER,'🌸')} {heart_bar}\n\n"
            f"{ap(_AP_BOW,'🎀')} <i>{love_message}</i>"
        )
    else:
        response = f"{ap(_AP_PINK,'🩷')} <b>ᴜsᴀɢᴇ :</b> <code>/love Name1 Name2</code>"
    app.send_message(message.chat.id, response)
