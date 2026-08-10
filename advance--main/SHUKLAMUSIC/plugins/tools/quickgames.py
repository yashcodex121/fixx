# ──────────────────────────────────────────────────────────────
# 🎮 SHUKLAMUSIC — Quick Group Games
#    • ⚡ Tap Race   — first tap wins coins
#    • 🎰 Slot Machine — spin for matching emojis
#    • 🔥 Hot or Not — group votes on a topic
# ──────────────────────────────────────────────────────────────
import asyncio
import random
import time

from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from SHUKLAMUSIC import app
from SHUKLAMUSIC.core.mongo import mongodb
from config import BANNED_USERS

# Reuse the existing wordgame_leaderboard collection (avoid creating new
# collections — MongoDB Atlas free tier has a 500-collection hard limit).
# Quick-game coin records are tagged with game_type="quickgame" so they
# don't clash with word-game records which have no game_type field.
_coins_db = mongodb["wordgame_leaderboard"]

_GTYPE = "quickgame"


async def _add_coins(user_id: int, name: str, amount: int):
    existing = await _coins_db.find_one({"user_id": user_id, "game_type": _GTYPE})
    if existing:
        await _coins_db.update_one(
            {"user_id": user_id, "game_type": _GTYPE},
            {"$inc": {"points": amount}, "$set": {"name": name}},
        )
    else:
        await _coins_db.insert_one(
            {"user_id": user_id, "name": name, "points": amount, "game_type": _GTYPE}
        )


async def _get_coins(user_id: int) -> int:
    doc = await _coins_db.find_one({"user_id": user_id, "game_type": _GTYPE})
    return doc["points"] if doc else 0

# ── in-memory state ─────────────────────────────────────────
_tap_games   = {}   # chat_id → {phase, winner, start_time, msg}
_slot_games  = {}   # chat_id → {players: {uid: spins}, msg, start_time}
_hot_games   = {}   # chat_id → {topic, votes: {uid: choice}, msg, start_time}

# ── coin rewards ─────────────────────────────────────────────
TAP_WIN_COINS   = 20
SLOT_JACKPOT    = 50
SLOT_TWO_MATCH  = 15
SLOT_NO_MATCH   = 0
HOT_WIN_COINS   = 10   # majority side earns coins

# ── slot emoji pools ─────────────────────────────────────────
SLOT_REELS = ["🍋", "🍊", "🍇", "🍓", "💎", "⭐", "🎰", "7️⃣"]

# ── hot-or-not topic pool ────────────────────────────────────
HOT_TOPICS = [
    "Pineapple on pizza 🍕",
    "Waking up at 5 AM ⏰",
    "Rainy days 🌧️",
    "Skipping breakfast 🍳",
    "Cold showers 🚿",
    "Horror movies 🎬",
    "Working on weekends 💼",
    "Cats > Dogs 🐱",
    "Dark mode always 🌙",
    "Spicy food 🌶️",
    "Gym at midnight 🏋️",
    "Talking on phone vs texting 📱",
    "Peanut butter with everything 🥜",
    "Silence over music 🤫",
    "Online friends > real friends 💻",
    "Sleeping with AC on max ❄️",
    "Skipping ads 📺",
    "Late night snacks 🌙🍟",
    "Singing alone in the car 🎤",
    "Living in a small town 🏘️",
]


def e(eid: int, fb: str) -> str:
    return f"<emoji id={eid}>{fb}</emoji>"


# ════════════════════════════════════════════════════════════
#  ⚡  TAP RACE
# ════════════════════════════════════════════════════════════

@app.on_message(filters.command(["taprace", "tapnow", "tapgame"]) & filters.group & ~BANNED_USERS)
async def cmd_tap_race(client, message: Message):
    chat_id = message.chat.id
    if chat_id in _tap_games:
        return await message.reply_text("⚡ A Tap Race is already running!")

    _tap_games[chat_id] = {"phase": "countdown", "winner": None, "start_time": None}

    msg = await message.reply_text(
        "⚡ <b>TAP RACE — GET READY!</b>\n\n"
        "🟡 Starting in <b>3 seconds...</b>\n\n"
        "<i>First one to tap the button wins coins!</i>"
    )
    _tap_games[chat_id]["msg"] = msg

    await asyncio.sleep(3)

    if chat_id not in _tap_games:
        return  # cancelled

    _tap_games[chat_id]["phase"] = "active"
    _tap_games[chat_id]["start_time"] = time.time()

    try:
        await msg.edit_text(
            "⚡ <b>TAP NOW! TAP NOW! TAP NOW!</b> 🎯\n\n"
            "👇 <b>FIRST TO TAP WINS!</b> 👇",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⚡  T A P  N O W !  ⚡", callback_data=f"taprace_tap_{chat_id}")
            ]])
        )
    except Exception:
        _tap_games.pop(chat_id, None)
        return

    # Auto-expire after 30 seconds
    async def expire():
        await asyncio.sleep(30)
        game = _tap_games.pop(chat_id, None)
        if game and game["winner"] is None:
            try:
                await msg.edit_text("⚡ <b>Tap Race expired!</b> Nobody was fast enough 😴")
            except Exception:
                pass
    asyncio.get_event_loop().create_task(expire())


