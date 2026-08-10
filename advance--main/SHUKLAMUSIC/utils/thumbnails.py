import os
import re
import math

import aiofiles
import aiohttp
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from textwrap import wrap
from unidecode import unidecode
from py_yt import VideosSearch

from SHUKLAMUSIC import app
from config import YOUTUBE_IMG_URL


CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)


# ── colour helpers ─────────────────────────────────────────────────────────────

def cover_fit(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Resize + crop an image to fully cover a target box without distortion
    (like CSS background-size: cover) — the whole frame is filled and the
    image's original aspect ratio is preserved."""
    src_w, src_h = img.size
    src_ratio = src_w / src_h
    target_ratio = target_w / target_h
    if src_ratio > target_ratio:
        new_h = target_h
        new_w = int(new_h * src_ratio)
    else:
        new_w = target_w
        new_h = int(new_w / src_ratio)
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    x0 = (new_w - target_w) // 2
    y0 = (new_h - target_h) // 2
    return resized.crop((x0, y0, x0 + target_w, y0 + target_h))


def get_dominant_color(img: Image.Image, n=4):
    small = img.convert("RGB").resize((120, 120))
    arr = np.array(small).reshape(-1, 3).astype(float)
    np.random.seed(42)
    centers = arr[np.random.choice(len(arr), n, replace=False)]
    for _ in range(12):
        dists = np.linalg.norm(arr[:, None] - centers[None], axis=2)
        labels = np.argmin(dists, axis=1)
        for k in range(n):
            pts = arr[labels == k]
            if len(pts):
                centers[k] = pts.mean(axis=0)
    best, best_sat = centers[0], 0
    for c in centers:
        r, g, b = c / 255.0
        mx, mn = max(r, g, b), min(r, g, b)
        sat = (mx - mn) / (mx + 1e-9)
        lum = (mx + mn) / 2
        score = sat * (1 - abs(lum - 0.5))
        if score > best_sat:
            best_sat, best = score, c
    return tuple(int(x) for x in best)


def clear(text, limit=34):
    words, title = text.split(" "), ""
    for w in words:
        if len(title) + len(w) < limit:
            title += " " + w
    return title.strip()


def get_bot_name():
    try:
        raw = unidecode(app.name)
    except Exception:
        raw = "Music"
    cleaned = raw.replace("_", " ")
    cleaned = re.sub(r"(?i)\b(robot|bot)\b", "", cleaned)
    return " ".join(cleaned.split()) or "Music"


# ── icon helpers (vector drawn, no external assets needed) ────────────────────

def draw_play_pause(draw, cx, cy, r, fg, bg, playing=True):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg)
    if playing:
        bar_w = r * 0.24
        bar_h = r * 0.9
        gap = r * 0.22
        x1 = cx - gap / 2 - bar_w
        x2 = cx + gap / 2
        draw.rounded_rectangle(
            [x1, cy - bar_h / 2, x1 + bar_w, cy + bar_h / 2],
            radius=bar_w * 0.35, fill=fg,
        )
        draw.rounded_rectangle(
            [x2, cy - bar_h / 2, x2 + bar_w, cy + bar_h / 2],
            radius=bar_w * 0.35, fill=fg,
        )
    else:
        s = r * 0.95
        draw.polygon(
            [(cx - s * 0.35, cy - s * 0.55), (cx - s * 0.35, cy + s * 0.55), (cx + s * 0.65, cy)],
            fill=fg,
        )


def draw_skip(draw, cx, cy, size, color, forward=True):
    tri_w = size * 0.55
    tri_h = size
    bar_w = size * 0.14
    if forward:
        draw.polygon(
            [(cx - tri_w / 2, cy - tri_h / 2), (cx - tri_w / 2, cy + tri_h / 2), (cx + tri_w / 2, cy)],
            fill=color,
        )
        draw.rectangle([cx + tri_w / 2, cy - tri_h / 2, cx + tri_w / 2 + bar_w, cy + tri_h / 2], fill=color)
    else:
        draw.polygon(
            [(cx + tri_w / 2, cy - tri_h / 2), (cx + tri_w / 2, cy + tri_h / 2), (cx - tri_w / 2, cy)],
            fill=color,
        )
        draw.rectangle([cx - tri_w / 2 - bar_w, cy - tri_h / 2, cx - tri_w / 2, cy + tri_h / 2], fill=color)


