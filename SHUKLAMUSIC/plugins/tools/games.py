# -----------------------------------------------
# 🔸 StrangerMusic Project — Group Games Plugin
# 🔹 Number Bomb, Dice Battle, Russian Roulette
# -----------------------------------------------
import asyncio
import random
import time

from pyrogram import filters
from pyrogram.enums import ButtonStyle
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from SHUKLAMUSIC import app
from config import BANNED_USERS

# ── emoji IDs ──
_E_DICE  = 6073371665381724173
_E_BOMB  = 5978715546865112655
_E_GUN   = 6073117703965511893
_E_JOIN  = 6269140848873574815
_E_ROLL  = 5978869985299142389
_E_STAR  = 6271653280187684816

# ── in-memory game state ──
_dice_games   = {}
_bomb_games   = {}
_roulette_games = {}


def _sc(text: str) -> str:
    table = str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ0123456789"
    )
    return text.translate(table)


# ═══════════════════════════════════════════════
#   🎲  DICE BATTLE
# ═══════════════════════════════════════════════

@app.on_message(filters.command(["dicebattle", "diceroll"]) & filters.group & ~BANNED_USERS)
async def start_dice_battle(client, message: Message):
    chat_id = message.chat.id
    if chat_id in _dice_games:
        return await message.reply_text(f"🎲 {_sc('A Dice Battle is already running!')}")

    _dice_games[chat_id] = {"players": {}, "phase": "joining", "start_time": time.time()}

    join_btn = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text=f"🎲 {_sc('Roll to Join')}",
            callback_data=f"dice_join_{chat_id}",
            style=ButtonStyle.SUCCESS,
            icon_custom_emoji_id=_E_DICE,
        )
    ]])
    msg = await message.reply_text(
        f"🎲 <b>{_sc('Dice Battle Royale!')}</b>\n\n"
        f"{_sc('Tap below to join and roll your dice!')}\n"
        f"⏳ {_sc('Closes in 20 seconds...')}",
        reply_markup=join_btn,
    )
    _dice_games[chat_id]["msg"] = msg
    await asyncio.sleep(20)

    game = _dice_games.pop(chat_id, None)
    if not game:
        return
    players = game["players"]
    if not players:
        return await msg.edit_text(f"😔 {_sc('Nobody joined the Dice Battle!')}")

    ranked = sorted(players.items(), key=lambda x: x[1][1], reverse=True)
    lines = ""
    medals = ["🥇", "🥈", "🥉"]
    for i, (uid, (name, roll)) in enumerate(ranked[:10]):
        medal = medals[i] if i < 3 else f"{i + 1}."
        lines += f"{medal} <b>{name}</b> — rolled <b>{roll}</b>\n"

    winner_name = ranked[0][1][0]
    winner_roll = ranked[0][1][1]
    await msg.edit_text(
        f"🎲 <b>{_sc('Dice Battle Results!')}</b>\n\n{lines}\n"
        f"🏆 {_sc('Winner')}: <b>{winner_name}</b> {_sc('with a roll of')} <b>{winner_roll}</b>! 🎉"
    )


@app.on_callback_query(filters.regex(r"^dice_join_") & ~BANNED_USERS)
async def dice_join_callback(client, callback_query):
    chat_id = int(callback_query.data.split("_")[2])
    game = _dice_games.get(chat_id)
    if not game or game["phase"] != "joining":
        return await callback_query.answer(_sc("The battle is closed!"), show_alert=True)

    user = callback_query.from_user
    if user.id in game["players"]:
        _, roll = game["players"][user.id]
        return await callback_query.answer(f"🎲 {_sc('You already rolled:')} {roll}!", show_alert=True)

    roll = random.randint(1, 6)
    game["players"][user.id] = (user.first_name, roll)
    await callback_query.answer(f"🎲 {_sc('You rolled:')} {roll}!", show_alert=True)


# ═══════════════════════════════════════════════
#   💣  NUMBER BOMB
# ═══════════════════════════════════════════════

