"""Draw the app icon and save it as PNG, ICO (Windows) and ICNS (macOS).

Run from the repository root:  python packaging/make_icons.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
S = 1024


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def font(size):
    for name in ("DejaVuSans-Bold.ttf", "Arial Bold.ttf", "arialbd.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    for p in Path("/usr/share/fonts").rglob("DejaVuSans-Bold.ttf"):
        return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def card(w, h, scene):
    """A white photo print with a small landscape on it."""
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=28, fill=(255, 255, 255, 255))
    m = 34
    px0, py0, px1, py1 = m, m, w - m, h - m
    sky = Image.new("RGB", (px1 - px0, py1 - py0))
    sd = ImageDraw.Draw(sky)
    for y in range(sky.height):
        sd.line([(0, y), (sky.width, y)], fill=lerp(scene[0], scene[1], y / sky.height))
    sd.ellipse((sky.width * 0.62, sky.height * 0.14, sky.width * 0.84, sky.height * 0.14 + sky.width * 0.22),
               fill=(255, 214, 102))
    sw, sh = sky.width, sky.height
    sd.polygon([(0, sh), (sw * 0.32, sh * 0.42), (sw * 0.62, sh)], fill=scene[2])
    sd.polygon([(sw * 0.35, sh), (sw * 0.68, sh * 0.55), (sw, sh * 0.85), (sw, sh)], fill=scene[3])
    mask = Image.new("L", sky.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, sw - 1, sh - 1), radius=14, fill=255)
    c.paste(sky, (px0, py0), mask)
    return c


def shadowed(layer, offset=(0, 18), blur=22, alpha=90):
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    a = layer.split()[3].point(lambda v: alpha if v else 0)
    sh.putalpha(a)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    out.alpha_composite(sh, offset)
    out.alpha_composite(layer)
    return out


def draw():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))

    # Background: rounded square with a deep blue -> violet gradient.
    bg = Image.new("RGB", (S, S))
    bd = ImageDraw.Draw(bg)
    for y in range(S):
        bd.line([(0, y), (S, y)], fill=lerp((37, 99, 235), (124, 58, 237), y / S))
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle((40, 40, S - 40, S - 40), radius=210, fill=255)
    img.paste(bg, (0, 0), mask)

    # Two stacked photos.
    back = card(500, 400, ((125, 211, 252), (186, 230, 253), (22, 163, 74), (21, 128, 61)))
    back = back.rotate(-12, expand=True, resample=Image.BICUBIC)
    front = card(540, 430, ((251, 146, 60), (253, 224, 71), (124, 45, 18), (154, 52, 18)))
    front = front.rotate(7, expand=True, resample=Image.BICUBIC)
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    layer.alpha_composite(back, (300, 170))
    layer.alpha_composite(front, (150, 300))
    img.alpha_composite(shadowed(layer))

    # Name tag "_1" in the corner.
    tag = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    td = ImageDraw.Draw(tag)
    box = (560, 690, 890, 860)
    td.rounded_rectangle(box, radius=60, fill=(255, 255, 255, 255))
    f = font(124)
    text = "_1"
    tb = td.textbbox((0, 0), text, font=f)
    tx = box[0] + (box[2] - box[0] - (tb[2] - tb[0])) / 2 - tb[0]
    ty = box[1] + (box[3] - box[1] - (tb[3] - tb[1])) / 2 - tb[1]
    td.text((tx, ty), text, font=f, fill=(91, 33, 182))
    img.alpha_composite(shadowed(tag, offset=(0, 12), blur=18, alpha=110))
    return img


def main():
    img = draw()
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    img.save(assets / "icon.png")
    img.save(assets / "icon.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    img.save(assets / "icon.icns")
    img.resize((256, 256), Image.LANCZOS).save(ROOT / "src" / "photo_batch_renamer" / "icon.png")
    print("icons written to", assets)


if __name__ == "__main__":
    main()
