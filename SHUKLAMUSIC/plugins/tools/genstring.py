# -----------------------------------------------
# 🔸 SHUKLAMUSIC — String Session Generator
# 🔹 Supports: Pyrogram v1/v2, Telethon, Bot Session
# 🔹 Interactive multi-step flow with state machine
# -----------------------------------------------
import asyncio
from pyrogram import Client as PyroClient, filters
from pyrogram.types import (
    Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
)
from pyrogram.enums import ButtonStyle
from SHUKLAMUSIC import app
from config import BANNED_USERS, API_ID as BOT_API_ID, API_HASH as BOT_API_HASH

# ── Premium emoji IDs (from Callmejija_by_fStikBot & existing packs) ──
_E_KEY    = 5978869985299142389   # 🦚  Pyrogram v2
_E_STAR   = 6271653280187684816   # 🌟  Pyrogram v1
_E_BOLT   = 4958479549265347295   # ⚡️  Telethon
_E_BOT    = 5208748315805499400   # ✅  Bot Session
_E_DONE   = 6269140848873574815   # ❤️  Success
_E_BACK   = 4956282853882069908   # ➡️  Back
_E_WARN   = 5978715546865112655   # 🚩  Error/Warning
_E_LOCK   = 4956337889593000947   # 🔒  Security

# In-memory state machine: user_id → state_dict
_gen_state: dict = {}

# Session type labels
_TYPES = {
    "pyro1": "Pyrogram v1",
    "pyro2": "Pyrogram v2",
    "telethon": "Telethon",
    "botstr": "Bot Session",
}


def e(eid: int, fb: str) -> str:
    return f"<emoji id={eid}>{fb}</emoji>"


def _type_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"⭐ ᴘʏʀᴏ ᴠ1",
                callback_data="gstr_pyro1",
                style=ButtonStyle.DANGER,
                icon_custom_emoji_id=_E_STAR,
            ),
            InlineKeyboardButton(
                f"✨ ᴘʏʀᴏ ᴠ2",
                callback_data="gstr_pyro2",
                style=ButtonStyle.SUCCESS,
                icon_custom_emoji_id=_E_KEY,
            ),
        ],
        [
            InlineKeyboardButton(
                f"⚡ ᴛᴇʟᴇᴛʜᴏɴ",
                callback_data="gstr_telethon",
                style=ButtonStyle.PRIMARY,
                icon_custom_emoji_id=_E_BOLT,
            ),
            InlineKeyboardButton(
                f"🤖 ʙᴏᴛ sᴇssɪᴏɴ",
                callback_data="gstr_botstr",
                style=ButtonStyle.DANGER,
                icon_custom_emoji_id=_E_BOT,
            ),
        ],
        [
            InlineKeyboardButton(
                f"❌ ᴄᴀɴᴄᴇʟ",
                callback_data="gstr_cancel",
                style=ButtonStyle.DANGER,
                icon_custom_emoji_id=_E_WARN,
            ),
        ],
    ])


_GENSTR_MSG = (
    f"{e(_E_KEY, '🦚')} <b>sᴛʀɪɴɢ sᴇssɪᴏɴ ɢᴇɴᴇʀᴀᴛᴏʀ</b>\n\n"
    f"{e(_E_STAR, '🌟')} ɢᴇɴᴇʀᴀᴛᴇ ʏᴏᴜʀ sᴇssɪᴏɴ sᴛʀɪɴɢ ꜱᴀꜰᴇʟʏ ɪɴ ᴅᴍ.\n\n"
    f"{e(_E_BOT, '✅')} <b>sᴜᴘᴘᴏʀᴛᴇᴅ ᴛʏᴘᴇs :</b>\n"
    f"  • <b>Pyrogram v1</b> — ʟᴇɢᴀᴄʏ ꜱᴛʀɪɴɢ ꜰᴏʀᴍᴀᴛ\n"
    f"  • <b>Pyrogram v2</b> — ᴍᴏᴅᴇʀɴ ꜱᴛʀɪɴɢ ꜰᴏʀᴍᴀᴛ\n"
    f"  • <b>Telethon</b>    — ᴛᴇʟᴇᴛʜᴏɴ ꜱᴇꜱꜱɪᴏɴ\n"
    f"  • <b>Bot Session</b> — ꜰᴏʀ ʙᴏᴛ ᴀᴄᴄᴏᴜɴᴛs\n\n"
    f"{e(_E_LOCK, '🔒')} <i>ᴛʜɪs ᴡɪʟʟ ɴᴇᴠᴇʀ sᴛᴏʀᴇ ʏᴏᴜʀ ᴄʀᴇᴅᴇɴᴛɪᴀʟs.\n"
    f"ᴀʟʟ ᴅᴀᴛᴀ ɪs ᴅᴇʟᴇᴛᴇᴅ ᴀꜰᴛᴇʀ ɢᴇɴᴇʀᴀᴛɪᴏɴ.</i>\n\n"
    f"👇 <b>ᴄʜᴏᴏsᴇ ᴛʏᴘᴇ ᴛᴏ ᴘʀᴏᴄᴇᴇᴅ :</b>"
)


