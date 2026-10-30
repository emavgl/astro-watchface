#!/usr/bin/env python3
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import render_assets as ra

OUT = ROOT / "fastlane" / "metadata" / "android" / "en-US" / "images"
SHOTS = OUT / "wearScreenshots"
S = 2
W = ra.W * S
C = W / 2

SHOT_SPECS = [
    ("01_core_sternglas", 12, "sternglas", 10, 10, "14"),
    ("02_dust_classic", 19, "classic", 2, 45, "07"),
    ("03_andromeda_minimal", 22, "minimal", 7, 25, "23"),
    ("04_nebula_sternglas", 23, "sternglas", 4, 40, "30"),
    ("05_band_classic", 14, "classic", 9, 15, "02"),
    ("06_stars_minimal", 17, "minimal", 11, 5, "18"),
]


def load(name):
    return Image.open(ra.RES / name).convert("RGBA").resize((W, W), Image.LANCZOS)


def compose(tile, tick_style, hour, minute, date_text):
    background = (
        Image.open(ra.RES / f"bg_tile_{tile:02d}.jpg")
        .convert("RGBA")
        .resize((W, W), Image.LANCZOS)
    )
    canvas = Image.alpha_composite(background, load("dial_frame.png"))
    canvas.alpha_composite(load(f"ticks_{tick_style}.png"))
    for hand, angle in (
        ("hand_hour.png", (hour % 12) * 30 + minute * 0.5),
        ("hand_minute.png", minute * 6),
    ):
        rotated = load(hand).rotate(-angle, resample=Image.BICUBIC, center=(C, C))
        canvas.alpha_composite(rotated)
    canvas.alpha_composite(load("center.png"))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (C, ra.DATE_Y / ra.SS * S + 1.5 * S),
        date_text,
        font=ra.font("Jost-300.ttf", 27.5 * S),
        fill=(240, 242, 245, 255),
        anchor="mm",
    )
    return canvas


def circular(image, size, margin, background=(0, 0, 0, 0)):
    if image.size != (size, size):
        image = image.resize((size, size), Image.LANCZOS)
    scale = 4
    mask = Image.new("L", (size * scale, size * scale), 0)
    box = (
        margin * scale,
        margin * scale,
        (size - margin) * scale,
        (size - margin) * scale,
    )
    ImageDraw.Draw(mask).ellipse(box, fill=255)
    mask = mask.resize((size, size), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), background)
    out.paste(image, (0, 0), mask)
    return out


def write_screenshots():
    SHOTS.mkdir(parents=True, exist_ok=True)
    for name, tile, tick, hour, minute, date in SHOT_SPECS:
        face = circular(
            compose(tile, tick, hour, minute, date), W, 2 * S, (0, 0, 0, 255)
        )
        face.convert("RGB").save(SHOTS / f"{name}.png", optimize=True)


def write_icon():
    face = compose(12, "sternglas", 10, 10, "14").resize((512, 512), Image.LANCZOS)
    face.convert("RGB").save(OUT / "icon.png", optimize=True)


def write_feature_graphic():
    width, height = 1024, 500
    background = (
        Image.open(ra.RES / "bg_tile_12.jpg")
        .convert("RGB")
        .resize((width, height), Image.LANCZOS)
    )
    background = ImageEnhance.Brightness(background).enhance(0.35)
    background = background.filter(ImageFilter.GaussianBlur(1.2))
    canvas = background.convert("RGBA")

    face = circular(compose(12, "sternglas", 10, 10, "14"), 420, 1)
    canvas.alpha_composite(face, (52, 40))

    draw = ImageDraw.Draw(canvas)
    title_font = ra.font("Jost-400.ttf", 84)
    subtitle_font = ra.font("Jost-380.ttf", 30)
    detail_font = ra.font("Jost-300.ttf", 22)
    draw.text((520, 122), "GALASSIA", font=title_font, fill=(247, 248, 251, 255))
    draw.text(
        (524, 222),
        "MILKY WAY WATCHFACE",
        font=subtitle_font,
        fill=(198, 210, 235, 255),
    )
    draw.line((524, 280, 940, 280), fill=(120, 140, 180, 160), width=1)
    draw.text(
        (524, 300),
        "Analog  ·  Minimal  ·  Wear OS",
        font=detail_font,
        fill=(160, 176, 205, 255),
    )
    canvas.convert("RGB").save(OUT / "featureGraphic.png", optimize=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    write_screenshots()
    write_icon()
    write_feature_graphic()
    print(f"screenshots written to {SHOTS}")


if __name__ == "__main__":
    main()
