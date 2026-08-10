# -----------------------------------------------
# 🔸 StrangerMusic Project — ChatFight Mini-Games
# 🔹 Word / Emoji / Flag guessing games with MongoDB leaderboard
# 🔹 Adapted from SUDEEPBOTS chatfight.py for SHUKLAMUSIC
# -----------------------------------------------
import time
import asyncio
import os
import random
from PIL import Image, ImageDraw, ImageFont
from pyrogram import filters
from pyrogram.enums import ButtonStyle
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from SHUKLAMUSIC import app
from SHUKLAMUSIC.core.mongo import mongodb
from config import BANNED_USERS

game_db = mongodb["wordgame_leaderboard"]

last_message_time = {}
active_games = {}
user_cooldowns = {}
INACTIVITY_LIMIT = 300
PENALTY_TIME = 60
_INACTIVITY_STARTED = False

TEMPLATE_PATH = "SHUKLAMUSIC/assets/template.jpg"
FONT_PATH = "SHUKLAMUSIC/assets/font.ttf"

# ── Premium emoji IDs used for ChatFight (ll_MR_DEVIL_KING_ll_by_fStikBot / PRISHU_BABU / emoji_2e47b packs) ──
_E_GIVEUP = 5978715546865112655   # 🚩
_E_WIN = 5978869985299142389      # 🦚
_E_CLAIM = 6269140848873574815    # ❤️
_E_TROPHY = 6271653280187684816   # 🌟
_E_TIMER = 6073598306510967017    # ⏱ (🐈 slot repurposed as timer accent)
_E_FUN = 6073371665381724173      # 🥰


def smallcaps(text):
    chars = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ', 'g': 'ɢ',
        'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ',
        'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ',
        'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ',
    }
    return ''.join(chars.get(c.lower(), c) for c in str(text))


WARNING_MESSAGES = [
    f"⏱ {smallcaps('Time passes. Tick tock, tick tock...')}",
    f"⚠️ {smallcaps('Alarm: time is running out!!')}",
    f"🥱 {smallcaps('It is too quiet here... let us play a game!')}",
    f"👀 {smallcaps('Anyone there? Get ready to type...')}",
]

EMOJIS = ["🍏", "🍎", "🍐", "🍊", "🍋", "🍌", "🍉", "🍇", "🍓", "🫐", "🍈", "🍒", "🍑", "🥭", "🍍",
          "🥥", "🥝", "🍅", "🍆", "🥑", "🥦", "🥬", "🥒", "🌶", "🌽", "🥕", "🥔", "🍠", "🥐", "🥯",
          "🍞", "🥖", "🥨", "🧀", "🥚", "🍳", "🧈", "🥞", "🧇", "🥓", "🥩", "🍗", "🍖", "🌭", "🍔",
          "🍟", "🍕", "🥪", "🥙", "🌮", "🌯", "🥗", "🥘", "🥫", "🍝", "🍜", "🍲", "🍛", "🍣", "🍱",
          "🥟", "🍤", "🍙", "🍚", "🍘", "🍥", "🥮", "🍢"]

COUNTRIES = [
    {"name": "India", "code": "in"}, {"name": "USA", "code": "us"}, {"name": "Japan", "code": "jp"},
    {"name": "Brazil", "code": "br"}, {"name": "Canada", "code": "ca"}, {"name": "UK", "code": "gb"},
    {"name": "France", "code": "fr"}, {"name": "Germany", "code": "de"}, {"name": "Italy", "code": "it"},
    {"name": "Russia", "code": "ru"}, {"name": "China", "code": "cn"}, {"name": "Australia", "code": "au"},
    {"name": "Spain", "code": "es"}, {"name": "Mexico", "code": "mx"}, {"name": "South Korea", "code": "kr"},
]

WORD_BANK = [
    "BACTERIAL", "GAMUT", "PANDEMIC", "AESTHETIC", "RESONATE", "ILLUSION",
    "HORIZON", "DEVELOPER", "SYMPHONY", "GALAXY", "MYSTERY", "VOLCANO",
    "PARADOX", "FESTIVAL", "JOURNEY", "CRYSTAL", "PHOENIX", "WHISPER",
]


