#!/usr/bin/env python3
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "watchface" / "src" / "main" / "res" / "drawable-nodpi"
FONT = ROOT / "tools" / "fonts"

W = 450
SS = 4
PX = W * SS
C = PX / 2
TICK_OUTER = 213 * SS
TICK_LONG = 178 * SS
TICK_MIN = 197 * SS
NUM_R = 154 * SS
NUM_SIZE = 27.5 * SS
BRAND_Y = 171 * SS
SUB_Y = 190 * SS
DATE_Y = 332 * SS


def font(name, size):
    return ImageFont.truetype(str(FONT / name), int(size))


def radial_background():
    img = Image.new("RGB", (PX, PX), "#02040a")
    px = img.load()
    step = 3
    for y in range(0, PX, step):
        for x in range(0, PX, step):
            d = math.hypot(x - C, y - C) / C
            glow = max(0.0, 1.0 - d)
            v = (
                3.0 + 6.0 * glow ** 1.8,
                5.0 + 9.0 * glow ** 1.8,
                11.0 + 16.0 * glow ** 1.8,
            )
            for yy in range(y, min(y + step, PX)):
                for xx in range(x, min(x + step, PX)):
                    px[xx, yy] = tuple(int(c) for c in v)
    return img


def add_sheen(img):
    sheen = Image.new("L", (PX, PX), 0)
    d = ImageDraw.Draw(sheen)
    d.polygon(
        [(-PX, PX * 1.2), (PX * 0.45, -PX * 0.1), (PX * 1.0, -PX * 0.1), (-PX, PX * 1.8)],
        fill=5,
    )
    sheen = sheen.filter(ImageFilter.GaussianBlur(55 * SS))
    white = Image.new("RGB", (PX, PX), "#aebfe4")
    img.paste(white, (0, 0), sheen)
    return img


def star_sprite(radius, color, peak=180):
    size = int(max(3, radius * 5))
    s = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    cx = cy = size / 2
    for i in range(5, 0, -1):
        r = radius * i / 5
        a = int(peak * (1 - (i - 1) / 5) ** 2.4)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (a,))
    return s


def add_stars(img):
    rng = random.Random(20261028)
    layer = Image.new("RGBA", (PX, PX), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    palette = [
        ((255, 255, 255), 0.70),
        ((196, 214, 255), 0.22),
        ((255, 210, 165), 0.04),
        ((160, 220, 255), 0.02),
    ]
    colors = [c for c, _ in palette]
    weights = [w for _, w in palette]

    def place(rmin, rmax, alpha_lo, alpha_hi, count):
        for _ in range(count):
            a = rng.random() * math.tau
            rr = math.sqrt(rng.random()) * (C - 2 * SS)
            x = C + math.cos(a) * rr
            y = C + math.sin(a) * rr
            color = rng.choices(colors, weights)[0]
            radius = rng.uniform(rmin, rmax) * SS
            alpha = int(rng.uniform(alpha_lo, alpha_hi))
            d.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color + (alpha,))

    place(0.05, 0.18, 14, 52, 7600)
    place(0.18, 0.34, 25, 80, 5600)
    place(0.34, 0.50, 45, 115, 3000)
    place(0.50, 0.68, 70, 150, 600)

    for _ in range(42):
        a = rng.random() * math.tau
        rr = math.sqrt(rng.random()) * (C - 3 * SS)
        x = C + math.cos(a) * rr
        y = C + math.sin(a) * rr
        bright = rng.uniform(0.55, 0.85) * SS
        core = rng.choice([(255, 255, 255), (208, 226, 255), (255, 224, 190)])
        layer.alpha_composite(star_sprite(bright, core, 95), (int(x - bright * 2.5), int(y - bright * 2.5)))

    for _ in range(9):
        a = rng.random() * math.tau
        rr = math.sqrt(rng.random()) * (C - 4 * SS)
        x = C + math.cos(a) * rr
        y = C + math.sin(a) * rr
        bright = rng.uniform(0.9, 1.35) * SS
        core = rng.choice([(255, 255, 255), (232, 241, 255)])
        layer.alpha_composite(star_sprite(bright, core, 135), (int(x - bright * 2.5), int(y - bright * 2.5)))
        d.line([x - 2.6 * SS, y, x + 2.6 * SS, y], fill=core + (40,), width=max(1, int(0.3 * SS)))
        d.line([x, y - 2.6 * SS, x, y + 2.6 * SS], fill=core + (40,), width=max(1, int(0.3 * SS)))

    img.paste(layer, (0, 0), layer)
    return img


def add_grain(img):
    noise = Image.effect_noise((PX, PX), 14).convert("L")
    noise = noise.filter(ImageFilter.GaussianBlur(0.5 * SS))
    alpha = noise.point(lambda v: int(max(0, v - 118) * 0.14))
    white = Image.new("RGB", (PX, PX), "#93a8cc")
    img.paste(white, (0, 0), alpha)
    return img


