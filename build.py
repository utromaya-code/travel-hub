#!/usr/bin/env python3
"""Собирает index.html витрины путешествий из content.json.

    python3 build.py                 -> index.html (картинки из папки img/)
    python3 build.py --inline OUT    -> одна страница с картинками внутри (для превью)
"""
import base64
import html
import json
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
C = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
META, TOURS = C["meta"], C["tours"]

FONTS = ("https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500"
         "&family=Onest:wght@400;500;600&family=Unbounded:wght@500;600&display=swap")

CSS = r"""
/* Сезонный указатель: семь фото-корешков по месяцам, затем по одной широкой главе на каждую поездку. */
:root{
  --paper:#F0F3F2; --surface:#FFFFFF; --ink:#111A1C; --ink-soft:#4C5A5D; --line:#D2DAD9;
  --stamp:#1D3EC4; --on-stamp:#FFFFFF;
  --on-photo:#FFFFFF; --scrim:rgba(6,10,12,.78); --chip-bg:rgba(255,255,255,.93); --chip-ink:#1D3EC4;
  --f-display:"Unbounded","Arial Black",system-ui,sans-serif;
  --f-body:"Onest","Segoe UI",system-ui,-apple-system,sans-serif;
  --f-mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#0B1011; --surface:#131A1C; --ink:#E4EAE9; --ink-soft:#9BA8AA; --line:#243033;
    --stamp:#8CA1FF; --on-stamp:#0B1011; color-scheme:dark;
  }
}
:root[data-theme="dark"]{
  --paper:#0B1011; --surface:#131A1C; --ink:#E4EAE9; --ink-soft:#9BA8AA; --line:#243033;
  --stamp:#8CA1FF; --on-stamp:#0B1011; color-scheme:dark;
}
*,*::before,*::after{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);font:400 1rem/1.6 var(--f-body);-webkit-font-smoothing:antialiased}
a{color:inherit}
:focus-visible{outline:2px solid var(--stamp);outline-offset:3px;border-radius:4px}
.wrap{max-width:1240px;margin-inline:auto;padding-inline:clamp(16px,4vw,40px)}

/* шапка */
.top{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding-block:1.1rem}
.brand{font:500 .78rem/1.2 var(--f-mono);letter-spacing:.14em;text-transform:uppercase}
.brand b{font-weight:500;color:var(--ink-soft)}
.top a{font:500 .85rem/1 var(--f-mono);text-decoration:none;padding:.55rem .8rem;border:1px solid var(--line);border-radius:6px}
.top a:hover{border-color:var(--ink)}

/* первый экран */
.hero{padding-block:clamp(1.5rem,5vw,3.5rem) clamp(1.25rem,3vw,2rem);display:grid;gap:1rem}
.eyebrow{margin:0;font:500 .78rem/1.3 var(--f-mono);letter-spacing:.14em;text-transform:uppercase;color:var(--stamp)}
.hero h1{margin:0;font:600 clamp(2rem,6.2vw,4.6rem)/1.04 var(--f-display);letter-spacing:-.02em;text-wrap:balance;max-width:16ch}
.lead{margin:0;max-width:60ch;font-size:clamp(1.02rem,1.6vw,1.2rem);color:var(--ink-soft)}

/* корешки */
.spines{display:flex;gap:clamp(4px,.8vw,8px);height:clamp(300px,44vw,470px)}
.spine{position:relative;flex:1 1 0;min-width:0;overflow:hidden;border-radius:4px;text-decoration:none;color:var(--on-photo);
  background:#2a3133 var(--img) var(--pos)/cover no-repeat;transition:flex-grow .55s cubic-bezier(.2,.7,.2,1)}
.spine::after{content:"";position:absolute;inset:0;background:linear-gradient(to top,rgba(6,10,12,.82) 0%,rgba(6,10,12,.15) 55%,rgba(6,10,12,.05) 100%)}
.spine-name{position:absolute;z-index:1;left:50%;bottom:3rem;writing-mode:vertical-rl;transform:translateX(-50%) rotate(180deg);
  font:600 clamp(.92rem,2.1vw,1.45rem)/1 var(--f-display);white-space:nowrap;letter-spacing:.01em}
.spine-month{position:absolute;z-index:1;left:0;right:0;bottom:.9rem;text-align:center;font:500 .72rem/1 var(--f-mono);letter-spacing:.12em;text-transform:uppercase;opacity:.9}
.spine.is-past{filter:grayscale(.85) brightness(.8)}
@media (hover:hover) and (min-width:760px){
  .spines:hover .spine{flex-grow:.75}
  .spines .spine:hover,.spines .spine:focus-visible{flex-grow:3.2}
}
.spines-note{margin:.8rem 0 0;font:400 .8rem/1.4 var(--f-mono);color:var(--ink-soft)}

/* поездки */
.trips{display:grid;gap:clamp(3.5rem,8vw,6.5rem);padding-block:clamp(3rem,7vw,5.5rem)}
.trip{scroll-margin-top:1rem}
.trip-photo{position:relative;display:block;overflow:hidden;border-radius:6px;aspect-ratio:4/5;max-width:100%;color:var(--on-photo);text-decoration:none;background:#2a3133}
@media (min-width:600px){.trip-photo{aspect-ratio:3/2}}
@media (min-width:1000px){.trip-photo{aspect-ratio:21/9}}
.photo{position:absolute;inset:0;background:var(--img) var(--pos)/cover no-repeat;transition:transform 1.4s cubic-bezier(.2,.7,.2,1)}
.trip-photo:hover .photo{transform:scale(1.035)}
.trip-photo::after{content:"";position:absolute;inset:0;background:linear-gradient(to top,var(--scrim) 0%,rgba(6,10,12,.5) 36%,rgba(6,10,12,0) 66%)}
.cap{text-shadow:0 1px 14px rgba(0,0,0,.35)}
.cap{position:absolute;z-index:1;left:0;right:0;bottom:0;padding:clamp(1rem,3.5vw,2.5rem);display:grid;gap:.35rem}
.kicker{font:500 .75rem/1.2 var(--f-mono);letter-spacing:.14em;text-transform:uppercase;opacity:.92}
.trip h2{margin:0;font:600 clamp(1.85rem,8.2vw,5.4rem)/1 var(--f-display);letter-spacing:-.02em}
.project{font:500 clamp(1rem,2vw,1.3rem)/1.3 var(--f-body)}
.stamp{position:absolute;z-index:1;top:clamp(.8rem,2.5vw,1.4rem);left:clamp(.8rem,2.5vw,1.4rem);transform:rotate(-3deg);
  background:var(--chip-bg);color:var(--chip-ink);border:1.5px solid currentColor;outline:1px solid var(--chip-bg);border-radius:4px;
  padding:.4rem .6rem;font:500 .78rem/1.15 var(--f-mono);letter-spacing:.04em;font-variant-numeric:tabular-nums}
.status{position:absolute;z-index:1;top:clamp(.8rem,2.5vw,1.4rem);right:clamp(.8rem,2.5vw,1.4rem);
  background:var(--stamp);color:var(--on-stamp);border-radius:4px;padding:.4rem .6rem;font:500 .75rem/1.15 var(--f-mono);letter-spacing:.04em}
.status.past{background:var(--chip-bg);color:#111A1C}

.trip-body{display:grid;gap:1.75rem;padding-top:clamp(1.25rem,3vw,2rem)}
@media (min-width:880px){.trip-body{grid-template-columns:minmax(0,1fr) 23rem;gap:clamp(2rem,5vw,4.5rem)}}
.trip-main{min-width:0;display:grid;gap:1rem;align-content:start}
.route{margin:0;font:500 .82rem/1.5 var(--f-mono);color:var(--stamp);letter-spacing:.02em}
.trip-text{margin:0;font-size:clamp(1.05rem,1.5vw,1.2rem);line-height:1.62;max-width:60ch}
.facts{margin:0;display:grid;grid-template-columns:7.2rem minmax(0,1fr);gap:.55rem 1rem;padding-top:1rem;border-top:1px solid var(--line)}
.facts dt{font:500 .7rem/1.9 var(--f-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--ink-soft)}
.facts dd{margin:0;font-variant-numeric:tabular-nums}
.facts .price{font:600 1.15rem/1.4 var(--f-body)}
.aside{display:grid;gap:.65rem;align-content:start}
.btn{display:flex;align-items:center;justify-content:center;gap:.5rem;min-height:3.1rem;padding:.6rem 1.2rem;border-radius:6px;
  font:600 1rem/1.2 var(--f-body);text-decoration:none;text-align:center;transition:background-color .2s,color .2s,border-color .2s}
.btn-primary{background:var(--stamp);color:var(--on-stamp);border:1.5px solid var(--stamp)}
.btn-primary:hover{filter:brightness(1.08)}
.btn-ghost{border:1.5px solid var(--ink);color:var(--ink)}
.btn-ghost:hover{background:var(--ink);color:var(--paper)}
.domain{margin:.15rem 0 0;text-align:center;font:400 .78rem/1.3 var(--f-mono);color:var(--ink-soft)}

/* как мы ездим */
.how{padding-block:clamp(3rem,7vw,5rem);border-top:1px solid var(--line)}
.how h2,.contact h2{margin:0 0 1.75rem;font:600 clamp(1.5rem,3.6vw,2.4rem)/1.1 var(--f-display);letter-spacing:-.015em;text-wrap:balance}
.how-grid{display:grid;gap:1.5rem 2rem;grid-template-columns:repeat(auto-fit,minmax(min(100%,15rem),1fr))}
.how h3{margin:0 0 .4rem;font:600 1.05rem/1.3 var(--f-body)}
.how p{margin:0;color:var(--ink-soft)}

/* контакты */
.contact{background:var(--surface);border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.contact .wrap{padding-block:clamp(3rem,7vw,5rem);display:grid;gap:1.5rem}
@media (min-width:880px){.contact .wrap{grid-template-columns:minmax(0,1fr) 23rem;align-items:end;gap:4rem}}
.contact h2{margin-bottom:.75rem}
.contact p{margin:0;max-width:52ch;color:var(--ink-soft);font-size:1.1rem}
.contact-links{display:grid;gap:.65rem}
.contact-links small{display:block;text-align:center;font:400 .78rem/1.3 var(--f-mono);color:var(--ink-soft);user-select:all}

footer{padding-block:2rem 2.5rem;font-size:.82rem;color:var(--ink-soft);display:grid;gap:.5rem}
footer a{color:var(--ink-soft)}

@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  .spine,.photo,.btn{transition:none}
  .trip-photo:hover .photo{transform:none}
}
"""