@app.on_message(filters.command(["genstring", "strgen", "gensession"]) & ~BANNED_USERS)
async def genstring_cmd(client, message: Message):
    """Entry point – only works in DM for security."""
    if not message.chat.id == message.from_user.id:
        # Redirect to DM
        return await message.reply_text(
            f"{e(_E_LOCK, '🔒')} <b>sᴛʀɪɴɢ ɢᴇɴᴇʀᴀᴛᴏʀ ᴍᴜsᴛ ʙᴇ ᴜsᴇᴅ ɪɴ ᴅᴍ ꜰᴏʀ ʏᴏᴜʀ sᴇᴄᴜʀɪᴛʏ!</b>\n\n"
            f"{e(_E_KEY, '🦚')} <a href='https://t.me/{app.username}?start=genstring'>ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ᴏᴘᴇɴ ᴅᴍ →</a>",
            disable_web_page_preview=True,
        )
    _gen_state.pop(message.from_user.id, None)
    await message.reply_text(_GENSTR_MSG, reply_markup=_type_buttons())


@app.on_callback_query(filters.regex(r"^gstr_") & ~BANNED_USERS)
async def genstring_type_cb(client, cb: CallbackQuery):
    action = cb.data[5:]  # strip "gstr_"
    user_id = cb.from_user.id

    if action == "cancel":
        _gen_state.pop(user_id, None)
        return await cb.edit_message_text(
            f"{e(_E_WARN, '🚩')} <b>ᴄᴀɴᴄᴇʟʟᴇᴅ.</b> sᴛʀɪɴɢ ɢᴇɴᴇʀᴀᴛɪᴏɴ ᴀʙᴏʀᴛᴇᴅ."
        )

    if action not in _TYPES:
        return await cb.answer("Unknown type.", show_alert=True)

    await cb.answer()
    _gen_state[user_id] = {"type": action, "step": "api_id"}

    label = _TYPES[action]
    prompt = (
        f"{e(_E_KEY, '🦚')} <b>{label} — sᴛᴇᴩ 1/4</b>\n\n"
        f"{e(_E_STAR, '🌟')} ᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ <b>API_ID</b>\n\n"
        f"<i>ɢᴇᴛ ɪᴛ ꜰʀᴏᴍ <a href='https://my.telegram.org'>my.telegram.org</a></i>"
    )
    await cb.edit_message_text(prompt, disable_web_page_preview=True)


