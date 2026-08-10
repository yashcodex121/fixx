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
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram import Client, filters, enums
from pyrogram.enums import ButtonStyle

# ── Premium emoji IDs (Emoji_fan37_by_TgEmodziBot pack) ──
_E_BRAIN   = 4958937938239947673   # 🧠  ChatGPT
_E_CROWN   = 4956420911310832630   # 👑  Groups
_E_HAT     = 4956564307383944011   # 🎩  Stickers
_E_PIN     = 4956232383721374836   # 📌  Tag-All
_E_INFO    = 4958529074533238201   # ℹ️  Info
_E_SPARK   = 4958489311726011319   # ✨  Extra
_E_ROSE    = 4958597497657230624   # 🌹  Image
_E_BOLT    = 4958479549265347295   # ⚡️  Action
_E_SEARCH  = 4958587679361991667   # 🔍  Search
_E_CHAT    = 4956475826762679249   # 💬  Font
_E_JOKER   = 4956525562483967357   # 🃏  Games
_E_CHART   = 4958506272551863292   # 📊  T-Graph
_E_CLOWN   = 4956398976912851936   # 🤡  Imposter
_E_CRYSTAL = 4958624886663678191   # 🔮  Truth-Dare
_E_LINK    = 4958689671950369798   # 🔗  Hastag
_E_MIC     = 4956441587283395517   # 🎤  TTS
_E_PARTY   = 4956308456182121758   # 🎉  Fun
_E_MEGA    = 4958686613933655185   # 📣  Quotly
_E_BACK    = 4956282853882069908   # ➡️  Back nav
_E_PLAY    = 4956250031741993892   # ▶️  Forward nav
_E_KEY     = 5978869985299142389   # 🦚  String Gen


class BUTTONS(object):
    MBUTTON = [
        [
            InlineKeyboardButton("ᴄʜᴀᴛ-ɢᴘᴛ",    callback_data="mplus HELP_ChatGPT", style=ButtonStyle.PRIMARY,  icon_custom_emoji_id=_E_BRAIN),
            InlineKeyboardButton("ɢʀᴏᴜᴘs",       callback_data="mplus HELP_Group",   style=ButtonStyle.SUCCESS,  icon_custom_emoji_id=_E_CROWN),
            InlineKeyboardButton("sᴛɪᴄᴋᴇʀs",     callback_data="mplus HELP_Sticker", style=ButtonStyle.DANGER,   icon_custom_emoji_id=_E_HAT),
        ],
        [
            InlineKeyboardButton("ᴛᴀɢ-ᴀʟʟ",      callback_data="mplus HELP_TagAll",  style=ButtonStyle.DANGER,   icon_custom_emoji_id=_E_PIN),
            InlineKeyboardButton("ɪɴꜰᴏ",          callback_data="mplus HELP_Info",    style=ButtonStyle.PRIMARY,  icon_custom_emoji_id=_E_INFO),
            InlineKeyboardButton("ᴇxᴛʀᴀ",         callback_data="mplus HELP_Extra",   style=ButtonStyle.SUCCESS,  icon_custom_emoji_id=_E_SPARK),
        ],
        [
            InlineKeyboardButton("ɪᴍᴀɢᴇ",         callback_data="mplus HELP_Image",   style=ButtonStyle.SUCCESS,  icon_custom_emoji_id=_E_ROSE),
            InlineKeyboardButton("ᴀᴄᴛɪᴏɴ",        callback_data="mplus HELP_Action",  style=ButtonStyle.DANGER,   icon_custom_emoji_id=_E_BOLT),
            InlineKeyboardButton("sᴇᴀʀᴄʜ",        callback_data="mplus HELP_Search",  style=ButtonStyle.PRIMARY,  icon_custom_emoji_id=_E_SEARCH),
        ],
        [
            InlineKeyboardButton("ғᴏɴᴛ",           callback_data="mplus HELP_Font",    style=ButtonStyle.PRIMARY,  icon_custom_emoji_id=_E_CHAT),
            InlineKeyboardButton("ɢᴀᴍᴇs",          callback_data="mplus HELP_Game",    style=ButtonStyle.SUCCESS,  icon_custom_emoji_id=_E_JOKER),
            InlineKeyboardButton("ᴛ-ɢʀᴀᴘʜ",        callback_data="mplus HELP_TG",      style=ButtonStyle.DANGER,   icon_custom_emoji_id=_E_CHART),
        ],
        [
            InlineKeyboardButton("ɪᴍᴘᴏsᴛᴇʀ",      callback_data="mplus HELP_Imposter",style=ButtonStyle.DANGER,   icon_custom_emoji_id=_E_CLOWN),
            InlineKeyboardButton("ᴛʀᴜᴛʜ-ᴅᴀʀᴇ",    callback_data="mplus HELP_TD",      style=ButtonStyle.PRIMARY,  icon_custom_emoji_id=_E_CRYSTAL),
            InlineKeyboardButton("ʜᴀsᴛᴀɢ",         callback_data="mplus HELP_HT",      style=ButtonStyle.SUCCESS,  icon_custom_emoji_id=_E_LINK),
        ],
        [
            InlineKeyboardButton("ᴛᴛs",             callback_data="mplus HELP_TTS",     style=ButtonStyle.SUCCESS,  icon_custom_emoji_id=_E_MIC),
            InlineKeyboardButton("ғᴜɴ",             callback_data="mplus HELP_Fun",     style=ButtonStyle.PRIMARY,  icon_custom_emoji_id=_E_PARTY),
            InlineKeyboardButton("ǫᴜᴏᴛʟʏ",         callback_data="mplus HELP_Q",       style=ButtonStyle.DANGER,   icon_custom_emoji_id=_E_MEGA),
        ],
        [
            InlineKeyboardButton("💰 ᴄʀʏᴘᴛᴏ",      callback_data="mplus HELP_Crypto",    style=ButtonStyle.PRIMARY,  icon_custom_emoji_id=_E_CHART),
            InlineKeyboardButton("💸 ᴜᴘɪ ᴛᴏᴏʟs",   callback_data="mplus HELP_UPI",       style=ButtonStyle.SUCCESS,  icon_custom_emoji_id=_E_BOLT),
        ],
        [
            InlineKeyboardButton("🔑 sᴛʀɪɴɢ ɢᴇɴ",  callback_data="mplus HELP_StringGen", style=ButtonStyle.DANGER,   icon_custom_emoji_id=_E_KEY),
            InlineKeyboardButton("⚡ ǫᴜɪᴄᴋ ɢᴀᴍᴇs", callback_data="mplus HELP_21",        style=ButtonStyle.SUCCESS,  icon_custom_emoji_id=_E_JOKER),
        ],
        [
            InlineKeyboardButton("◁", callback_data="settings_back_helper",            style=ButtonStyle.SUCCESS,  icon_custom_emoji_id=_E_BACK),
            InlineKeyboardButton("▷", callback_data="managebot123 settings_back_helper",style=ButtonStyle.PRIMARY, icon_custom_emoji_id=_E_PLAY),
        ],
    ]