def draw_rim(img):
    ring = Image.new("L", (PX, PX), 0)
    rd = ImageDraw.Draw(ring)
    r_out, r_in = 222.5 * SS, 219.0 * SS
    rd.ellipse([C - r_out, C - r_out, C + r_out, C + r_out], fill=255)
    rd.ellipse([C - r_in, C - r_in, C + r_in, C + r_in], fill=0)

    grad = Image.new("RGB", (PX, PX))
    gp = grad.load()
    for y in range(PX):
        for x in range(0, PX, 4):
            t = ((x / PX) + (y / PX)) / 2
            t = min(1.0, max(0.0, t))
            base = int(198 - 128 * t)
            col = (base, base + 3, base + 8)
            for xx in range(x, min(x + 4, PX)):
                gp[xx, y] = col
    soft = Image.new("L", (PX, PX), 0)
    sd = ImageDraw.Draw(soft)
    sd.arc(
        [C - (r_out - 1.0 * SS), C - (r_out - 1.0 * SS), C + (r_out - 1.0 * SS), C + (r_out - 1.0 * SS)],
        150,
        330,
        fill=80,
        width=int(0.7 * SS),
    )
    soft = soft.filter(ImageFilter.GaussianBlur(0.8 * SS))

    img.paste(grad, (0, 0), ring)
    img.paste(Image.new("RGB", (PX, PX), "#e8ecf2"), (0, 0), soft)

    d = ImageDraw.Draw(img)
    r = 223.0 * SS
    d.ellipse([C - r, C - r, C + r, C + r], outline=(10, 12, 16, 200), width=int(0.6 * SS))
    r = 218.4 * SS
    d.ellipse([C - r, C - r, C + r, C + r], outline=(8, 10, 14, 170), width=int(0.7 * SS))
    return img


def draw_ticks(img):
    layer = Image.new("RGBA", (PX, PX), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for minute in range(60):
        a = math.radians(minute * 6)
        if minute % 5 == 0:
            inner = TICK_LONG
            width = 1.9 * SS
            alpha = 246
        else:
            inner = TICK_MIN
            width = 0.95 * SS
            alpha = 195
        x1 = C + math.sin(a) * TICK_OUTER
        y1 = C - math.cos(a) * TICK_OUTER
        x2 = C + math.sin(a) * inner
        y2 = C - math.cos(a) * inner
        d.line([x1, y1, x2, y2], fill=(238, 241, 246, alpha), width=max(1, int(width)))
    img.paste(layer, (0, 0), layer)
    return img


def centered_text(draw, xy, text, fnt, fill, tracking=0):
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = xy[0] - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, xy[1]), ch, font=fnt, fill=fill, anchor="lm")
        x += w + tracking
    return total