@app.on_callback_query(filters.regex(r"^taprace_tap_") & ~BANNED_USERS)
async def tap_race_cb(client, cb: CallbackQuery):
    chat_id = int(cb.data.split("_")[2])
    game = _tap_games.get(chat_id)

    if not game or game["phase"] != "active":
        return await cb.answer("⚡ Too slow! The race is over.", show_alert=True)

    if game.get("winner"):
        return await cb.answer("😅 Someone already won!", show_alert=True)

    # First tap wins — atomic claim
    game["winner"] = cb.from_user.id
    game["phase"] = "done"
    _tap_games.pop(chat_id, None)

    elapsed = round(time.time() - game["start_time"], 2)
    winner_name = cb.from_user.first_name

    await _add_coins(cb.from_user.id, cb.from_user.first_name, TAP_WIN_COINS)
    coins_now = await _get_coins(cb.from_user.id)

    await cb.answer(f"⚡ YOU WON! +{TAP_WIN_COINS} coins!", show_alert=True)
    try:
        await cb.message.edit_text(
            f"⚡ <b>TAP RACE RESULT!</b>\n\n"
            f"🏆 Winner: <b>{winner_name}</b>\n"
            f"⏱ Speed: <b>{elapsed}s</b>\n"
            f"💰 Reward: <b>+{TAP_WIN_COINS} coins</b>\n"
            f"💳 Balance: <b>{coins_now} coins</b>\n\n"
            f"<i>Play again with /taprace</i>"
        )
    except Exception:
        pass


# ════════════════════════════════════════════════════════════
#  🎰  SLOT MACHINE
# ════════════════════════════════════════════════════════════

def _spin_reels():
    return [random.choice(SLOT_REELS) for _ in range(3)]


def _slot_result(reels):
    if reels[0] == reels[1] == reels[2]:
        return SLOT_JACKPOT, "🎰 JACKPOT!! All 3 match!"
    if reels[0] == reels[1] or reels[1] == reels[2] or reels[0] == reels[2]:
        return SLOT_TWO_MATCH, "✨ Two match! Nice!"
    return SLOT_NO_MATCH, "😔 No match this time."


def _slot_markup(chat_id):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🎰  S P I N !  🎰", callback_data=f"slot_spin_{chat_id}")
    ]])


@app.on_message(filters.command(["slots", "slotmachine", "spin"]) & filters.group & ~BANNED_USERS)
async def cmd_slots(client, message: Message):
    chat_id = message.chat.id
    if chat_id in _slot_games:
        return await message.reply_text("🎰 A Slot game is already running! Click SPIN to join.")

    _slot_games[chat_id] = {
        "players": {},
        "start_time": time.time(),
        "results": [],
    }

    msg = await message.reply_text(
        "🎰 <b>SLOT MACHINE!</b>\n\n"
        f"💎 Jackpot (3 match): <b>+{SLOT_JACKPOT} coins</b>\n"
        f"✨ Two match: <b>+{SLOT_TWO_MATCH} coins</b>\n"
        f"😔 No match: <b>+0 coins</b>\n\n"
        "👇 Tap SPIN to play! Everyone gets one spin.",
        reply_markup=_slot_markup(chat_id),
    )
    _slot_games[chat_id]["msg"] = msg

    # Auto-close after 60s
    async def close_slots():
        await asyncio.sleep(60)
        game = _slot_games.pop(chat_id, None)
        if not game:
            return
        results = game.get("results", [])
        if not results:
            try:
                await msg.edit_text("🎰 Slot Machine closed — nobody played!", reply_markup=None)
            except Exception:
                pass
            return
        summary = "\n".join(results[-8:])  # last 8 results
        try:
            await msg.edit_text(
                f"🎰 <b>SLOT MACHINE CLOSED!</b>\n\n{summary}\n\n<i>Play again with /slots</i>",
                reply_markup=None,
            )
        except Exception:
            pass

    asyncio.get_event_loop().create_task(close_slots())


@app.on_callback_query(filters.regex(r"^slot_spin_") & ~BANNED_USERS)
async def slot_spin_cb(client, cb: CallbackQuery):
    chat_id = int(cb.data.split("_")[2])
    game = _slot_games.get(chat_id)

    if not game:
        return await cb.answer("🎰 This slot game is over.", show_alert=True)

    user_id = cb.from_user.id
    if user_id in game["players"]:
        return await cb.answer("😅 You already spun! Wait for the next game.", show_alert=True)

    game["players"][user_id] = True

    reels = _spin_reels()
    coins, verdict = _slot_result(reels)

    if coins > 0:
        await _add_coins(user_id, cb.from_user.first_name, coins)

    display = " ".join(reels)
    name = cb.from_user.first_name
    result_line = f"• <b>{name}</b>: {display} — {verdict} (+{coins}c)"
    game["results"].append(result_line)

    await cb.answer(f"{display}  {verdict}  +{coins} coins!", show_alert=True)

    # Update message to show latest result
    recent = "\n".join(game["results"][-5:])
    try:
        await cb.message.edit_text(
            f"🎰 <b>SLOT MACHINE</b> — tap to play!\n\n"
            f"{recent}\n\n"
            f"💎 3-match = +{SLOT_JACKPOT}c  ✨ 2-match = +{SLOT_TWO_MATCH}c",
            reply_markup=_slot_markup(chat_id),
        )
    except Exception:
        pass