PURPLE_TOP = (88, 24, 138)
PURPLE_BOTTOM = (35, 8, 66)
BRAND_TEXT = "RADHA MUSIC"


def _purple_canvas(size=(800, 400)):
    img = Image.new("RGB", size, color=PURPLE_TOP)
    top = PURPLE_TOP
    bottom = PURPLE_BOTTOM
    for y in range(size[1]):
        ratio = y / size[1]
        r = int(top[0] + (bottom[0] - top[0]) * ratio)
        g = int(top[1] + (bottom[1] - top[1]) * ratio)
        b = int(top[2] + (bottom[2] - top[2]) * ratio)
        ImageDraw.Draw(img).line([(0, y), (size[0], y)], fill=(r, g, b))
    return img


def _ensure_template():
    if not os.path.exists(TEMPLATE_PATH):
        os.makedirs(os.path.dirname(TEMPLATE_PATH), exist_ok=True)
        _purple_canvas().save(TEMPLATE_PATH)


def _draw_branding(bg):
    draw = ImageDraw.Draw(bg)
    try:
        brand_font = ImageFont.truetype(FONT_PATH, 34)
    except Exception:
        brand_font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), BRAND_TEXT, font=brand_font)
    text_w = bbox[2] - bbox[0]
    draw.text(
        ((bg.size[0] - text_w) / 2, bg.size[1] - 55),
        BRAND_TEXT,
        fill=(255, 215, 0),
        font=brand_font,
    )
    draw.rectangle([(0, 0), (bg.size[0] - 1, bg.size[1] - 1)], outline=(255, 215, 0), width=4)
    return bg


def create_game_image(text):
    output_path = f"downloads/game_{random.randint(1000, 9999)}.jpg"
    os.makedirs("downloads", exist_ok=True)
    bg = _purple_canvas().convert("RGBA")
    draw = ImageDraw.Draw(bg)
    try:
        font = ImageFont.truetype(FONT_PATH, 65)
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x, y = (bg.size[0] - text_w) / 2, ((bg.size[1] - text_h) / 2) - 30
    draw.text((x, y), text, fill="white", font=font)
    bg = _draw_branding(bg)
    bg = bg.convert("RGB")
    bg.save(output_path)
    return output_path


async def create_emoji_or_flag_image(identifier, is_flag=False):
    import aiohttp
    _ensure_template()
    output_path = f"downloads/game_{random.randint(1000, 9999)}.jpg"
    os.makedirs("downloads", exist_ok=True)
    if is_flag:
        url = f"https://flagcdn.com/256x192/{identifier}.png"
    else:
        hex_code = "-".join(f"{ord(c):x}" for c in identifier).replace("-fe0f", "")
        url = f"https://cdn.jsdelivr.net/gh/jdecked/twemoji@15.0.3/assets/72x72/{hex_code}.png"

    bg = _purple_canvas().convert("RGBA")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    img_bytes = await resp.read()
                    temp_name = f"downloads/temp_{random.randint(100, 999)}.png"
                    with open(temp_name, "wb") as f:
                        f.write(img_bytes)
                    img_layer = Image.open(temp_name).convert("RGBA")
                    if not is_flag:
                        img_layer = img_layer.resize((160, 160), Image.Resampling.LANCZOS)
                    bg.paste(
                        img_layer,
                        ((bg.size[0] - img_layer.size[0]) // 2, ((bg.size[1] - img_layer.size[1]) // 2) - 20),
                        img_layer,
                    )
                    os.remove(temp_name)
    except Exception:
        pass
    bg = _draw_branding(bg)
    bg = bg.convert("RGB")
    bg.save(output_path)
    return output_path


def _start_inactivity_loop():
    global _INACTIVITY_STARTED
    if not _INACTIVITY_STARTED:
        _INACTIVITY_STARTED = True
        asyncio.create_task(inactivity_checker_loop())


async def start_word_game(chat_id):
    try:
        original_word = random.choice(WORD_BANK)
        is_missing = random.choice([True, False])
        display_word = hide_letters(original_word) if is_missing else original_word

        img_path = create_game_image(display_word)
        caption = (
            f"⚡ **{smallcaps('Be the first to write the word shown in the photo!')}**\n\n"
            f"⏱ **{smallcaps('Time remaining: 10 minutes')}**"
        )

        markup = None
        if is_missing:
            markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton(
                    text=f"🏳️ {smallcaps('Give Up')}",
                    callback_data=f"giveup_{chat_id}",
                    style=ButtonStyle.DANGER,
                    icon_custom_emoji_id=_E_GIVEUP,
                )]]
            )

        sent_msg = await app.send_photo(chat_id, photo=img_path, caption=caption, has_spoiler=True, reply_markup=markup)
        if os.path.exists(img_path):
            os.remove(img_path)
        active_games[chat_id] = {"type": "word", "answer": original_word, "start_time": time.time(), "message_id": sent_msg.id}
    except Exception:
        pass