def draw_numerals(img):
    layer = Image.new("RGBA", (PX, PX), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    fnt = font("Jost-380.ttf", NUM_SIZE)
    for hour in (12, 2, 4, 6, 8, 10):
        a = math.radians(hour % 12 * 30)
        x = C + math.sin(a) * NUM_R
        y = C - math.cos(a) * NUM_R
        d.text((x, y), str(hour), font=fnt, fill=(242, 244, 247, 250), anchor="mm")
    img.paste(layer, (0, 0), layer)
    return img


def draw_brand(img):
    layer = Image.new("RGBA", (PX, PX), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    main = font("Jost-400.ttf", 12.6 * SS)
    sub = font("Jost-400.ttf", 6.2 * SS)
    centered_text(d, (C, BRAND_Y), "STERNGLAS", main, (246, 247, 250, 250), tracking=3.0 * SS)
    centered_text(d, (C, SUB_Y), "ZEITMESSER", sub, (224, 227, 233, 225), tracking=2.0 * SS)
    img.paste(layer, (0, 0), layer)
    return img


def draw_date_frame(img):
    layer = Image.new("RGBA", (PX, PX), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    w, h = 44 * SS, 40 * SS
    x, y = C - w / 2, DATE_Y - h / 2
    d.rectangle([x, y, x + w, y + h], fill=(176, 180, 188, 255))
    d.line([x + 1, y + 1, x + w - 1, y + 1], fill=(246, 248, 251, 235), width=int(0.8 * SS))
    d.line([x + 1, y + 1, x + 1, y + h - 1], fill=(226, 229, 235, 210), width=int(0.8 * SS))
    d.line([x + 1, y + h - 1, x + w - 1, y + h - 1], fill=(104, 108, 116, 220), width=int(0.8 * SS))
    d.line([x + w - 1, y + 1, x + w - 1, y + h - 1], fill=(118, 122, 130, 220), width=int(0.8 * SS))
    d.rectangle([x, y, x + w, y + h], outline=(16, 17, 21, 245), width=int(0.9 * SS))
    bx, by = 2.4 * SS, 2.4 * SS
    d.rectangle([x + bx, y + by, x + w - bx, y + h - by], fill=(2, 3, 6, 255))
    d.rectangle(
        [x + bx, y + by, x + w - bx, y + h - by],
        outline=(32, 34, 39, 230),
        width=int(0.7 * SS),
    )
    d.line([x + bx + 1, y + by + 1, x + w - bx - 1, y + by + 1], fill=(0, 0, 0, 220), width=int(0.9 * SS))
    img.paste(layer, (0, 0), layer)
    return img


def hand_polygon(length, base_width, tip_width, center=C, tail=7 * SS):
    return [
        (center - base_width / 2, center + tail),
        (center + base_width / 2, center + tail),
        (center + base_width * 0.46, center - length * 0.78),
        (center, center - length),
        (center - base_width * 0.46, center - length * 0.78),
    ]


def make_hand(length, base_width, tip_width, ridge=0.36):
    img = Image.new("RGBA", (PX, PX), (0, 0, 0, 0))
    pts = hand_polygon(length, base_width, tip_width)
    shadow = Image.new("RGBA", (PX, PX), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.polygon([(x + 1.0 * SS, y + 1.8 * SS) for x, y in pts], fill=(0, 0, 0, 135))
    shadow = shadow.filter(ImageFilter.GaussianBlur(1.6 * SS))
    img.alpha_composite(shadow)

    outline = Image.new("RGBA", (PX, PX), (0, 0, 0, 0))
    od = ImageDraw.Draw(outline)
    od.polygon(pts, fill=(30, 32, 37, 255), outline=(12, 13, 16, 255), width=int(1.0 * SS))
    img.alpha_composite(outline)

    inner = hand_polygon(length, base_width - 1.7 * SS, tip_width * 0.5)
    face = Image.new("RGBA", (PX, PX), (0, 0, 0, 0))
    fd = ImageDraw.Draw(face)
    fd.polygon(inner, fill=(172, 177, 184, 255))
    img.alpha_composite(face)

    ridge_pts = hand_polygon(length * 0.97, base_width * ridge, tip_width * 0.32)
    ridge_layer = Image.new("RGBA", (PX, PX), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ridge_layer)
    rd.polygon(ridge_pts, fill=(248, 250, 252, 255))
    ridge_layer = ridge_layer.filter(ImageFilter.GaussianBlur(0.3 * SS))
    img.alpha_composite(ridge_layer)
    return img


def make_center_cap():
    img = Image.new("RGBA", (PX, PX), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = 6.6 * SS
    d.ellipse([C - r, C - r, C + r, C + r], fill=(190, 194, 201, 255), outline=(18, 19, 23, 255), width=int(0.9 * SS))
    r = 5.1 * SS
    d.ellipse([C - r, C - r, C + r, C + r], fill=(20, 22, 26, 255), outline=(86, 90, 97, 255), width=int(0.55 * SS))
    r = 2.1 * SS
    d.ellipse([C - r, C - r, C + r, C + r], fill=(232, 235, 239, 255))
    d.ellipse([C - 1.0 * SS, C - 1.0 * SS, C + 0.3 * SS, C + 0.3 * SS], fill=(255, 255, 255, 225))
    return img


def build_dial():
    img = radial_background()
    add_sheen(img)
    add_stars(img)
    add_grain(img)
    img = img.convert("RGBA")
    draw_rim(img)
    draw_ticks(img)
    draw_numerals(img)
    draw_date_frame(img)
    return img


def composite_preview(dial, hour, minute, cap, date_text="14"):
    canvas = dial.copy()
    for hand, angle in ((hour, 10 * 30 + 10 * 0.5), (minute, 10 * 6)):
        rotated = hand.rotate(-angle, resample=Image.BICUBIC, center=(C, C))
        canvas.alpha_composite(rotated)
    canvas.alpha_composite(cap)
    d = ImageDraw.Draw(canvas)
    f = font("Jost-300.ttf", 27.5 * SS)
    d.text((C, DATE_Y + 1.5 * SS), date_text, font=f, fill=(240, 242, 245, 255), anchor="mm")
    return canvas


def main():
    RES.mkdir(parents=True, exist_ok=True)
    dial = build_dial()
    hour = make_hand(122 * SS, 6.4 * SS, 1.6 * SS)
    minute = make_hand(153 * SS, 5.2 * SS, 1.1 * SS)
    cap = make_center_cap()
    preview = composite_preview(dial, hour, minute, cap)

    for name, im in (
        ("dial", dial),
        ("hand_hour", hour),
        ("hand_minute", minute),
        ("center", cap),
        ("preview", preview),
    ):
        im.resize((W, W), Image.LANCZOS).save(RES / f"{name}.png", optimize=True)

    preview.resize((900, 900), Image.LANCZOS).save(ROOT / "preview.png", optimize=True)
    print("assets written to", RES)


if __name__ == "__main__":
    main()