@app.on_message(filters.private & filters.text & ~filters.command([]) & ~BANNED_USERS, group=20)
async def genstring_input(client, message: Message):
    user_id = message.from_user.id
    state = _gen_state.get(user_id)
    if not state:
        return

    step = state.get("step")
    text = message.text.strip()
    label = _TYPES.get(state["type"], "Session")
    stype = state["type"]

    # ── Step 1: API_ID ──
    if step == "api_id":
        if not text.isdigit():
            return await message.reply_text(f"{e(_E_WARN, '🚩')} <b>API_ID ᴍᴜsᴛ ʙᴇ ᴀ ɴᴜᴍʙᴇʀ.</b> ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀɢᴀɪɴ.")
        state["api_id"] = int(text)
        state["step"] = "api_hash"
        return await message.reply_text(
            f"{e(_E_KEY, '🦚')} <b>{label} — sᴛᴇᴩ 2/4</b>\n\n"
            f"{e(_E_STAR, '🌟')} ɴᴏᴡ sᴇɴᴅ ʏᴏᴜʀ <b>API_HASH</b>"
        )

    # ── Step 2: API_HASH ──
    if step == "api_hash":
        state["api_hash"] = text
        state["step"] = "credential"
        if stype == "botstr":
            prompt = (
                f"{e(_E_KEY, '🦚')} <b>{label} — sᴛᴇᴩ 3/4</b>\n\n"
                f"{e(_E_BOT, '✅')} sᴇɴᴅ ʏᴏᴜʀ <b>BOT TOKEN</b>\n\n"
                f"<i>ɢᴇᴛ ɪᴛ ꜰʀᴏᴍ @BotFather</i>"
            )
        else:
            prompt = (
                f"{e(_E_KEY, '🦚')} <b>{label} — sᴛᴇᴩ 3/4</b>\n\n"
                f"{e(_E_STAR, '🌟')} sᴇɴᴅ ʏᴏᴜʀ <b>PHONE NUMBER</b>\n\n"
                f"<i>ɪɴᴄʟᴜᴅᴇ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ ᴇ.ɢ. +911234567890</i>"
            )
        return await message.reply_text(prompt)

    # ── Step 3: Phone / Bot Token ──
    if step == "credential":
        state["credential"] = text
        state["step"] = "generating"
        await message.reply_text(
            f"{e(_E_KEY, '🦚')} <b>ɢᴇɴᴇʀᴀᴛɪɴɢ...</b> ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..."
        )

        if stype == "botstr":
            await _generate_bot_string(client, message, state)
        elif stype in ("pyro1", "pyro2"):
            await _generate_pyro_string(client, message, state)
        elif stype == "telethon":
            await _generate_telethon_string(client, message, state)
        return

    # ── Step 4: OTP / 2FA ──
    if step == "otp":
        state["otp"] = text
        state["step"] = "signing_in"
        await _complete_pyro_signin(client, message, state)
        return

    if step == "tg_otp":
        state["otp"] = text
        state["step"] = "tg_signing_in"
        await _complete_telethon_signin(client, message, state)
        return

    if step == "twofa":
        state["twofa"] = text
        state["step"] = "signing_in_2fa"
        await _complete_pyro_signin(client, message, state, twofa=True)
        return

    if step == "tg_twofa":
        state["twofa"] = text
        state["step"] = "tg_signing_in_2fa"
        await _complete_telethon_signin(client, message, state, twofa=True)
        return


# ── Pyrogram Session Generator ──
async def _generate_pyro_string(client, message: Message, state: dict):
    user_id = message.from_user.id
    api_id = state["api_id"]
    api_hash = state["api_hash"]
    phone = state["credential"]
    label = _TYPES[state["type"]]

    try:
        temp = PyroClient(
            name=f"_genstr_{user_id}",
            api_id=api_id,
            api_hash=api_hash,
            in_memory=True,
            no_updates=True,
        )
        await temp.connect()
        sent = await temp.send_code(phone)
        state["phone_code_hash"] = sent.phone_code_hash
        state["_temp_client"] = temp
        state["step"] = "otp"
        await message.reply_text(
            f"{e(_E_KEY, '🦚')} <b>{label} — sᴛᴇᴩ 4/4</b>\n\n"
            f"{e(_E_STAR, '🌟')} ᴏᴛᴩ sᴇɴᴛ ᴛᴏ ʏᴏᴜʀ ᴛᴇʟᴇɢʀᴀᴍ!\n\n"
            f"<b>ᴩʟᴇᴀsᴇ sᴇɴᴅ ᴛʜᴇ ᴏᴛᴩ ᴄᴏᴅᴇ ᴡɪᴛʜ sᴩᴀᴄᴇs</b>\n"
            f"<i>ᴇxᴀᴍᴩʟᴇ: 1 2 3 4 5</i>"
        )
    except Exception as ex:
        _gen_state.pop(user_id, None)
        await message.reply_text(f"{e(_E_WARN, '🚩')} <b>ᴇʀʀᴏʀ:</b> <code>{ex}</code>")