def hide_letters(word):
    num_to_hide = max(1, len(word) // 2)
    indices_to_hide = random.sample(range(len(word)), num_to_hide)
    hidden_word = list(word)
    for i in indices_to_hide:
        hidden_word[i] = "_"
    return "".join(hidden_word)


async def start_emoji_game(chat_id):
    try:
        correct_emoji = random.choice(EMOJIS)
        options = random.sample([e for e in EMOJIS if e != correct_emoji], 11) + [correct_emoji]
        random.shuffle(options)

        img_path = await create_emoji_or_flag_image(correct_emoji, is_flag=False)
        caption = (
            f"👇 **{smallcaps('Identify the emoji in the photo and select it below!')}**\n\n"
            f"⏱ **{smallcaps('Time remaining: 10 minutes')}**"
        )

        rows, row = [], []
        for em in options:
            row.append(InlineKeyboardButton(text=em, callback_data=f"emg_{chat_id}_{em}", style=ButtonStyle.PRIMARY))
            if len(row) == 3:
                rows.append(row)
                row = []
        if row:
            rows.append(row)

        sent_msg = await app.send_photo(chat_id, photo=img_path, caption=caption, has_spoiler=True, reply_markup=InlineKeyboardMarkup(rows))
        if os.path.exists(img_path):
            os.remove(img_path)
        active_games[chat_id] = {"type": "emoji", "answer": correct_emoji, "start_time": time.time(), "message_id": sent_msg.id}
    except Exception:
        pass


async def start_flag_game(chat_id):
    try:
        correct_country = random.choice(COUNTRIES)
        options_pool = [c for c in COUNTRIES if c["code"] != correct_country["code"]]
        options = random.sample(options_pool, min(11, len(options_pool))) + [correct_country]
        random.shuffle(options)

        img_path = await create_emoji_or_flag_image(correct_country["code"], is_flag=True)
        caption = (
            f"🌍 **{smallcaps('Guess the country from its flag and select the correct option!')}**\n\n"
            f"⏱ **{smallcaps('Time remaining: 10 minutes')}**"
        )

        rows, row = [], []
        for c in options:
            row.append(InlineKeyboardButton(
                text=smallcaps(c["name"]),
                callback_data=f"flg_{chat_id}_{c['code']}",
                style=ButtonStyle.PRIMARY,
                icon_custom_emoji_id=_E_WIN,
            ))
            if len(row) == 2:
                rows.append(row)
                row = []
        if row:
            rows.append(row)

        sent_msg = await app.send_photo(chat_id, photo=img_path, caption=caption, has_spoiler=True, reply_markup=InlineKeyboardMarkup(rows))
        if os.path.exists(img_path):
            os.remove(img_path)
        active_games[chat_id] = {
            "type": "flag", "answer": correct_country["code"], "name": correct_country["name"],
            "start_time": time.time(), "message_id": sent_msg.id,
        }
    except Exception:
        pass


async def check_cooldown(user_id, callback_query):
    if user_id in user_cooldowns:
        time_passed = time.time() - user_cooldowns[user_id]
        if time_passed < PENALTY_TIME:
            wait_time = int(PENALTY_TIME - time_passed)
            await callback_query.answer(f"⏳ {smallcaps('Penalty active!')} {wait_time} {smallcaps('seconds remaining.')}", show_alert=True)
            return True
    return False


async def send_claim(client, chat_id, success_text):
    markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(
            text=f"💓 {smallcaps('Play More in DM')}",
            url=f"https://t.me/{app.username}?start=chatfight",
            style=ButtonStyle.SUCCESS,
            icon_custom_emoji_id=_E_CLAIM,
        )]]
    )
    await client.send_message(chat_id, success_text, reply_markup=markup)