@app.on_message(filters.command(["numberbomb", "bomb"]) & filters.group & ~BANNED_USERS)
async def start_number_bomb(client, message: Message):
    chat_id = message.chat.id
    if chat_id in _bomb_games:
        return await message.reply_text(f"💣 {_sc('A Number Bomb game is already active!')}")

    bomb_number = random.randint(1, 20)
    _bomb_games[chat_id] = {
        "bomb": bomb_number,
        "picked": {},
        "order": [],
        "phase": "active",
        "start_time": time.time(),
    }

    rows = []
    for row_start in range(1, 21, 5):
        row = []
        for n in range(row_start, min(row_start + 5, 21)):
            row.append(InlineKeyboardButton(
                text=str(n),
                callback_data=f"bomb_pick_{chat_id}_{n}",
                style=ButtonStyle.PRIMARY,
            ))
        rows.append(row)

    msg = await message.reply_text(
        f"💣 <b>{_sc('Number Bomb!')}</b>\n\n"
        f"{_sc('Pick a number from 1 to 20.')}\n"
        f"⚠️ {_sc('One number is the BOMB. Pick it and you LOSE!')}\n\n"
        f"{_sc('Game ends when someone hits the bomb or all safe numbers are picked.')}",
        reply_markup=InlineKeyboardMarkup(rows),
    )
    _bomb_games[chat_id]["msg"] = msg
    await asyncio.sleep(120)
    game = _bomb_games.pop(chat_id, None)
    if game and game["phase"] == "active":
        try:
            await game["msg"].edit_text(
                f"⏰ {_sc('Number Bomb timed out!')}\n💣 {_sc('The bomb was number')} <b>{game['bomb']}</b>!"
            )
        except Exception:
            pass


@app.on_callback_query(filters.regex(r"^bomb_pick_") & ~BANNED_USERS)
async def bomb_pick_callback(client, callback_query):
    parts = callback_query.data.split("_")
    chat_id, number = int(parts[2]), int(parts[3])
    game = _bomb_games.get(chat_id)
    if not game or game["phase"] != "active":
        return await callback_query.answer(_sc("No active bomb game!"), show_alert=True)

    user = callback_query.from_user
    if user.id in game["picked"].values():
        return await callback_query.answer(_sc("You already picked a number!"), show_alert=True)

    if number in game["picked"]:
        return await callback_query.answer(_sc("That number is already taken! Pick another."), show_alert=True)

    game["picked"][number] = user.id
    game["order"].append((user.first_name, number))

    if number == game["bomb"]:
        game["phase"] = "ended"
        _bomb_games.pop(chat_id, None)
        picks_txt = "\n".join(f"• {name}: {n}" for name, n in game["order"][:-1]) or _sc("Nobody else picked.")
        await callback_query.answer(f"💥 BOOM! You hit the bomb!", show_alert=True)
        try:
            await game["msg"].edit_text(
                f"💥 <b>{_sc('BOOM!')}</b> <b>{user.first_name}</b> {_sc('hit the bomb and LOST!')}\n\n"
                f"💣 {_sc('Bomb was number')} <b>{game['bomb']}</b>\n\n"
                f"{_sc('Safe picks before explosion:')}\n{picks_txt}"
            )
        except Exception:
            pass
    else:
        remaining = 20 - len(game["picked"])
        await callback_query.answer(f"✅ Safe! {remaining} numbers left.", show_alert=True)
        if remaining == 0:
            game["phase"] = "ended"
            _bomb_games.pop(chat_id, None)
            try:
                await game["msg"].edit_text(
                    f"🎉 {_sc('All numbers picked safely!')} 💣 {_sc('Bomb was')} <b>{game['bomb']}</b> — "
                    f"{_sc('but it was never touched! Everyone survives!')}"
                )
            except Exception:
                pass


# ═══════════════════════════════════════════════
#   🎡  RUSSIAN ROULETTE
# ═══════════════════════════════════════════════

@app.on_message(filters.command(["roulette", "russianroulette"]) & filters.group & ~BANNED_USERS)
async def start_roulette(client, message: Message):
    chat_id = message.chat.id
    if chat_id in _roulette_games:
        return await message.reply_text(f"🎡 {_sc('A Roulette game is already running!')}")

    bullet_pos = random.randint(1, 6)
    _roulette_games[chat_id] = {
        "bullet": bullet_pos,
        "chamber": 0,
        "players": [],
        "phase": "joining",
        "start_time": time.time(),
    }

    join_btn = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text=f"🎡 {_sc('Join Roulette')}",
            callback_data=f"roulette_join_{chat_id}",
            style=ButtonStyle.DANGER,
            icon_custom_emoji_id=_E_GUN,
        )
    ]])
    msg = await message.reply_text(
        f"🎡 <b>{_sc('Russian Roulette!')}</b>\n\n"
        f"🔫 {_sc('6 chambers, 1 bullet. Players take turns pulling the trigger.')}\n"
        f"💀 {_sc('The player who gets the bullet is eliminated!')}\n\n"
        f"⏳ {_sc('Join now — starting in 20 seconds...')}",
        reply_markup=join_btn,
    )
    _roulette_games[chat_id]["msg"] = msg
    await asyncio.sleep(20)

    game = _roulette_games.get(chat_id)
    if not game:
        return
    if len(game["players"]) < 2:
        _roulette_games.pop(chat_id, None)
        return await msg.edit_text(f"😔 {_sc('Need at least 2 players for Roulette!')}")

    game["phase"] = "playing"
    names = ", ".join(p[1] for p in game["players"])
    pull_btn = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text=f"🔫 {_sc('Pull the Trigger')}",
            callback_data=f"roulette_pull_{chat_id}",
            style=ButtonStyle.DANGER,
            icon_custom_emoji_id=_E_GUN,
        )
    ]])
    turn_user = game["players"][0]
    await msg.edit_text(
        f"🎡 <b>{_sc('Roulette Started!')}</b>\n\n"
        f"{_sc('Players')}: {names}\n\n"
        f"🔫 {_sc('First up')}: <b>{turn_user[1]}</b> — {_sc('pull the trigger!')}",
        reply_markup=pull_btn,
    )