async def _complete_pyro_signin(client, message: Message, state: dict, twofa: bool = False):
    user_id = message.from_user.id
    temp: PyroClient = state.get("_temp_client")
    label = _TYPES[state["type"]]

    if not temp:
        _gen_state.pop(user_id, None)
        return await message.reply_text(f"{e(_E_WARN, '🚩')} <b>sᴇssɪᴏɴ ᴇxᴩɪʀᴇᴅ.</b> ᴩʟᴇᴀsᴇ ʀᴇsᴛᴀʀᴛ ᴡɪᴛʜ /genstring")

    try:
        if twofa:
            await temp.check_password(state["twofa"])
        else:
            otp = state["otp"].replace(" ", "")
            try:
                await temp.sign_in(
                    phone_number=state["credential"],
                    phone_code_hash=state["phone_code_hash"],
                    phone_code=otp,
                )
            except Exception as ex2:
                err_str = str(ex2).lower()
                if "password" in err_str or "2fa" in err_str or "two" in err_str:
                    state["step"] = "twofa"
                    return await message.reply_text(
                        f"{e(_E_LOCK, '🔒')} <b>2FA ᴇɴᴀʙʟᴇᴅ.</b>\n\n"
                        f"ᴩʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ <b>2FA ᴩᴀssᴡᴏʀᴅ</b>:"
                    )
                raise

        session_string = await temp.export_session_string()
        await temp.disconnect()
        _gen_state.pop(user_id, None)

        await message.reply_text(
            f"{e(_E_DONE, '❤️')} <b>{label} sᴛʀɪɴɢ ɢᴇɴᴇʀᴀᴛᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b>\n\n"
            f"{e(_E_LOCK, '🔒')} <b>ᴋᴇᴇᴩ ᴛʜɪs ᴩʀɪᴠᴀᴛᴇ. ɴᴇᴠᴇʀ sʜᴀʀᴇ ɪᴛ!</b>\n\n"
            f"<code>{session_string}</code>"
        )
    except Exception as ex:
        try:
            await temp.disconnect()
        except Exception:
            pass
        _gen_state.pop(user_id, None)
        await message.reply_text(f"{e(_E_WARN, '🚩')} <b>ᴇʀʀᴏʀ:</b> <code>{ex}</code>\n\nᴜsᴇ /genstring ᴛᴏ ᴛʀʏ ᴀɢᴀɪɴ.")


# ── Bot Session Generator ──
async def _generate_bot_string(client, message: Message, state: dict):
    user_id = message.from_user.id
    api_id = state["api_id"]
    api_hash = state["api_hash"]
    bot_token = state["credential"]

    try:
        temp = PyroClient(
            name=f"_genbot_{user_id}",
            api_id=api_id,
            api_hash=api_hash,
            bot_token=bot_token,
            in_memory=True,
            no_updates=True,
        )
        await temp.start()
        session_string = await temp.export_session_string()
        await temp.stop()
        _gen_state.pop(user_id, None)

        await message.reply_text(
            f"{e(_E_DONE, '❤️')} <b>ʙᴏᴛ sᴇssɪᴏɴ sᴛʀɪɴɢ ɢᴇɴᴇʀᴀᴛᴇᴅ!</b>\n\n"
            f"{e(_E_LOCK, '🔒')} <b>ᴋᴇᴇᴩ ᴛʜɪs ᴩʀɪᴠᴀᴛᴇ. ɴᴇᴠᴇʀ sʜᴀʀᴇ ɪᴛ!</b>\n\n"
            f"<code>{session_string}</code>"
        )
    except Exception as ex:
        _gen_state.pop(user_id, None)
        await message.reply_text(f"{e(_E_WARN, '🚩')} <b>ᴇʀʀᴏʀ:</b> <code>{ex}</code>\n\nᴜsᴇ /genstring ᴛᴏ ᴛʀʏ ᴀɢᴀɪɴ.")