@app.on_callback_query(filters.regex(r"^(emg|flg)_") & ~BANNED_USERS)
async def guess_game_callback(client, callback_query):
    user = callback_query.from_user
    if await check_cooldown(user.id, callback_query):
        return

    data = callback_query.data.split("_")
    game_type, chat_id, selected_option = data[0], int(data[1]), data[2]

    if chat_id not in active_games:
        return await callback_query.answer(smallcaps("Game ended or expired!"), show_alert=True)
    game_data = active_games[chat_id]

    if (game_type == "emg" and game_data.get("type") != "emoji") or (game_type == "flg" and game_data.get("type") != "flag"):
        return await callback_query.answer(smallcaps("Invalid game interaction!"), show_alert=True)

    if selected_option == game_data["answer"]:
        # Atomically remove the game so only the first correct clicker wins
        won_game = active_games.pop(chat_id, None)
        if won_game is None:
            # Game was claimed by someone else between the check and now
            return await callback_query.answer(
                f"😔 {smallcaps('Someone else claimed it first! Next game coming up...')}",
                show_alert=True
            )

        time_taken = round(time.time() - won_game["start_time"], 1)
        points_won = 3 if game_type == "emg" else 5
        game_name_str = "emoji" if game_type == "emg" else won_game.get("name", "flag")

        success_text = (
            f"🎉 **{smallcaps(f'The {game_name_str} was guessed correctly by')} {user.mention} "
            f"{smallcaps(f'in {time_taken} seconds!')}**\n*+{points_won} {smallcaps('coins')}*"
        )

        try:
            await callback_query.message.delete()
        except Exception:
            pass

        try:
            user_data = await game_db.find_one({"user_id": user.id})
            if user_data:
                await game_db.update_one(
                    {"user_id": user.id},
                    {"$set": {"points": user_data["points"] + points_won, "name": user.first_name}}
                )
            else:
                await game_db.insert_one({"user_id": user.id, "name": user.first_name, "points": points_won})
        except Exception:
            pass

        await callback_query.answer(f"✅ {smallcaps(f'Correct! +{points_won} coins!')}", show_alert=True)
        await send_claim(client, chat_id, success_text)
    else:
        user_cooldowns[user.id] = time.time()
        await callback_query.answer(f"❌ {smallcaps('Wrong answer! You have a 1-minute penalty.')}", show_alert=True)


@app.on_callback_query(filters.regex(r"^giveup_") & ~BANNED_USERS)
async def giveup_callback(client, callback_query):
    data = callback_query.data.split("_")
    chat_id = int(data[1])

    if chat_id not in active_games or active_games[chat_id].get("type") != "word":
        return await callback_query.answer(smallcaps("Game already ended!"), show_alert=True)

    correct_word = active_games[chat_id]["answer"]
    del active_games[chat_id]
    try:
        await callback_query.message.delete()
    except Exception:
        pass
    await client.send_message(
        chat_id,
        f"🏳️ **{smallcaps('Game Over!')}** {callback_query.from_user.mention} {smallcaps('gave up.')}\n\n"
        f"{smallcaps('The correct word was:')} **{correct_word}**",
    )


