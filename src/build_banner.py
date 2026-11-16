"""Build the animated Z-Spark Tech GitHub banner from the supplied brand assets.

Run from the project root:
    python -m pip install -r requirements.txt
    python src/build_banner.py

The script writes the animated GIF, a still preview, and a contact sheet to output/.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUTPUT = ROOT / "output"
LOGO_PATH = ASSETS / "z-spark-logo-original.png"
BACKGROUND_PATH = ASSETS / "z-spark-dark-tech-background.png"
GIF_PATH = OUTPUT / "Z-Spark-Tech-Animated-GitHub-Banner.gif"
PREVIEW_PATH = OUTPUT / "Z-Spark-Tech-Animated-GitHub-Banner-Preview.png"
CONTACT_PATH = OUTPUT / "frame-contact-sheet.png"

WIDTH, HEIGHT = 1600, 500
FRAME_COUNT = 36
FRAME_DURATION_MS = 100  # 36 frames × 100 ms = 3.6 seconds per loop.


def load_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Use DejaVu on Linux, Arial on Windows/macOS, then Pillow's fallback."""
    candidates = (
        [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "/Library/Fonts/Arial Bold.ttf",
        ]
        if bold
        else [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/Library/Fonts/Arial.ttf",
        ]
    )
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def bezier(p0: tuple[float, float], p1: tuple[float, float],
           p2: tuple[float, float], p3: tuple[float, float], t: float) -> tuple[float, float]:
    u = 1 - t
    return (
        u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0],
        u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1],
    )


