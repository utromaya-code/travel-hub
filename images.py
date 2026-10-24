#!/usr/bin/env python3
"""Готовит картинки сайта из исходников в img/. Нужен Pillow: pip install pillow

    python3 images.py

  img/<id>.jpg (фото поездки, 1440 px)     -> img/<id>-1440.webp  для широких экранов
                                            -> img/<id>-800.webp   вертикальный кадр 4:5 по точке pos
                                               из content.json: фото-полосы и главы на телефоне
  img/past-*.jpg, team-*.jpg               -> .webp того же размера
  favicon.ico, apple-touch-icon.png        -> буква «П» шрифтом Unbounded, как в favicon.svg
  img/og.jpg                               -> превью ссылки 1200×630: семь полос и заголовок

Запускать после замены фото, смены pos или текста превью, затем python3 build.py.
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
IMG = ROOT / "img"
FONTS = ROOT / "tools" / "fonts"
C = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
OG = C["og"]
BLUE = "#1D3EC4"


def pos(t):
    return [float(v.rstrip("%")) / 100 for v in t["pos"].split()]


def webp(im, out, q):
    im.save(out, "WEBP", quality=q, method=6)
    print(f"{out.relative_to(ROOT)}  {im.width}×{im.height}  {out.stat().st_size // 1024} КБ")


def tour_images():
    for t in C["tours"]:
        im = Image.open(IMG / f"{t['id']}.jpg").convert("RGB")
        if im.width > 1440:
            im = im.resize((1440, round(im.height * 1440 / im.width)), Image.LANCZOS)
        webp(im, IMG / f"{t['id']}-1440.webp", 72)
        # Кадр 4:5 режется там же, где его показал бы background-position: pos,
        # поэтому то же значение pos даёт на нём ту же картинку, что и на полном фото.
        cw = min(im.width, round(im.height * 4 / 5))
        left = round((im.width - cw) * pos(t)[0])
        crop = im.crop((left, 0, left + cw, im.height))
        if crop.width > 800:
            crop = crop.resize((800, round(crop.height * 800 / crop.width)), Image.LANCZOS)
        webp(crop, IMG / f"{t['id']}-800.webp", 72)


def about_images():
    for f in sorted(IMG.glob("past-*.jpg")) + sorted(IMG.glob("team-*.jpg")):
        webp(Image.open(f).convert("RGB"), f.with_suffix(".webp"), 70)


def letter(size, radius):
    """Синий квадрат с белой «П» из Unbounded, та же геометрия, что в favicon.svg."""
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=BLUE)
    font = ImageFont.truetype(str(FONTS / "Unbounded-600.ttf"), round(size * 0.667))
    x0, y0, x1, y1 = d.textbbox((0, 0), "П", font=font)
    d.text(((size - (x1 - x0)) / 2 - x0, (size - (y1 - y0)) / 2 - y0), "П", font=font, fill="white")
    return im


def icons():
    letter(512, 112).save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    # iOS сам скругляет углы, поэтому квадрат без скругления и без прозрачности
    letter(180, 0).convert("RGB").save(ROOT / "apple-touch-icon.png", optimize=True)
    print("favicon.ico, apple-touch-icon.png")


def og_image():
    W, H, GAP = 1200, 630, 6
    og = Image.new("RGB", (W, H), "#0B1011")
    n = len(C["tours"])
    sw = (W - GAP * (n - 1)) / n
    for i, t in enumerate(C["tours"]):
        im = Image.open(IMG / f"{t['id']}.jpg").convert("RGB")
        x0, x1 = round(i * (sw + GAP)), round(i * (sw + GAP) + sw)
        scaled = im.resize((round(im.width * H / im.height), H), Image.LANCZOS)
        left = round((scaled.width - (x1 - x0)) * pos(t)[0])
        og.paste(scaled.crop((left, 0, left + x1 - x0, H)), (x0, 0))
    # затемнение сильнее к низу, чтобы читался текст
    shade = Image.new("L", (1, H))
    for y in range(H):
        k = max(0.0, (y / H - 0.25) / 0.75)
        shade.putpixel((0, y), round(255 * (0.30 + 0.55 * k ** 1.3)))
    og = Image.composite(Image.new("RGB", (W, H), (6, 10, 12)), og, shade.resize((W, H)))

    d = ImageDraw.Draw(og)
    head = ImageFont.truetype(str(FONTS / "Unbounded-600.ttf"), 104)
    sub = ImageFont.truetype(str(FONTS / "Unbounded-500.ttf"), 30)
    x, y = 64, 300
    for line in OG["title"].split("\n"):
        d.text((x, y), line, font=head, fill="white")
        y += 110
    bx0, by0, bx1, by1 = d.textbbox((0, 0), OG["subtitle"], font=sub)
    top = y + 20
    d.rounded_rectangle((x, top, x + bx1 + 36, top + by1 - by0 + 24), radius=6, fill=BLUE)
    d.text((x + 18, top + 12 - by0), OG["subtitle"], font=sub, fill="white")
    og.save(IMG / "og.jpg", "JPEG", quality=82, optimize=True, progressive=True)
    print(f"img/og.jpg  {(IMG / 'og.jpg').stat().st_size // 1024} КБ")


if __name__ == "__main__":
    tour_images()
    about_images()
    icons()
    og_image()