# ── Telethon Session Generator ──
async def _generate_telethon_string(client, message: Message, state: dict):
    user_id = message.from_user.id
    api_id = state["api_id"]
    api_hash = state["api_hash"]
    phone = state["credential"]

    try:
        from telethon import TelegramClient
        from telethon.sessions import StringSession

        tg = TelegramClient(StringSession(), api_id, api_hash)
        await tg.connect()
        result = await tg.send_code_request(phone)
        state["tg_client"] = tg
        state["tg_phone_hash"] = result.phone_code_hash
        state["step"] = "tg_otp"
        await message.reply_text(
            f"{e(_E_BOLT, '⚡')} <b>Telethon — sᴛᴇᴩ 4/4</b>\n\n"
            f"{e(_E_STAR, '🌟')} ᴏᴛᴩ sᴇɴᴛ ᴛᴏ ʏᴏᴜʀ ᴛᴇʟᴇɢʀᴀᴍ!\n\n"
            f"<b>ᴩʟᴇᴀsᴇ sᴇɴᴅ ᴛʜᴇ ᴏᴛᴩ ᴄᴏᴅᴇ ᴡɪᴛʜ sᴩᴀᴄᴇs</b>\n"
            f"<i>ᴇxᴀᴍᴩʟᴇ: 1 2 3 4 5</i>"
        )
    except ImportError:
        _gen_state.pop(user_id, None)
        await message.reply_text(
            f"{e(_E_WARN, '🚩')} <b>Telethon ɪs ɴᴏᴛ ɪɴsᴛᴀʟʟᴇᴅ ᴏɴ ᴛʜɪs sᴇʀᴠᴇʀ.</b>\n\n"
            f"ᴜsᴇ <b>Pyrogram v2</b> ᴏᴘᴛɪᴏɴ ɪɴsᴛᴇᴀᴅ ᴡʜɪᴄʜ ɪs ᴄᴏᴍᴘᴀᴛɪʙʟᴇ."
        )
    except Exception as ex:
        _gen_state.pop(user_id, None)
        await message.reply_text(f"{e(_E_WARN, '🚩')} <b>ᴇʀʀᴏʀ:</b> <code>{ex}</code>")


async def _complete_telethon_signin(client, message: Message, state: dict, twofa: bool = False):
    user_id = message.from_user.id
    tg = state.get("tg_client")

    if not tg:
        _gen_state.pop(user_id, None)
        return await message.reply_text(f"{e(_E_WARN, '🚩')} <b>sᴇssɪᴏɴ ᴇxᴩɪʀᴇᴅ.</b> ᴜsᴇ /genstring ᴛᴏ ʀᴇsᴛᴀʀᴛ.")

    try:
        from telethon.errors import SessionPasswordNeededError

        if twofa:
            await tg.sign_in(password=state["twofa"])
        else:
            otp = state["otp"].replace(" ", "")
            try:
                await tg.sign_in(
                    phone=state["credential"],
                    code=otp,
                    phone_code_hash=state["tg_phone_hash"],
                )
            except SessionPasswordNeededError:
                state["step"] = "tg_twofa"
                return await message.reply_text(
                    f"{e(_E_LOCK, '🔒')} <b>2FA ᴇɴᴀʙʟᴇᴅ.</b>\n\nᴩʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ <b>2FA ᴩᴀssᴡᴏʀᴅ</b>:"
                )

        from telethon.sessions import StringSession
        session_string = StringSession.save(tg.session)
        await tg.disconnect()
        _gen_state.pop(user_id, None)

        await message.reply_text(
            f"{e(_E_DONE, '❤️')} <b>Telethon sᴛʀɪɴɢ ɢᴇɴᴇʀᴀᴛᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b>\n\n"
            f"{e(_E_LOCK, '🔒')} <b>ᴋᴇᴇᴩ ᴛʜɪs ᴩʀɪᴠᴀᴛᴇ. ɴᴇᴠᴇʀ sʜᴀʀᴇ ɪᴛ!</b>\n\n"
            f"<code>{session_string}</code>"
        )
    except Exception as ex:
        try:
            await tg.disconnect()
        except Exception:
            pass
        _gen_state.pop(user_id, None)
        await message.reply_text(f"{e(_E_WARN, '🚩')} <b>ᴇʀʀᴏʀ:</b> <code>{ex}</code>\n\nᴜsᴇ /genstring ᴛᴏ ᴛʀʏ ᴀɢᴀɪɴ.")