def build_frames() -> list[Image.Image]:
    if not LOGO_PATH.is_file():
        raise FileNotFoundError(f"Original logo not found: {LOGO_PATH}")
    if not BACKGROUND_PATH.is_file():
        raise FileNotFoundError(f"Background artwork not found: {BACKGROUND_PATH}")

    # Keep one stable background and layout for every frame; only lighting animates.
    background = (
        Image.open(BACKGROUND_PATH)
        .convert("RGB")
        .resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        .convert("RGBA")
    )

    card = (58, 65, 425, 435)
    card_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    card_draw = ImageDraw.Draw(card_layer)
    card_draw.rounded_rectangle(card, radius=34, fill=(4, 6, 10, 165), outline=(194, 30, 44, 125), width=2)
    card_draw.rounded_rectangle((69, 76, 414, 424), radius=27, outline=(255, 255, 255, 24), width=1)
    card_draw.rounded_rectangle((58, 132, 63, 368), radius=2, fill=(239, 30, 48, 190))
    background = Image.alpha_composite(background, card_layer)

    # Preserve the supplied mark; only trim transparent padding and resize proportionally.
    logo_source = Image.open(LOGO_PATH).convert("RGBA")
    alpha = logo_source.getchannel("A")
    visible_bounds = alpha.point(lambda value: 255 if value > 6 else 0).getbbox()
    if visible_bounds is None:
        raise ValueError("The supplied logo contains no visible pixels.")
    logo = logo_source.crop(visible_bounds)
    logo_width = 320
    logo_height = round(logo.height * logo_width / logo.width)
    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
    logo_mask = np.asarray(logo.getchannel("A"), dtype=np.uint16)
    logo_x = 82
    logo_y = (HEIGHT - logo_height) // 2

    font_label = load_font(17, bold=True)
    font_title = load_font(66, bold=True)
    font_tagline = load_font(25)
    font_footer = load_font(15, bold=True)

    text_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_layer)
    draw.text((500, 151), "SOFTWARE ENGINEERING  /  DIGITAL PRODUCTS", font=font_label, fill=(255, 76, 91, 255))
    draw.text((496, 190), "Z-SPARK TECH", font=font_title, fill=(247, 248, 251, 255))
    draw.rounded_rectangle((500, 282, 594, 288), radius=3, fill=(238, 32, 51, 255))
    draw.text((500, 314), "Engineering ideas into real-world solutions.", font=font_tagline, fill=(205, 212, 223, 255))
    draw.text((501, 382), "BUILD   •   ENGINEER   •   INNOVATE", font=font_footer, fill=(139, 150, 166, 255))
    base = Image.alpha_composite(background, text_layer)

    yy, xx = np.mgrid[0:logo_height, 0:logo_width]
    diagonal = xx + 0.33 * yy
    frames: list[Image.Image] = []

    for frame_index in range(FRAME_COUNT):
        phase = frame_index / (FRAME_COUNT - 1)
        frame = base.copy()
        pulse = (math.sin(2 * math.pi * frame_index / FRAME_COUNT) + 1) / 2

        # Gentle breathing accent around the logo panel.
        border = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        border_draw = ImageDraw.Draw(border)
        border_alpha = int(78 + 45 * pulse)
        border_draw.rounded_rectangle(card, radius=34, outline=(235, 29, 48, border_alpha), width=2)
        frame = Image.alpha_composite(frame, border)

        # A soft light pulse travels along the existing lower-right red ribbon.
        px, py = bezier((1030, 515), (1220, 490), (1470, 430), (1640, 292), phase)
        travel_fade = math.sin(math.pi * phase) ** 1.2
        glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        radius = 38
        strength = int(76 * travel_fade)
        glow_draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill=(255, 26, 42, strength))
        glow = glow.filter(ImageFilter.GaussianBlur(27))
        frame = Image.alpha_composite(frame, glow)

        # Fixed circuit nodes pulse subtly; they do not change position.
        node_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        node_draw = ImageDraw.Draw(node_layer)
        nodes = [(1243, 65), (1344, 90), (1544, 74), (177, 448), (250, 475)]
        for node_index, (node_x, node_y) in enumerate(nodes):
            node_alpha = int(24 + 28 * (0.5 + 0.5 * math.sin(2 * math.pi * frame_index / FRAME_COUNT + node_index * 0.9)))
            node_draw.ellipse((node_x - 3, node_y - 3, node_x + 3, node_y + 3), fill=(255, 65, 78, node_alpha))
        frame = Image.alpha_composite(frame, node_layer)

        # Metallic shine is masked to the logo's original alpha, leaving its silhouette intact.
        shine_center = -175 + (logo_width + 350) * phase
        halo = np.clip(np.exp(-0.5 * ((diagonal - shine_center) / 21.0) ** 2) * 62 * travel_fade, 0, 100).astype(np.uint8)
        core = np.clip(np.exp(-0.5 * ((diagonal - shine_center) / 7.0) ** 2) * 105 * travel_fade, 0, 150).astype(np.uint8)
        halo = ((halo.astype(np.uint16) * logo_mask) // 255).astype(np.uint8)
        core = ((core.astype(np.uint16) * logo_mask) // 255).astype(np.uint8)

        logo_shine = Image.new("RGBA", (logo_width, logo_height), (255, 84, 91, 0))
        logo_shine.putalpha(Image.fromarray(halo, "L"))
        logo_core = Image.new("RGBA", (logo_width, logo_height), (255, 248, 241, 0))
        logo_core.putalpha(Image.fromarray(core, "L"))
        logo_frame = Image.alpha_composite(Image.alpha_composite(logo.copy(), logo_shine), logo_core)
        frame.alpha_composite(logo_frame, (logo_x, logo_y))
        frames.append(frame.convert("RGB"))

    return frames


def save_outputs(frames: list[Image.Image]) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)

    # Build one shared palette to reduce flicker between GIF frames.
    sample_width, sample_height = 400, 125
    montage = Image.new("RGB", (sample_width * 4, sample_height * 3))
    samples = [frame.resize((sample_width, sample_height), Image.Resampling.BILINEAR) for frame in frames[::3]]
    for index, sample in enumerate(samples[:12]):
        montage.paste(sample, ((index % 4) * sample_width, (index // 4) * sample_height))
    palette = montage.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    paletted_frames = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    paletted_frames[0].save(
        GIF_PATH,
        save_all=True,
        append_images=paletted_frames[1:],
        duration=FRAME_DURATION_MS,
        loop=0,
        optimize=True,
        disposal=1,
    )

    frames[0].save(PREVIEW_PATH)
    selected = [0, 4, 8, 12, 16, 20, 24, 28, FRAME_COUNT - 1]
    thumbs = [frames[index].resize((640, 200), Image.Resampling.LANCZOS) for index in selected]
    contact = Image.new("RGB", (640 * 3, 200 * 3), (15, 15, 18))
    for index, thumb in enumerate(thumbs):
        contact.paste(thumb, ((index % 3) * 640, (index // 3) * 200))
    contact.save(CONTACT_PATH)


def main() -> None:
    frames = build_frames()
    save_outputs(frames)
    print(f"Created: {GIF_PATH}")
    print(f"Frames: {FRAME_COUNT}; size: {WIDTH}x{HEIGHT}; duration: {FRAME_COUNT * FRAME_DURATION_MS} ms; loop: infinite")
    print(f"Preview: {PREVIEW_PATH}")
    print(f"Contact sheet: {CONTACT_PATH}")


if __name__ == "__main__":
    main()
