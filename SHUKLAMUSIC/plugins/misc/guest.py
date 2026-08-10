from pyrogram.enums import ButtonStyle
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)

from SHUKLAMUSIC import app

# ================================
#   GUEST BOTS (@-mention anywhere)
# ================================
# Telegram's "Guest Mode" lets a bot be summoned by tagging its
# @username in ANY chat — a group, a channel, or even a private DM
# between two other people — without the bot being a member of that
# chat at all. Telegram delivers this as a "guest message" and the
# bot gets exactly ONE reply via answer_guest_query().
#
# IMPORTANT (one-time setup, cannot be done from code):
#   Open @BotFather's Mini App (blue "Open" button, NOT /mybots text
#   menu) -> your bot -> Bot Settings -> Guest Mode -> Enable.
#   Without this toggle ON, Telegram will never send guest messages
#   to your bot, no matter what code is running.

ADD_ME_PROMO_TEXT = (
    "❖ 𝗗𝗼𝗼𝗺 𝗠𝘂𝘀𝗶𝗰 - 𝗔 𝗠𝗼𝘀𝘁 𝗣𝗼𝘄𝗲𝗿𝗳𝘂𝗹 𝗠𝘂𝘀𝗶𝗰 𝗦𝘁𝗿𝗲𝗮𝗺𝗲𝗿 𝗕𝗼𝘁 𝗙𝗼𝗿 𝗬𝗼𝘂𝗿 𝗚𝗿𝗼𝘂𝗽𝘀 & 𝗖𝗵𝗮𝗻𝗻𝗲𝗹𝘀 🚀\n\n"
    "▸ 𝗧𝗮𝗽 𝗧𝗵𝗲 𝗕𝗲𝗹𝗼𝘄 𝗕𝘂𝘁𝘁𝗼𝗻 𝗧𝗼 𝗔𝗱𝗱 𝗠𝗲 𝗶𝗻 𝗬𝗼𝘂𝗿 𝗚𝗿𝗼𝘂𝗽 & 𝗘𝗻𝗷𝗼𝘆 𝗛𝗶𝗴𝗵 𝗤𝘂𝗮𝗹𝗶𝘁𝘆 𝗦𝗼𝗻𝗴𝘀 🎵"
)


def _add_me_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="➕ 𝗔𝗱𝗱 𝗠𝗲 𝗧𝗼 𝗬𝗼𝘂𝗿 𝗚𝗿𝗼𝘂𝗽 ➕",
                    url=f"https://t.me/{app.username}?startgroup=true",
                    style=ButtonStyle.SUCCESS,
                )
            ]
        ]
    )


@app.on_guest_message()
async def guest_username_mention(_, message: Message):
    # message.guest_query_id is the id you must answer with, exactly once.
    if not message.guest_query_id:
        return

    result = InlineQueryResultArticle(
        title="❖ 𝗗𝗼𝗼𝗺 𝗠𝘂𝘀𝗶𝗰",
        description="Tap to send the Add Me card in this chat 🎵",
        thumb_url="https://files.catbox.moe/w5nima.jpg",
        input_message_content=InputTextMessageContent(ADD_ME_PROMO_TEXT),
        reply_markup=_add_me_markup(),
    )

    try:
        await app.answer_guest_query(message.guest_query_id, result=result)
    except Exception:
        pass
