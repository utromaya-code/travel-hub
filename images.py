#!/usr/bin/env python3
"""Готовит картинки сайта из исходников в img/. Нужен Pillow: pip install pillow

    python3 images.py

  img/<id>.jpg (фото поездки, до 2400 px) -> img/<id>-1440.webp, -2400.webp  для широких экранов
                                            (2400 только если исходник от 1800 px)
                                          -> img/<id>-800.webp, -1200.webp  вертикальный кадр 4:5 по точке pos
                                            из content.json: фото-полосы и главы на телефоне
  gallery.items: img/<img>.jpg           -> img/<img>-360/640/960.webp в пропорции ratio по точке pos
  about.team:    img/<img>.jpg           -> img/<img>-400.webp, -800.webp, кадр 4:5 по точке pos
  contact.photo: img/<photo>.jpg         -> img/<photo>-bg-800.webp, -bg-1280.webp, фон блока контактов
  img/review-*.jpg                       -> .webp того же размера
  favicon.ico, apple-touch-icon.png      -> буква «П» шрифтом Unbounded, как в favicon.svg
  img/og.jpg                             -> превью ссылки 1200×630: семь полос и заголовок

Все фото проходят одну цветокоррекцию (grade): снимки из разных поездок и с разных
камер выглядят одной серией. Запускать после замены фото, смены pos или текста
превью, затем python3 build.py.
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
IMG = ROOT / "img"
FONTS = ROOT / "tools" / "fonts"
C = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
OG = C["og"]
BLUE = "#1D3EC4"


def pos(item):
    return [float(v.rstrip("%")) / 100 for v in item.get("pos", "50% 50%").split()]


def webp(im, out, q, budget=None, smooth=False):
    """WebP; если файл тяжелее budget КБ, сначала (при smooth) лёгкое шумоподавление,
    потом качество снижается до 50."""
    im.save(out, "WEBP", quality=q, method=6)
    if smooth and budget and out.stat().st_size > budget * 1024:
        im = im.filter(ImageFilter.MedianFilter(3))
        im.save(out, "WEBP", quality=q, method=6)
    while budget and out.stat().st_size > budget * 1024 and q > 50:
        q -= 4
        im.save(out, "WEBP", quality=q, method=6)
    print(f"{out.relative_to(ROOT)}  {im.width}×{im.height}  q{q}  {out.stat().st_size // 1024} КБ")


def grade(im):
    """Единая цветокоррекция: выровнять тона, чуть теплее и контрастнее."""
    im = im.convert("RGB")
    # автоуровни вполсилы, чтобы сумеречные кадры не превращались в дневные
    im = Image.blend(im, ImageOps.autocontrast(im, cutoff=0.4, preserve_tone=True), 0.7)
    r, g, b = im.split()
    r = r.point(lambda v: min(255, round(v * 1.03)))
    b = b.point(lambda v: round(v * 0.97))
    im = Image.merge("RGB", (r, g, b))
    im = ImageEnhance.Contrast(im).enhance(1.06)
    return ImageEnhance.Color(im).enhance(1.04)


def source(name):
    return grade(ImageOps.exif_transpose(Image.open(IMG / f"{name}.jpg")))


def crop(im, ratio, item):
    """Кадр нужной пропорции; лишнее срезается так же, как object-position: pos."""
    w, h = (int(x) for x in ratio.split(":"))
    px, py = pos(item)
    if im.width / im.height > w / h:
        cw = round(im.height * w / h)
        left = round((im.width - cw) * px)
        return im.crop((left, 0, left + cw, im.height))
    ch = round(im.width * h / w)
    top = round((im.height - ch) * py)
    return im.crop((0, top, im.width, top + ch))


def sized(im, width):
    if im.width <= width:
        return im
    return im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)


def tour_images():
    for t in C["tours"]:
        base = sized(source(t["id"]), 2400)
        # soften: у пересвеченного по резкости исходника ореолы вокруг мелких деталей,
        # лёгкое размытие убирает их; тогда шумоподавление широких версий не нужно, а запас по весу больше
        soft = t.get("soften")
        if soft:
            base = base.filter(ImageFilter.GaussianBlur(soft))
        # Широкие версии: 1440 для обычных экранов, 2400 для ретины, если исходник это позволяет
        for w, q, budget in ((1440, 70, 200), (2400, 68, 420)):
            out = IMG / f"{t['id']}-{w}.webp"
            if w == 2400 and base.width < 1800:
                continue
            # шумный кадр: лёгкое шумоподавление вместо грубого сжатия, на экране разница не видна
            webp(sized(base, w), out, q, (budget * 3 // 2) if soft else budget, smooth=not soft)
        # Кадр 4:5 режется там же, где его показал бы background-position: pos,
        # поэтому то же значение pos даёт на нём ту же картинку, что и на полном фото.
        # 800 для полос и карточек, 1200 для телефонов с плотным экраном, если высоты исходника хватает.
        cw = min(base.width, round(base.height * 4 / 5))
        left = round((base.width - cw) * pos(t)[0])
        tall = base.crop((left, 0, left + cw, base.height))
        for w, budget in ((800, 90), (1200, 160)):
            if w == 1200 and tall.width < 1000:
                continue
            webp(sized(tall, w), IMG / f"{t['id']}-{w}.webp", 66, budget, smooth=True)


def gallery_images():
    for x in C["gallery"]["items"]:
        # лёгкое шумоподавление: снимки с телефона без него весят вдвое больше
        im = crop(source(x["img"]), x["ratio"], x).filter(ImageFilter.MedianFilter(3))
        for w, budget in ((360, 28), (640, 64), (960, 130)):
            webp(sized(im, w), IMG / f"{x['img']}-{w}.webp", 66, budget)


def team_images():
    for x in C["about"]["team"]:
        im = crop(source(x["img"]), "4:5", x)
        for w in (400, 800):
            webp(sized(im, w), IMG / f"{x['img']}-{w}.webp", 70)


def contact_image():
    name = C["contact"].get("photo")
    if not name:
        return
    # фон под тёмной вуалью: мелкие детали не видны, поэтому сжимается сильнее
    im = source(name).filter(ImageFilter.MedianFilter(3))
    for w, budget in ((800, 50), (1280, 110)):
        webp(sized(im, w), IMG / f"{name}-bg-{w}.webp", 60, budget)


def review_images():
    for f in sorted(IMG.glob("review-*.jpg")):
        webp(grade(Image.open(f)), f.with_suffix(".webp"), 72)


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
        im = source(t["id"])
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
    gallery_images()
    team_images()
    contact_image()
    review_images()
    icons()
    og_image()