@app.on_message(filters.command(["wordgame", "cfword"]) & filters.group & ~BANNED_USERS)
async def cmd_word_game(client, message: Message):
    _start_inactivity_loop()
    if message.chat.id in active_games:
        return await message.reply_text(smallcaps("A game is already running in this chat!"))
    await start_word_game(message.chat.id)


@app.on_message(filters.command(["emojigame", "cfemoji"]) & filters.group & ~BANNED_USERS)
async def cmd_emoji_game(client, message: Message):
    _start_inactivity_loop()
    if message.chat.id in active_games:
        return await message.reply_text(smallcaps("A game is already running in this chat!"))
    await start_emoji_game(message.chat.id)


@app.on_message(filters.command(["flaggame", "cfflag"]) & filters.group & ~BANNED_USERS)
async def cmd_flag_game(client, message: Message):
    _start_inactivity_loop()
    if message.chat.id in active_games:
        return await message.reply_text(smallcaps("A game is already running in this chat!"))
    await start_flag_game(message.chat.id)


@app.on_message(filters.group & filters.text & ~filters.bot & ~BANNED_USERS, group=10)
async def chat_activity_tracker(client, message: Message):
    chat_id = message.chat.id
    if not message.from_user:
        return
    user_id = message.from_user.id
    last_message_time[chat_id] = time.time()

    if chat_id in active_games and active_games[chat_id].get("type") == "word" and message.text:
        correct_word = active_games[chat_id]["answer"]
        if message.text.strip().upper() == correct_word:
            time_taken = round(time.time() - active_games[chat_id]["start_time"], 1)
            del active_games[chat_id]
            try:
                await client.send_reaction(chat_id=chat_id, message_id=message.id, emoji="❤️")
            except Exception:
                pass

            user_data = await game_db.find_one({"user_id": user_id})
            if user_data:
                await game_db.update_one({"user_id": user_id}, {"$set": {"points": user_data["points"] + 15, "name": message.from_user.first_name}})
            else:
                await game_db.insert_one({"user_id": user_id, "name": message.from_user.first_name, "points": 15})

            msg = (
                f"⚡ **{smallcaps('How fast!')}** ({time_taken} {smallcaps('seconds')})\n"
                f"🎉 {message.from_user.mention} {smallcaps('guessed the word in record time!')}\n"
                f"{smallcaps('Correct Word:')} **{correct_word}**\n*+15 {smallcaps('in the global game ranking')}*"
            )
            await send_claim(client, chat_id, msg)


@app.on_message(filters.command(["wordleaderboard", "gametop", "cflb"]) & ~BANNED_USERS)
async def word_leaderboard(client, message: Message):
    top_users = game_db.find().sort("points", -1).limit(10)
    text = f"🏆 **{smallcaps('ChatFight Global Leaderboard')}** 🏆\n\n"
    count, has_users = 1, False
    async for user in top_users:
        has_users = True
        text += f"**{count}.** {smallcaps(user.get('name', 'Unknown User'))} - `{user['points']}` {smallcaps('points')}\n"
        count += 1
    if not has_users:
        text += smallcaps("No one has scored points yet! Start a game with /wordgame, /emojigame or /flaggame.")
    await message.reply_text(text)


async def inactivity_checker_loop():
    while True:
        await asyncio.sleep(60)
        current_time = time.time()
        for chat_id, game_data in list(active_games.items()):
            if (current_time - game_data["start_time"]) > 600:
                try:
                    await app.delete_messages(chat_id, game_data["message_id"])
                except Exception:
                    pass
                del active_games[chat_id]
                if chat_id in last_message_time:
                    del last_message_time[chat_id]

        for chat_id, last_time in list(last_message_time.items()):
            if (current_time - last_time) > INACTIVITY_LIMIT and chat_id not in active_games:
                try:
                    warning = await app.send_message(chat_id, random.choice(WARNING_MESSAGES))
                    await asyncio.sleep(3)
                    await warning.delete()
                    game_choice = random.choice(["word", "emoji", "flag"])
                    if game_choice == "word":
                        await start_word_game(chat_id)
                    elif game_choice == "emoji":
                        await start_emoji_game(chat_id)
                    else:
                        await start_flag_game(chat_id)
                except Exception:
                    pass