JS = r"""
(function(){
  var DAY=864e5, now=new Date(); now.setHours(0,0,0,0);
  function plural(n){var a=n%10,b=n%100;if(a===1&&b!==11)return 'день';if(a>=2&&a<=4&&(b<10||b>=20))return 'дня';return 'дней';}
  var nextFound=false;
  document.querySelectorAll('.trip').forEach(function(t){
    var s=new Date(t.dataset.start+'T00:00:00'), e=new Date(t.dataset.end+'T00:00:00');
    var badge=t.querySelector('.status'), spine=document.querySelector('.spine[href="#'+t.id+'"]');
    if(!badge||isNaN(s))return;
    if(now>e){badge.textContent='Состоялось';badge.classList.add('past');badge.hidden=false;if(spine)spine.classList.add('is-past');return;}
    if(now>=s){badge.textContent='Идёт сейчас';badge.hidden=false;nextFound=true;return;}
    if(!nextFound){var d=Math.round((s-now)/DAY);badge.textContent='Старт через '+d+' '+plural(d);badge.hidden=false;nextFound=true;}
  });
})();
"""

e = html.escape


def tg_link(t):
    msg = f"Здравствуйте! Хочу поехать: {t['name']}, «{t['project']}», {t['dates']}. Расскажите подробнее."
    return f"https://t.me/{META['telegram']}?text={quote(msg)}"