@app.on_callback_query(filters.regex(r"^roulette_join_") & ~BANNED_USERS)
async def roulette_join_callback(client, callback_query):
    chat_id = int(callback_query.data.split("_")[2])
    game = _roulette_games.get(chat_id)
    if not game or game["phase"] != "joining":
        return await callback_query.answer(_sc("Joining is closed!"), show_alert=True)

    user = callback_query.from_user
    if any(p[0] == user.id for p in game["players"]):
        return await callback_query.answer(_sc("You already joined!"), show_alert=True)

    game["players"].append((user.id, user.first_name))
    await callback_query.answer(f"🎡 {_sc('You joined the roulette!')}", show_alert=True)


@app.on_callback_query(filters.regex(r"^roulette_pull_") & ~BANNED_USERS)
async def roulette_pull_callback(client, callback_query):
    chat_id = int(callback_query.data.split("_")[2])
    game = _roulette_games.get(chat_id)
    if not game or game["phase"] != "playing":
        return await callback_query.answer(_sc("No active roulette!"), show_alert=True)

    user = callback_query.from_user
    current_player = game["players"][0]
    if user.id != current_player[0]:
        return await callback_query.answer(
            f"⏳ {_sc('Wait for')} {current_player[1]} {_sc('to pull first!')}",
            show_alert=True,
        )

    game["chamber"] += 1
    if game["chamber"] == game["bullet"]:
        game["phase"] = "ended"
        _roulette_games.pop(chat_id, None)
        survivors = [p[1] for p in game["players"][1:]]
        survivors_txt = ", ".join(survivors) if survivors else _sc("Nobody survived")
        await callback_query.answer("💀 BANG! You're eliminated!", show_alert=True)
        try:
            await callback_query.message.edit_text(
                f"💀 <b>BANG!</b> <b>{user.first_name}</b> {_sc('pulled the trigger and got ELIMINATED!')}\n\n"
                f"🏆 {_sc('Survivors')}: {survivors_txt}"
            )
        except Exception:
            pass
    else:
        game["players"].pop(0)
        game["players"].append(current_player)
        if len(game["players"]) == 1:
            game["phase"] = "ended"
            winner = game["players"][0]
            _roulette_games.pop(chat_id, None)
            await callback_query.answer("✅ Click!", show_alert=True)
            try:
                await callback_query.message.edit_text(
                    f"🏆 <b>{_sc('Roulette Over!')}</b>\n\n"
                    f"🎉 <b>{winner[1]}</b> {_sc('is the last survivor!')}"
                )
            except Exception:
                pass
            return

        remaining = 6 - game["chamber"]
        next_player = game["players"][0]
        pull_btn = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                text=f"🔫 {_sc('Pull the Trigger')}",
                callback_data=f"roulette_pull_{chat_id}",
                style=ButtonStyle.DANGER,
                icon_custom_emoji_id=_E_GUN,
            )
        ]])
        await callback_query.answer(f"✅ Click! Safe... {remaining} chambers left.", show_alert=True)
        try:
            await callback_query.message.edit_text(
                f"🎡 <b>{_sc('Chamber')} {game['chamber']}/6 — Click!</b>\n\n"
                f"😅 <b>{user.first_name}</b> {_sc('survived!')}\n\n"
                f"🔫 {_sc('Next')}: <b>{next_player[1]}</b> — {_sc('your turn!')}",
                reply_markup=pull_btn,
            )
        except Exception:
            pass