# =====================================================================
# 🏆 LEGENDARY GAME — Trivia Battle Royale (full-group multiplayer quiz)
# =====================================================================
trivia_db = mongodb["trivia_leaderboard"]
active_battles = {}

_E_JOIN = 6269140848873574815     # ❤️
_E_START = 5978869985299142389    # 🦚
_E_A = 6073371665381724173        # 🥰
_E_B = 6073598306510967017        # 🐈
_E_C = 6073117703965511893        # 💐
_E_D = 5978715546865112655        # 🚩
_E_CROWN = 6271653280187684816    # 🌟

TRIVIA_QUESTIONS = [
    ("Which planet is known as the Red Planet?", ["Venus", "Mars", "Jupiter", "Saturn"], 1),
    ("What is the capital of Japan?", ["Seoul", "Beijing", "Tokyo", "Bangkok"], 2),
    ("Who painted the Mona Lisa?", ["Van Gogh", "Picasso", "Da Vinci", "Monet"], 2),
    ("How many continents are there on Earth?", ["5", "6", "7", "8"], 2),
    ("What is the largest ocean on Earth?", ["Atlantic", "Indian", "Arctic", "Pacific"], 3),
    ("Which gas do plants absorb from the atmosphere?", ["Oxygen", "Carbon Dioxide", "Nitrogen", "Hydrogen"], 1),
    ("What is the fastest land animal?", ["Lion", "Cheetah", "Horse", "Leopard"], 1),
    ("Which country invented pizza?", ["France", "Spain", "Italy", "Greece"], 2),
    ("How many strings does a standard guitar have?", ["4", "5", "6", "7"], 2),
    ("What is the smallest prime number?", ["0", "1", "2", "3"], 2),
    ("Which language has the most native speakers worldwide?", ["English", "Spanish", "Mandarin", "Hindi"], 2),
    ("What is the currency of Japan?", ["Won", "Yuan", "Yen", "Ringgit"], 2),
    ("Which planet has the most moons?", ["Earth", "Mars", "Saturn", "Mercury"], 2),
    ("Who wrote Romeo and Juliet?", ["Dickens", "Shakespeare", "Tolstoy", "Homer"], 1),
    ("What is H2O commonly known as?", ["Salt", "Water", "Oxygen", "Hydrogen"], 1),
    ("Which animal is known as the King of the Jungle?", ["Tiger", "Elephant", "Lion", "Bear"], 2),
    ("What is the tallest mountain in the world?", ["K2", "Everest", "Kilimanjaro", "Denali"], 1),
    ("How many colors are there in a rainbow?", ["5", "6", "7", "8"], 2),
    ("Which sport uses a shuttlecock?", ["Tennis", "Badminton", "Squash", "Volleyball"], 1),
    ("What is the largest mammal on Earth?", ["Elephant", "Blue Whale", "Giraffe", "Rhino"], 1),
    ("Which country is home to the kangaroo?", ["South Africa", "India", "Australia", "Brazil"], 2),
    ("What is the chemical symbol for Gold?", ["Ag", "Au", "Gd", "Go"], 1),
    ("Which is the longest river in the world?", ["Amazon", "Nile", "Yangtze", "Mississippi"], 1),
    ("How many players are on a football (soccer) team on the field?", ["9", "10", "11", "12"], 2),
    ("What is the freezing point of water in Celsius?", ["-1", "0", "1", "32"], 1),
]


def battle_smallcaps(text):
    return smallcaps(text)