def image_css(img_src):
    rules = []
    for t in TOURS:
        rules.append(f'.t-{t["id"]}{{--img:url("{img_src(t["id"])}");--pos:{t["pos"]}}}')
    return "\n".join(rules)


def render_body():
    spines = "\n".join(
        f'    <a class="spine t-{t["id"]}" href="#{t["id"]}" aria-label="{e(t["name"])}, {e(t["dates"])}">'
        f'<span class="spine-name">{e(t["name"])}</span><span class="spine-month">{e(t["month"])}</span></a>'
        for t in TOURS)

    trips = []
    for t in TOURS:
        facts = [("Даты", e(t["dates"])), ("Длительность", e(t["days"])), ("Ведут", e(t["leaders"]))]
        if t["group"]:
            facts.append(("Группа", e(t["group"])))
        facts.append(("Стоимость", f'<span class="price">{e(t["price"])}</span>'))
        dl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in facts)
        trips.append(f"""
  <article class="trip t-{t['id']}" id="{t['id']}" data-start="{t['start']}" data-end="{t['end']}">
    <a class="trip-photo" href="{e(t['url'])}" target="_blank" rel="noopener" aria-label="{e(t['name'])}: открыть сайт поездки">
      <span class="photo" role="img" aria-label="{e(t['alt'])}"></span>
      <span class="stamp">{e(t['dates'])}</span>
      <span class="status" hidden></span>
      <div class="cap">
        <span class="kicker">{e(t['kicker'])}</span>
        <h2>{e(t['name'])}</h2>
        <span class="project">«{e(t['project'])}»</span>
      </div>
    </a>
    <div class="trip-body">
      <div class="trip-main">
        <p class="route">{e(t['route'])}</p>
        <p class="trip-text">{e(t['text'])}</p>
        <dl class="facts">{dl}</dl>
      </div>
      <div class="aside">
        <a class="btn btn-primary" href="{e(tg_link(t))}" target="_blank" rel="noopener">Записаться</a>
        <a class="btn btn-ghost" href="{e(t['url'])}" target="_blank" rel="noopener">Подробнее о поездке ↗</a>
        <p class="domain">{e(t['domain'])}</p>
      </div>
    </div>
  </article>""")

    credits = "; ".join(
        f'{e(c["what"])}: <a href="{e(c["source"])}" target="_blank" rel="noopener">{e(c["author"])}</a>, '
        f'<a href="{e(c["licenseUrl"])}" target="_blank" rel="noopener">{e(c["license"])}</a>'
        for c in C["credits"])

    tg = META["telegram"]
    return f"""
<div class="wrap top">
  <span class="brand">Авторские путешествия <b>· сезон 26/27</b></span>
  <a href="https://t.me/{tg}" target="_blank" rel="noopener">@{tg}</a>
</div>

<header class="wrap hero">
  <p class="eyebrow">Ноябрь 2026 · Август 2027</p>
  <h1>Куда мы едем в&nbsp;этом сезоне</h1>
  <p class="lead">Красное море, край Патагонии, Бали, дороги Камбоджи, Китай, Гималаи и Тибет. Выберите маршрут, откройте программу на его сайте и напишите нам, если хотите поехать.</p>
</header>

<nav class="wrap" aria-label="Все поездки сезона">
  <div class="spines">
{spines}
  </div>
  <p class="spines-note">Семь поездок по порядку дат. Нажмите на любую.</p>
</nav>

<main class="wrap trips">{''.join(trips)}
</main>

<section class="how" aria-labelledby="how-title">
  <div class="wrap">
    <h2 id="how-title">Как мы ездим</h2>
    <div class="how-grid">
      <div><h3>Небольшие группы</h3><p>Обычно до 15–20 человек. Все успевают познакомиться, никто не теряется.</p></div>
      <div><h3>Ведущие рядом весь маршрут</h3><p>Те, кто придумал поездку, едут с вами от первого до последнего дня.</p></div>
      <div><h3>Практики по желанию</h3><p>Во многих поездках утро начинается с цигуна, йоги или дыхания. Можно присоединиться, можно поспать.</p></div>
      <div><h3>Логистика на нас</h3><p>Трансферы, отели, разрешения и местные гиды. С вас билеты до старта и удобная обувь.</p></div>
    </div>
  </div>
</section>

<section class="contact" aria-labelledby="contact-title">
  <div class="wrap">
    <div>
      <h2 id="contact-title">Не знаете, что выбрать?</h2>
      <p>Напишите Андрею. Расскажем про сложность, погоду и группу каждого маршрута и подберём поездку под ваш темп.</p>
    </div>
    <div class="contact-links">
      <a class="btn btn-primary" href="https://t.me/{tg}" target="_blank" rel="noopener">Написать в Telegram</a>
      <small>@{tg}</small>
      <a class="btn btn-ghost" href="https://wa.me/{META['whatsapp']}" target="_blank" rel="noopener">Написать в WhatsApp</a>
      <small>{e(META['whatsappHuman'])}</small>
    </div>
  </div>
</section>

<footer class="wrap">
  <span>Андрей Баранов · авторские путешествия · 2026–2027</span>
  <span>Фото с Wikimedia Commons, кадрировано: {credits}. Остальные снимки из материалов поездок.</span>
</footer>
"""