def draw_shuffle(draw, cx, cy, size, color, width=3):
    half = size / 2
    draw.line([(cx - half, cy - half * 0.45), (cx + half * 0.35, cy + half * 0.45)], fill=color, width=width)
    draw.line([(cx - half, cy + half * 0.45), (cx + half * 0.35, cy - half * 0.45)], fill=color, width=width)
    draw.polygon(
        [(cx + half * 0.25, cy + half * 0.45 - size * 0.12),
         (cx + half * 0.25, cy + half * 0.45 + size * 0.12),
         (cx + half * 0.55, cy + half * 0.45)],
        fill=color,
    )
    draw.polygon(
        [(cx + half * 0.25, cy - half * 0.45 - size * 0.12),
         (cx + half * 0.25, cy - half * 0.45 + size * 0.12),
         (cx + half * 0.55, cy - half * 0.45)],
        fill=color,
    )


def draw_repeat(draw, cx, cy, size, color, width=3):
    r = size / 2
    box = [cx - r, cy - r, cx + r, cy + r]
    draw.arc(box, start=200, end=340, fill=color, width=width)
    draw.arc(box, start=20, end=160, fill=color, width=width)
    ah = size * 0.16
    top_x = cx + r * math.cos(math.radians(340))
    top_y = cy + r * math.sin(math.radians(340))
    draw.polygon(
        [(top_x - ah * 0.6, top_y - ah), (top_x + ah * 0.6, top_y - ah * 0.2), (top_x - ah * 0.9, top_y + ah * 0.3)],
        fill=color,
    )
    bot_x = cx + r * math.cos(math.radians(160))
    bot_y = cy + r * math.sin(math.radians(160))
    draw.polygon(
        [(bot_x + ah * 0.6, bot_y + ah), (bot_x - ah * 0.6, bot_y + ah * 0.2), (bot_x + ah * 0.9, bot_y - ah * 0.3)],
        fill=color,
    )


def draw_checkmark_badge(draw, cx, cy, r, badge_color, mark_color):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=badge_color)
    draw.line(
        [(cx - r * 0.5, cy), (cx - r * 0.1, cy + r * 0.4), (cx + r * 0.55, cy - r * 0.45)],
        fill=mark_color, width=max(2, int(r * 0.28)), joint="curve",
    )


def draw_equalizer_icon(draw, x, y, w, h, color):
    bar_w = w / 4
    heights = [h * 0.45, h, h * 0.65]
    bx = x
    for i, bh in enumerate(heights):
        draw.rounded_rectangle(
            [bx, y + (h - bh), bx + bar_w * 0.7, y + h],
            radius=bar_w * 0.25, fill=color,
        )
        bx += bar_w * 1.35


def draw_devices_icon(draw, x, y, w, h, color):
    mon_w, mon_h = w * 0.62, h * 0.62
    draw.rounded_rectangle([x, y, x + mon_w, y + mon_h], radius=3, outline=color, width=2)
    draw.line([(x + mon_w * 0.3, y + mon_h + 3), (x + mon_w * 0.7, y + mon_h + 3)], fill=color, width=2)
    ph_w, ph_h = w * 0.28, h
    px, py = x + mon_w + w * 0.14, y
    draw.rounded_rectangle([px, py, px + ph_w, py + ph_h], radius=4, outline=color, width=2)