@app.on_message(filters.command(["triviabattle", "battle", "legendarygame"]) & filters.group & ~BANNED_USERS)
async def start_trivia_battle(client, message: Message):
    chat_id = message.chat.id
    if chat_id in active_battles:
        return await message.reply_text(f"⚔️ {battle_smallcaps('A Trivia Battle is already running in this chat!')}")

    active_battles[chat_id] = {"phase": "joining", "players": {}, "scores": {}, "round": 0}

    join_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(
            text=f"⚔️ {battle_smallcaps('Join Battle')}",
            callback_data=f"battlejoin_{chat_id}",
            style=ButtonStyle.SUCCESS,
            icon_custom_emoji_id=_E_JOIN,
        )]]
    )
    intro = await message.reply_text(
        f"🏆 <b>{battle_smallcaps('Trivia Battle Royale')}</b> 🏆\n\n"
        f"{battle_smallcaps('Tap below to join the battle! 5 rounds of trivia, fastest correct answers win the most points.')}\n\n"
        f"⏳ {battle_smallcaps('Starting in 20 seconds...')}",
        reply_markup=join_markup,
    )
    active_battles[chat_id]["intro_msg"] = intro
    await asyncio.sleep(20)

    battle = active_battles.get(chat_id)
    if not battle:
        return
    if not battle["players"]:
        del active_battles[chat_id]
        return await intro.edit_text(f"😔 {battle_smallcaps('No one joined the battle. Try again with')} /triviabattle")

    battle["phase"] = "question"
    names = ", ".join(battle["players"].values())
    await intro.edit_text(
        f"⚔️ <b>{battle_smallcaps('Battle starting!')}</b>\n\n{battle_smallcaps('Fighters')}: {names}\n\n"
        f"{battle_smallcaps('Get ready for round 1!')}"
    )
    await asyncio.sleep(2)
    await run_trivia_round(client, chat_id)


@app.on_callback_query(filters.regex(r"^battlejoin_") & ~BANNED_USERS)
async def battle_join_callback(client, callback_query):
    chat_id = int(callback_query.data.split("_")[1])
    battle = active_battles.get(chat_id)
    if not battle or battle["phase"] != "joining":
        return await callback_query.answer(smallcaps("Joining window is closed!"), show_alert=True)
    user = callback_query.from_user
    if user.id in battle["players"]:
        return await callback_query.answer(smallcaps("You already joined!"), show_alert=True)
    battle["players"][user.id] = user.first_name
    battle["scores"][user.id] = 0
    await callback_query.answer(f"⚔️ {smallcaps('You joined the battle!')}", show_alert=True)


async def run_trivia_round(client, chat_id):
    battle = active_battles.get(chat_id)
    if not battle:
        return
    if battle["round"] >= 5:
        return await finish_trivia_battle(client, chat_id)

    battle["round"] += 1
    question, options, correct_idx = random.choice(TRIVIA_QUESTIONS)
    battle["current_answer"] = correct_idx
    battle["answered"] = {}
    battle["question_time"] = time.time()

    emoji_map = [_E_A, _E_B, _E_C, _E_D]
    letters = ["A", "B", "C", "D"]
    rows = []
    for idx, opt in enumerate(options):
        rows.append([InlineKeyboardButton(
            text=f"{letters[idx]}. {opt}",
            callback_data=f"battleans_{chat_id}_{idx}",
            style=[ButtonStyle.PRIMARY, ButtonStyle.SUCCESS, ButtonStyle.DANGER, ButtonStyle.PRIMARY][idx],
            icon_custom_emoji_id=emoji_map[idx],
        )])

    round_label = battle_smallcaps(f"Round {battle['round']}/5")
    msg = await app.send_message(
        chat_id,
        f"🏆 <b>{round_label}</b>\n\n❓ <b>{question}</b>\n\n"
        f"⏱ {battle_smallcaps('You have 15 seconds!')}",
        reply_markup=InlineKeyboardMarkup(rows),
    )
    battle["question_msg"] = msg
    await asyncio.sleep(15)

    battle = active_battles.get(chat_id)
    if not battle:
        return
    correct_option = options[correct_idx]
    winners = [uid for uid, ans in battle["answered"].items() if ans == correct_idx]
    for uid in winners:
        elapsed = battle["answered_time"].get(uid, 15)
        points = max(5, 15 - int(elapsed))
        battle["scores"][uid] = battle["scores"].get(uid, 0) + points

    if winners:
        winner_text = "\n".join(
            f"• {battle['players'].get(uid, 'Unknown')} (+{max(5, 15 - int(battle['answered_time'].get(uid, 15)))})"
            for uid in winners
        )
    else:
        winner_text = battle_smallcaps("No one answered correctly!")

    try:
        await msg.edit_text(
            f"✅ <b>{battle_smallcaps('Correct answer')}:</b> {correct_option}\n\n{winner_text}"
        )
    except Exception:
        pass

    await asyncio.sleep(3)
    await run_trivia_round(client, chat_id)