def build(inline_out=None):
    if inline_out:
        def img_src(i):
            b = base64.b64encode((ROOT / "img" / f"{i}.jpg").read_bytes()).decode()
            return f"data:image/jpeg;base64,{b}"
    else:
        def img_src(i):
            return f"img/{i}.jpg"

    style = f"<style>{CSS}\n{image_css(img_src)}\n</style>"
    fonts = (f'<link rel="preconnect" href="https://fonts.googleapis.com">'
             f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
             f'<link rel="stylesheet" href="{FONTS}">')
    body = render_body()
    script = f"<script>{JS}</script>"

    if inline_out:
        page = f"<title>{e(META['title'])}</title>\n{fonts}\n{style}\n{body}\n{script}\n"
        Path(inline_out).write_text(page, encoding="utf-8")
        return

    site = META["siteUrl"].rstrip("/")
    og_img = f"{site}/img/og.jpg" if site else "img/og.jpg"
    head = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(META['title'])}</title>
<meta name="description" content="{e(META['description'])}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(META['title'])}">
<meta property="og:description" content="{e(META['description'])}">
<meta property="og:image" content="{og_img}">
<meta name="twitter:card" content="summary_large_image">
{fonts}
{style}
</head>
<body>"""
    (ROOT / "index.html").write_text(f"{head}\n{body}\n{script}\n</body>\n</html>\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--inline":
        build(sys.argv[2])
    else:
        build()
