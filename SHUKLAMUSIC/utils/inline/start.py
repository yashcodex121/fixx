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

from pyrogram.types import InlineKeyboardButton

import config
from pyrogram.enums import ButtonStyle
from SHUKLAMUSIC import app

# ── Premium emoji IDs (Emoji_fan37_by_TgEmodziBot pack) ──
_E_SPARK   = 4958489311726011319   # ✨
_E_STAR    = 4958714479681471536   # ⭐️
_E_CROWN   = 4956420911310832630   # 👑
_E_SUPPORT = 4956475826762679249   # 💬
_E_BULB    = 4958665796227171144   # 💡
_E_UPDATE  = 4956214478002717877   # 🔝
_E_DIAMOND = 4956739572114392015   # 💎
_E_BELL    = 4956290155326473271   # 🔔


def _clean_username(username: str) -> str:
    return username.lstrip("@")


def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_1"],
                url=f"https://t.me/{app.username}?startgroup=true",
                style=ButtonStyle.PRIMARY,
                icon_custom_emoji_id=_E_SPARK
            ),
            InlineKeyboardButton(
                text=_["S_B_2"],
                url=config.SUPPORT_CHAT,
                style=ButtonStyle.DANGER,
                icon_custom_emoji_id=_E_SUPPORT
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_4"],
                url=f"https://t.me/{app.username}?start=help",
                style=ButtonStyle.SUCCESS,
                icon_custom_emoji_id=_E_BULB
            ),
        ],
    ]
    return buttons


def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
                style=ButtonStyle.PRIMARY,
                icon_custom_emoji_id=_E_SPARK
            )
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_6"],
                url=config.SUPPORT_CHANNEL,
                style=ButtonStyle.SUCCESS,
                icon_custom_emoji_id=_E_UPDATE
            ),
            InlineKeyboardButton(
                text=_["S_B_2"],
                url=config.SUPPORT_CHAT,
                style=ButtonStyle.DANGER,
                icon_custom_emoji_id=_E_SUPPORT
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_4"],
                callback_data="settings_back_helper",
                style=ButtonStyle.SUCCESS,
                icon_custom_emoji_id=_E_BULB
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                url=f"https://t.me/{_clean_username(config.OWNER_USERNAME)}",
                style=ButtonStyle.DANGER,
                icon_custom_emoji_id=_E_CROWN
            ),
        ],
    ]
    return buttons