@app.on_callback_query(filters.regex(r"^battleans_") & ~BANNED_USERS)
async def battle_answer_callback(client, callback_query):
    parts = callback_query.data.split("_")
    chat_id, chosen_idx = int(parts[1]), int(parts[2])
    battle = active_battles.get(chat_id)
    user = callback_query.from_user

    if not battle or battle["phase"] != "question":
        return await callback_query.answer(smallcaps("No active round!"), show_alert=True)
    if user.id not in battle["players"]:
        return await callback_query.answer(smallcaps("You did not join this battle!"), show_alert=True)
    if user.id in battle["answered"]:
        return await callback_query.answer(smallcaps("You already answered!"), show_alert=True)

    battle["answered"][user.id] = chosen_idx
    battle.setdefault("answered_time", {})[user.id] = time.time() - battle["question_time"]
    await callback_query.answer(f"✅ {smallcaps('Answer locked in!')}")


async def finish_trivia_battle(client, chat_id):
    battle = active_battles.pop(chat_id, None)
    if not battle:
        return
    ranking = sorted(battle["scores"].items(), key=lambda x: x[1], reverse=True)
    if not ranking or ranking[0][1] == 0:
        return await app.send_message(chat_id, f"😔 {battle_smallcaps('Battle over — nobody scored any points!')}")

    text = f"🏆 <b>{battle_smallcaps('Trivia Battle Results')}</b> 🏆\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, (uid, score) in enumerate(ranking[:5]):
        medal = medals[i] if i < 3 else f"{i + 1}."
        text += f"{medal} {battle['players'].get(uid, 'Unknown')} — <b>{score}</b> pts\n"

    winner_id, winner_score = ranking[0]
    if winner_score > 0:
        existing = await trivia_db.find_one({"user_id": winner_id})
        if existing:
            await trivia_db.update_one({"user_id": winner_id}, {"$set": {"points": existing["points"] + winner_score, "name": battle["players"][winner_id]}})
        else:
            await trivia_db.insert_one({"user_id": winner_id, "name": battle["players"][winner_id], "points": winner_score})

    text += f"\n👑 {battle_smallcaps('Champion')}: <b>{battle['players'].get(winner_id, 'Unknown')}</b>"
    await app.send_message(chat_id, text)


@app.on_message(filters.command(["triviatop", "battletop"]) & ~BANNED_USERS)
async def trivia_leaderboard(client, message: Message):
    top_users = trivia_db.find().sort("points", -1).limit(10)
    text = f"🏆 <b>{battle_smallcaps('Trivia Battle Global Leaderboard')}</b> 🏆\n\n"
    count, has_users = 1, False
    async for user in top_users:
        has_users = True
        text += f"<b>{count}.</b> {battle_smallcaps(user.get('name', 'Unknown'))} - <code>{user['points']}</code> pts\n"
        count += 1
    if not has_users:
        text += battle_smallcaps("No champions yet! Start a battle with /triviabattle")
    await message.reply_text(text)
