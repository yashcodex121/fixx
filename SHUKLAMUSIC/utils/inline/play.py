import math

from pyrogram.types import InlineKeyboardButton
from pyrogram.enums import ButtonStyle

import config
from SHUKLAMUSIC.utils.formatters import time_to_seconds


def track_markup(_, videoid, user_id, channel, fplay, chat_id=None):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="✨ Add to Playlist",
                callback_data=f"SHUKLAPlaylists {videoid}|{user_id}|add|{channel}|{fplay}",
                style=ButtonStyle.SUCCESS,
            ),
            InlineKeyboardButton(
                text="🔁 Autoplay On/Off",
                callback_data=f"ADMIN Autoplay|{chat_id if chat_id else user_id}",
                style=ButtonStyle.PRIMARY,
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style=ButtonStyle.DANGER,
            )
        ],
    ]
    return buttons


def stream_markup_timer(_, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / max(duration_sec, 1)) * 100
    umm = min(100, max(0, math.floor(percentage)))

    total_blocks = 10
    filled = round((umm / 100) * total_blocks)
    empty = total_blocks - filled
    bar = "▰" * filled + "▱" * empty

    current_min, current_sec = divmod(played_sec, 60)
    total_min, total_sec = divmod(duration_sec, 60)
    current_time = f"{int(current_min):02d}:{int(current_sec):02d}"
    total_time = f"{int(total_min):02d}:{int(total_sec):02d}"

    buttons = [
        [
            InlineKeyboardButton(
                text=f"{current_time} {bar} {total_time}",
                callback_data="GetTimer",
                style=ButtonStyle.PRIMARY,
                icon_custom_emoji_id=5204046146955153467,
            )
        ],
        [
            InlineKeyboardButton(text="", callback_data=f"ADMIN Resume|{chat_id}", icon_custom_emoji_id=5409222721869459068, style=ButtonStyle.SUCCESS),
            InlineKeyboardButton(text="", callback_data=f"ADMIN Skip|{chat_id}", icon_custom_emoji_id=6062169402831279585, style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="", callback_data=f"ADMIN Pause|{chat_id}", icon_custom_emoji_id=5409042015415448331, style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="", callback_data=f"ADMIN Stop|{chat_id}", icon_custom_emoji_id=5408832111773757273, style=ButtonStyle.DANGER),
        ],
        [
            InlineKeyboardButton(text="🔁 Replay", callback_data=f"ADMIN Replay|{chat_id}", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="🔀 Shuffle", callback_data=f"ADMIN Shuffle|{chat_id}", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="🔂 Loop", callback_data=f"ADMIN Loop|{chat_id}", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton(text="🔁 Autoplay On/Off", callback_data=f"ADMIN Autoplay|{chat_id}", style=ButtonStyle.SUCCESS),
        ],
        [InlineKeyboardButton(text=" ᴄʟᴏsᴇ ▣", callback_data="close", style=ButtonStyle.DANGER, icon_custom_emoji_id=5408832111773757273)],
    ]

    return buttons


def stream_markup(_, chat_id):
    buttons = [
        [
            InlineKeyboardButton(text="", callback_data=f"ADMIN Resume|{chat_id}", icon_custom_emoji_id=5409222721869459068, style=ButtonStyle.SUCCESS),
            InlineKeyboardButton(text="", callback_data=f"ADMIN Skip|{chat_id}", icon_custom_emoji_id=6062169402831279585, style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="", callback_data=f"ADMIN Pause|{chat_id}", icon_custom_emoji_id=5409042015415448331, style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="", callback_data=f"ADMIN Stop|{chat_id}", icon_custom_emoji_id=5408832111773757273, style=ButtonStyle.DANGER),
        ],
        [
            InlineKeyboardButton(text="🔁 Replay", callback_data=f"ADMIN Replay|{chat_id}", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="🔀 Shuffle", callback_data=f"ADMIN Shuffle|{chat_id}", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="🔂 Loop", callback_data=f"ADMIN Loop|{chat_id}", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton(text="🔁 Autoplay On/Off", callback_data=f"ADMIN Autoplay|{chat_id}", style=ButtonStyle.SUCCESS),
        ],
        [InlineKeyboardButton(text=" ᴄʟᴏsᴇ ▣", callback_data="close", style=ButtonStyle.DANGER, icon_custom_emoji_id=5408832111773757273)],
    ]
    return buttons


def playlist_markup(_, videoid, user_id, ptype, channel, fplay, chat_id=None):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"SHUKLAPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"SHUKLAPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="📋 Playlist",
                callback_data=f"ViewPlaylist {user_id}",
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text="🔁 Autoplay On/Off",
                callback_data=f"ADMIN Autoplay|{chat_id if chat_id else user_id}",
                style=ButtonStyle.SUCCESS,
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style=ButtonStyle.DANGER,
            ),
        ],
    ]
    return buttons


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style=ButtonStyle.DANGER,
            ),
        ],
    ]
    return buttons


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = f"{query[:20]}"
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="◁",
                callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {query}|{user_id}",
                style=ButtonStyle.DANGER,
            ),
            InlineKeyboardButton(
                text="▷",
                callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
        ],
    ]
    return buttons
