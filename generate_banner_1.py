"""
Banner Generator for Etzhaella
Generates: "Welcome to Etzhaella — Where my evolution turns into code"
Output: banner.png (1920x600)
Requirements: pip install pillow
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import random
import os


# ─── CONFIG ────────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1920, 600
OUTPUT = "banner.png"

# Color palette — deep space tech with electric accents
BG_DARK       = (4, 6, 15)
BG_MID        = (8, 14, 35)
ACCENT_CYAN   = (0, 220, 255)
ACCENT_PURPLE = (120, 60, 255)
ACCENT_GLOW   = (0, 180, 220)
WHITE         = (255, 255, 255)
SOFT_WHITE    = (200, 210, 240)
DIM_BLUE      = (40, 60, 120)

random.seed(42)


# ─── HELPERS ───────────────────────────────────────────────────────────────────

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, v))


# ─── LAYER 1 — GRADIENT BACKGROUND ────────────────────────────────────────────

def draw_background(img):
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        t = y / HEIGHT
        # Diagonal gradient: dark navy → deep purple-blue
        color = lerp_color(BG_DARK, (10, 8, 40), t)
        draw.line([(0, y), (WIDTH, y)], fill=color)

    # Subtle radial glow center-left
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx, cy = WIDTH // 3, HEIGHT // 2
    for r in range(400, 0, -4):
        alpha = int(30 * (1 - r / 400))
        gd.ellipse([cx - r, cy - r, cx + r, cy + r],
                   fill=(0, 80, 180, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    return img


# ─── LAYER 2 — STAR FIELD ─────────────────────────────────────────────────────

def draw_stars(img):
    draw = ImageDraw.Draw(img)
    for _ in range(320):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.choice([1, 1, 1, 2])
        brightness = random.randint(100, 255)
        color = (brightness, brightness, min(255, brightness + 40))
        draw.ellipse([x, y, x + size, y + size], fill=color)
    return img


# ─── LAYER 3 — CIRCUIT / CODE GRID LINES ──────────────────────────────────────

def draw_grid(img):
    draw = ImageDraw.Draw(img)
    # Faint horizontal grid
    for y in range(0, HEIGHT, 40):
        alpha_factor = 0.06 + 0.04 * math.sin(y * 0.05)
        c = int(255 * alpha_factor)
        draw.line([(0, y), (WIDTH, y)], fill=(c, c + 20, c + 60), width=1)
    # Faint vertical grid (sparse)
    for x in range(0, WIDTH, 80):
        c = int(255 * 0.04)
        draw.line([(x, 0), (x, HEIGHT)], fill=(c, c + 15, c + 50), width=1)
    return img


# ─── LAYER 4 — FLOWING CIRCUIT TRACES ─────────────────────────────────────────

def draw_circuit_traces(img):
    draw = ImageDraw.Draw(img)
    traces = [
        # (start_x, y, length, direction)
        (0,    80,  900, 1),
        (400, 140,  600, 1),
        (0,   500,  700, 1),
        (1200, 60,  720, 1),
        (1100, 520, 820, 1),
    ]
    for sx, sy, length, _ in traces:
        x, y = sx, sy
        color = (*ACCENT_CYAN[:2], 150, 60)
        segments = random.randint(4, 8)
        seg_len = length // segments
        for _ in range(segments):
            direction = random.choice(["h", "h", "h", "v"])
            if direction == "h":
                nx = x + random.randint(seg_len // 2, seg_len)
                ny = y
            else:
                nx = x
                ny = y + random.choice([-1, 1]) * random.randint(20, 60)
            nx = clamp(nx, 0, WIDTH)
            ny = clamp(ny, 0, HEIGHT)
            draw.line([(x, y), (nx, ny)], fill=(*DIM_BLUE, 80), width=1)
            # Node dot
            draw.ellipse([nx - 2, ny - 2, nx + 2, ny + 2],
                         fill=(*ACCENT_CYAN, 120))
            x, y = nx, ny
    return img


# ─── LAYER 5 — GLOWING DIAGONAL SLASH ─────────────────────────────────────────

def draw_accent_slash(img):
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    # Glowing diagonal from top-right area downward
    x1, y1 = WIDTH // 2 + 200, -30
    x2, y2 = WIDTH // 2 - 200, HEIGHT + 30
    for offset, alpha in [(-4, 15), (-2, 30), (0, 60), (2, 30), (4, 15)]:
        od.line([(x1 + offset, y1), (x2 + offset, y2)],
                fill=(*ACCENT_CYAN, alpha), width=2)
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    return img


# ─── LAYER 6 — TYPOGRAPHY ─────────────────────────────────────────────────────

def get_font(size, bold=False):
    """Try to load a system font, fallback to default."""
    candidates_bold = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:/Windows/Fonts/arialbd.ttf",
    ]
    candidates_regular = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:/Windows/Fonts/arial.ttf",
    ]
    candidates = candidates_bold if bold else candidates_regular
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_text_glow(draw, pos, text, font, glow_color, glow_radius=12):
    """Draw a glowing halo behind text."""
    x, y = pos
    for r in range(glow_radius, 0, -2):
        alpha = int(80 * (1 - r / glow_radius))
        for dx in range(-r, r + 1, 2):
            for dy in range(-r, r + 1, 2):
                if dx * dx + dy * dy <= r * r:
                    draw.text((x + dx, y + dy), text, font=font,
                              fill=(*glow_color, alpha))


def draw_typography(img):
    draw = ImageDraw.Draw(img)

    # ── "WELCOME TO" — small label above ──────────────────────────────────────
    label_font = get_font(28)
    label_text = "W E L C O M E  T O"
    lw = draw.textlength(label_text, font=label_font)
    lx = (WIDTH - lw) // 2
    ly = 155

    draw.text((lx, ly), label_text, font=label_font, fill=(*SOFT_WHITE, 180))

    # Thin separator line
    sep_y = ly + 44
    draw.line([(lx, sep_y), (lx + lw, sep_y)], fill=(*ACCENT_CYAN, 120), width=1)

    # ── "ETZHAELLA" — hero title ───────────────────────────────────────────────
    title_font = get_font(148, bold=True)
    title_text = "ETZHAELLA"
    tw = draw.textlength(title_text, font=title_font)
    tx = (WIDTH - tw) // 2
    ty = sep_y + 12

    # Glow pass
    glow_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    for r, a in [(20, 8), (12, 18), (6, 35)]:
        for dx in range(-r, r + 1, 3):
            for dy in range(-r, r + 1, 3):
                if dx * dx + dy * dy <= r * r:
                    gd.text((tx + dx, ty + dy), title_text,
                            font=title_font, fill=(*ACCENT_CYAN, a))

    img = Image.alpha_composite(img.convert("RGBA"), glow_layer).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Main title — white with slight blue tint
    draw.text((tx, ty), title_text, font=title_font, fill=(230, 240, 255))

    # Cyan highlight on first 3 chars (stylistic)
    partial_font = get_font(148, bold=True)
    draw.text((tx, ty), "ETZ", font=partial_font, fill=ACCENT_CYAN)

    # ── TAGLINE ────────────────────────────────────────────────────────────────
    tag_font = get_font(30)
    tag_text = "Where my evolution turns into code"
    tagw = draw.textlength(tag_text, font=tag_font)
    tagx = (WIDTH - tagw) // 2
    tagy = ty + 160

    # Subtle underline accent
    draw.line([(tagx - 20, tagy - 6), (tagx + tagw + 20, tagy - 6)],
              fill=(*ACCENT_PURPLE, 80), width=1)
    draw.text((tagx, tagy), tag_text, font=tag_font, fill=SOFT_WHITE)

    # ── BOTTOM ACCENT BAR ──────────────────────────────────────────────────────
    bar_y = HEIGHT - 6
    for x in range(WIDTH):
        t = x / WIDTH
        r = int(ACCENT_PURPLE[0] + (ACCENT_CYAN[0] - ACCENT_PURPLE[0]) * t)
        g = int(ACCENT_PURPLE[1] + (ACCENT_CYAN[1] - ACCENT_PURPLE[1]) * t)
        b = int(ACCENT_PURPLE[2] + (ACCENT_CYAN[2] - ACCENT_PURPLE[2]) * t)
        draw.point((x, bar_y), fill=(r, g, b))
        draw.point((x, bar_y - 1), fill=(r, g, b))
        draw.point((x, bar_y - 2), fill=(r // 2, g // 2, b // 2))

    return img


# ─── FINAL SHARPENING + VIGNETTE ──────────────────────────────────────────────

def add_vignette(img):
    vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    steps = 60
    for i in range(steps):
        t = i / steps
        alpha = int(180 * (t ** 1.8))
        margin = int(i * (min(WIDTH, HEIGHT) / (2 * steps)))
        x0, y0 = margin, margin
        x1, y1 = WIDTH - margin, HEIGHT - margin
        if x1 > x0 and y1 > y0:
            vd.rectangle([x0, y0, x1, y1], outline=(0, 0, 0, alpha), width=4)
    img = Image.alpha_composite(img.convert("RGBA"), vignette).convert("RGB")
    return img


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def generate_banner():
    print("🎨 Generating Etzhaella banner...")
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)

    img = draw_background(img)
    print("  ✓ Background gradient")

    img = draw_stars(img)
    print("  ✓ Star field")

    img = draw_grid(img)
    print("  ✓ Grid overlay")

    img = draw_circuit_traces(img)
    print("  ✓ Circuit traces")

    img = draw_accent_slash(img)
    print("  ✓ Accent slash")

    img = draw_typography(img)
    print("  ✓ Typography")

    img = add_vignette(img)
    print("  ✓ Vignette")

    img.save(OUTPUT, "PNG", optimize=True)
    print(f"\n✅ Banner saved → {OUTPUT}  ({WIDTH}×{HEIGHT}px)")


if __name__ == "__main__":
    generate_banner()