# ════════════════════════════════════════════════════════════
#  🔥  HOT OR NOT
# ════════════════════════════════════════════════════════════

def _hot_markup(chat_id):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🔥  HOT", callback_data=f"hot_vote_{chat_id}_hot"),
        InlineKeyboardButton("❄️  NOT", callback_data=f"hot_vote_{chat_id}_not"),
    ]])


def _hot_bar(hot: int, not_: int) -> str:
    total = hot + not_
    if total == 0:
        return "🔥 0%  |  ❄️ 0%"
    hp = round(hot / total * 100)
    np = 100 - hp
    hb = "█" * (hp // 10)
    nb = "█" * (np // 10)
    return f"🔥 {hp}% {hb}  |  {nb} {np}% ❄️"


@app.on_message(filters.command(["hotvote", "hotnot", "hotornot"]) & filters.group & ~BANNED_USERS)
async def cmd_hot_vote(client, message: Message):
    chat_id = message.chat.id
    if chat_id in _hot_games:
        return await message.reply_text("🔥 A Hot or Not vote is already running!")

    topic = random.choice(HOT_TOPICS)
    _hot_games[chat_id] = {
        "topic": topic,
        "votes": {},
        "start_time": time.time(),
    }

    msg = await message.reply_text(
        f"🔥 <b>HOT OR NOT?</b>\n\n"
        f"📢 Topic: <b>{topic}</b>\n\n"
        f"{_hot_bar(0, 0)}\n"
        f"<i>Vote closes in 30 seconds!</i>",
        reply_markup=_hot_markup(chat_id),
    )
    _hot_games[chat_id]["msg"] = msg

    # Close after 30s and reward majority
    async def close_vote():
        await asyncio.sleep(30)
        game = _hot_games.pop(chat_id, None)
        if not game:
            return

        votes = game["votes"]
        hot_voters = [uid for uid, v in votes.items() if v == "hot"]
        not_voters = [uid for uid, v in votes.items() if v == "not"]
        hot_count = len(hot_voters)
        not_count = len(not_voters)

        if hot_count == not_count:
            result_text = "🤝 <b>It's a TIE!</b> No coins awarded."
        else:
            if hot_count > not_count:
                winners = hot_voters
                side_emoji, side_label = "🔥", "HOT"
            else:
                winners = not_voters
                side_emoji, side_label = "❄️", "NOT"

            for uid in winners:
                await _add_coins(uid, str(uid), HOT_WIN_COINS)

            result_text = (
                f"{side_emoji} <b>{side_label} wins!</b>\n"
                f"🏆 {len(winners)} voter(s) each won <b>+{HOT_WIN_COINS} coins</b>!"
            )

        bar = _hot_bar(hot_count, not_count)
        try:
            await msg.edit_text(
                f"🔥 <b>HOT OR NOT — RESULTS!</b>\n\n"
                f"📢 Topic: <b>{game['topic']}</b>\n\n"
                f"{bar}\n"
                f"🔥 Hot: <b>{hot_count}</b>  |  ❄️ Not: <b>{not_count}</b>\n\n"
                f"{result_text}\n\n"
                f"<i>Play again with /hotvote</i>",
                reply_markup=None,
            )
        except Exception:
            pass

    asyncio.get_event_loop().create_task(close_vote())


@app.on_callback_query(filters.regex(r"^hot_vote_") & ~BANNED_USERS)
async def hot_vote_cb(client, cb: CallbackQuery):
    parts = cb.data.split("_")
    chat_id = int(parts[2])
    choice = parts[3]  # "hot" or "not"

    game = _hot_games.get(chat_id)
    if not game:
        return await cb.answer("🔥 This vote is already closed.", show_alert=True)

    user_id = cb.from_user.id
    prev = game["votes"].get(user_id)

    if prev == choice:
        return await cb.answer(
            f"{'🔥 HOT' if choice == 'hot' else '❄️ NOT'} already recorded!", show_alert=False
        )

    game["votes"][user_id] = choice

    hot_count = sum(1 for v in game["votes"].values() if v == "hot")
    not_count = sum(1 for v in game["votes"].values() if v == "not")

    label = "🔥 HOT" if choice == "hot" else "❄️ NOT"
    await cb.answer(f"{label} vote recorded!", show_alert=False)

    try:
        await cb.message.edit_text(
            f"🔥 <b>HOT OR NOT?</b>\n\n"
            f"📢 Topic: <b>{game['topic']}</b>\n\n"
            f"{_hot_bar(hot_count, not_count)}\n"
            f"🔥 {hot_count}  |  ❄️ {not_count}\n\n"
            f"<i>Vote closes in 30 seconds!</i>",
            reply_markup=_hot_markup(chat_id),
        )
    except Exception:
        pass