def draw_fullscreen_icon(draw, x, y, size, color, width=2):
    a = size * 0.32
    corners = [
        [(x, y + a), (x, y), (x + a, y)],
        [(x + size - a, y), (x + size, y), (x + size, y + a)],
        [(x + size, y + size - a), (x + size, y + size), (x + size - a, y + size)],
        [(x + a, y + size), (x, y + size), (x, y + size - a)],
    ]
    for pts in corners:
        draw.line(pts, fill=color, width=width, joint="curve")


def draw_speaker_icon(draw, x, y, w, h, color):
    body_w = w * 0.42
    draw.rectangle([x, y + h * 0.3, x + body_w * 0.55, y + h * 0.7], fill=color)
    draw.polygon(
        [(x + body_w * 0.55, y + h * 0.7), (x + body_w * 0.55, y + h * 0.3),
         (x + body_w, y), (x + body_w, y + h)],
        fill=color,
    )
    draw.arc([x + body_w + 2, y + h * 0.15, x + body_w + w * 0.35, y + h * 0.85], start=290, end=70, fill=color, width=2)


def glass_panel(canvas, source, box, radius, blur=22, tint_alpha=45, dark_alpha=70,
                 tint_color=(255, 255, 255), dark_color=(8, 8, 16), border_alpha=90):
    """Paste a translucent frosted-glass rounded panel onto canvas, using a
    blurred crop of `source` (the full-size blurred page background) so the
    photo underneath is genuinely visible through the panel."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    if w <= 0 or h <= 0:
        return
    panel = source.crop(box).filter(ImageFilter.GaussianBlur(blur))
    tint = Image.new("RGBA", (w, h), (*tint_color, tint_alpha))
    panel = Image.alpha_composite(panel.convert("RGBA"), tint)
    wash = Image.new("RGBA", (w, h), (*dark_color, dark_alpha))
    panel = Image.alpha_composite(panel, wash)

    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
    canvas.paste(panel, (x0, y0), mask)

    if border_alpha:
        ImageDraw.Draw(canvas).rounded_rectangle(
            box, radius=radius, outline=(255, 255, 255, border_alpha), width=2
        )


# ── main ──────────────────────────────────────────────────────────────────────

async def get_thumb(videoid: str) -> str:
    cache_path = os.path.join(CACHE_DIR, f"{videoid}_v6.png")
    if os.path.isfile(cache_path):
        return cache_path

    results = VideosSearch(f"https://www.youtube.com/watch?v={videoid}", limit=1)
    try:
        results_data = await results.next()
        result_items = results_data.get("result", [])
        if not result_items:
            raise ValueError("No results found.")
        data = result_items[0]
        title = re.sub(r"\W+", " ", data.get("title", "Unsupported Title")).title()
        thumbnail = data.get("thumbnails", [{}])[0].get("url", YOUTUBE_IMG_URL)
        duration = data.get("duration") or "0:00"
        channel = data.get("channel", {}).get("name", "Unknown Channel")
    except Exception:
        title, thumbnail, duration, channel = (
            "Unsupported Title", YOUTUBE_IMG_URL, "0:00", "Unknown Channel",
        )

    tmp_path = os.path.join(CACHE_DIR, f"thumb{videoid}.png")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(tmp_path, "wb") as f:
                        await f.write(await resp.read())
    except Exception:
        return YOUTUBE_IMG_URL

    try:
        S = 2
        def sc(v):
            return int(v * S)

        W0, H0 = 1280, 720
        W, H = sc(W0), sc(H0)

        cover_raw = Image.open(tmp_path).convert("RGBA")
        cover_raw = ImageEnhance.Sharpness(cover_raw).enhance(1.4)
        cover_raw = ImageEnhance.Color(cover_raw).enhance(1.25)

        dominant = get_dominant_color(cover_raw)
        rd, gd, bd = dominant

        ACCENT = (30, 215, 150, 255)
        WHITE = (255, 255, 255, 255)
        GRAY = (170, 178, 200, 220)
        DARK_TEXT = (10, 10, 15, 255)

        # ── LAYER 1: full thumbnail, blurred, fills the whole frame ─────────
        page_bg = cover_fit(cover_raw, W, H).convert("RGBA")
        page_bg = page_bg.filter(ImageFilter.GaussianBlur(sc(55)))
        page_bg = Image.alpha_composite(page_bg, Image.new("RGBA", (W, H), (4, 4, 10, 130)))

        canvas = Image.new("RGBA", (W, H), (4, 4, 10, 255))
        canvas.alpha_composite(page_bg)

        # ── LAYER 2: the "now playing" glass card, inset so layer 1 clearly
        #    peeks around its edges ──────────────────────────────────────────
        M = sc(70)
        card_box = (M, M, W - M, H - M)
        card_r = sc(40)

        glass_panel(
            canvas, page_bg, card_box, card_r,
            blur=sc(24), tint_alpha=42, dark_alpha=95,
            tint_color=(255, 255, 255), dark_color=(8, 8, 16), border_alpha=70,
        )

        P = sc(44)
        content_left = M + P
        content_top = M + P
        content_right = W - M - P
        content_bottom = H - M - P
        content_w = content_right - content_left
        content_h = content_bottom - content_top

        # ── album art ───────────────────────────────────────────────────────
        ART = sc(460)
        ART_X = content_left
        ART_Y = content_top + (content_h - ART) // 2

        shadow = Image.new("RGBA", (ART + sc(80), ART + sc(80)), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rounded_rectangle(
            (sc(40), sc(40), ART + sc(40), ART + sc(40)),
            radius=sc(24), fill=(rd // 3, gd // 3, bd // 3, 200),
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(sc(18)))
        canvas.alpha_composite(shadow, (ART_X - sc(40), ART_Y - sc(40)))

        art = cover_raw.resize((ART, ART), Image.LANCZOS).convert("RGBA")
        art = ImageEnhance.Contrast(art).enhance(1.1)
        art_mask = Image.new("L", (ART, ART), 0)
        ImageDraw.Draw(art_mask).rounded_rectangle((0, 0, ART, ART), radius=sc(24), fill=255)
        art.putalpha(art_mask)
        canvas.alpha_composite(art, (ART_X, ART_Y))

        # ── fonts ───────────────────────────────────────────────────────────
        def load_font(path, size):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                try:
                    return ImageFont.load_default(size=size)
                except Exception:
                    return ImageFont.load_default()

        FONT_BOLD = "SHUKLAMUSIC/assets/font2.ttf"
        FONT_REG = "SHUKLAMUSIC/assets/font.ttf"

        fn_eyebrow = load_font(FONT_REG, sc(20))
        fn_title = load_font(FONT_BOLD, sc(46))
        fn_artist = load_font(FONT_REG, sc(24))
        fn_time = load_font(FONT_REG, sc(18))

        draw = ImageDraw.Draw(canvas)

        RX = ART_X + ART + sc(50)
        RW = content_right - RX

        # ── eyebrow row: small equalizer icon + "PLAYING FROM ALBUM" ───────
        eb_y = ART_Y + sc(6)
        draw_equalizer_icon(draw, RX, eb_y, sc(20), sc(20), ACCENT)
        draw.text((RX + sc(28), eb_y - sc(2)), "PLAYING NOW", font=fn_eyebrow, fill=ACCENT)

        # ── title (max 2 lines) ─────────────────────────────────────────────
        title_y = eb_y + sc(38)
        title_lines = wrap(clear(title, 34), 20)[:2]
        line_h = sc(56)
        for i, line in enumerate(title_lines):
            draw.text((RX + sc(2), title_y + i * line_h + sc(2)), line, font=fn_title, fill=(0, 0, 0, 110))
            draw.text((RX, title_y + i * line_h), line, font=fn_title, fill=WHITE)

        # ── artist row with badge ───────────────────────────────────────────
        artist_y = title_y + len(title_lines) * line_h + sc(14)
        ch_str = (channel or "Unknown Channel")[:26]
        draw.text((RX, artist_y), ch_str, font=fn_artist, fill=GRAY)
        try:
            ch_w = fn_artist.getlength(ch_str)
        except Exception:
            ch_w = len(ch_str) * sc(12)
        draw_checkmark_badge(draw, RX + ch_w + sc(22), artist_y + sc(14), sc(12), ACCENT, DARK_TEXT)

        # ── progress bar, inside its own glass pill ────────────────────────
        bar_y = ART_Y + ART - sc(90)
        bar_x0 = RX + sc(24)
        bar_x1 = content_right - sc(24)
        bar_h = sc(6)

        bar_pill_pad_x = sc(24)
        bar_pill_pad_y = sc(28)
        bar_pill_box = (
            RX - bar_pill_pad_x,
            bar_y - bar_pill_pad_y,
            content_right + bar_pill_pad_x,
            bar_y + sc(30) + bar_pill_pad_y,
        )
        glass_panel(
            canvas, page_bg, bar_pill_box, (bar_pill_box[3] - bar_pill_box[1]) // 2,
            blur=sc(20), tint_alpha=35, dark_alpha=70, border_alpha=55,
        )
        draw = ImageDraw.Draw(canvas)

        played_frac = 0.32
        draw.rounded_rectangle([bar_x0, bar_y, bar_x1, bar_y + bar_h], radius=bar_h // 2, fill=(255, 255, 255, 70))
        thumb_x = int(bar_x0 + (bar_x1 - bar_x0) * played_frac)
        draw.rounded_rectangle([bar_x0, bar_y, thumb_x, bar_y + bar_h], radius=bar_h // 2, fill=ACCENT)
        th_r = sc(7)
        draw.ellipse([thumb_x - th_r, bar_y + bar_h // 2 - th_r, thumb_x + th_r, bar_y + bar_h // 2 + th_r], fill=WHITE)

        time_y = bar_y + sc(14)
        draw.text((bar_x0, time_y), "0:00", font=fn_time, fill=GRAY)
        dur_text = str(duration)[:7]
        try:
            dw = fn_time.getlength(dur_text)
        except Exception:
            dw = len(dur_text) * sc(10)
        draw.text((bar_x1 - dw, time_y), dur_text, font=fn_time, fill=GRAY)

        # ── playback controls row (sits on its own glass pill) ─────────────
        controls_y = time_y + sc(56)
        controls_cx = (bar_x0 + bar_x1) // 2

        play_r = sc(30)
        gap = sc(58)

        pill_pad_x = sc(18)
        pill_pad_y = sc(16)
        pill_box = (
            controls_cx - gap * 2 - play_r - pill_pad_x,
            controls_y - play_r - pill_pad_y,
            controls_cx + gap * 2 + play_r + pill_pad_x,
            controls_y + play_r + pill_pad_y,
        )
        glass_panel(
            canvas, page_bg, pill_box, (pill_box[3] - pill_box[1]) // 2,
            blur=sc(20), tint_alpha=35, dark_alpha=70, border_alpha=55,
        )
        draw = ImageDraw.Draw(canvas)

        draw_play_pause(draw, controls_cx, controls_y, play_r, DARK_TEXT, WHITE, playing=True)
        draw_skip(draw, controls_cx - gap, controls_y, sc(26), WHITE, forward=False)
        draw_skip(draw, controls_cx + gap, controls_y, sc(26), WHITE, forward=True)
        draw_shuffle(draw, controls_cx - gap * 2, controls_y, sc(26), ACCENT, width=max(2, sc(3)))
        draw_repeat(draw, controls_cx + gap * 2, controls_y, sc(26), ACCENT, width=max(2, sc(3)))

        canvas.convert("RGB").resize((W0, H0), Image.LANCZOS).save(
            cache_path, quality=97, optimize=False
        )

    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    return cache_path
