#!/usr/bin/env python3
"""Собирает index.html витрины путешествий из content.json.

    python3 build.py                 -> index.html (картинки из папки img/)
    python3 build.py --inline OUT    -> одна страница с картинками внутри (для превью)

Места, цены и ранние тарифы меняются в content.json:
  seats   {"left": осталось, "total": всего или null, "of": "по ранней цене" или ""}
  tiers   ступени цены, state: sold (продано) / now (сейчас) / next (потом) / option (вариант)
  urgency надпись на фото, hot + hotOrder строка в блоке «Места заканчиваются»
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
/* Сезонный указатель: заголовок и горящие места, семь фото-корешков по месяцам, затем по одной широкой главе на поездку. */
:root{
  --paper:#F0F3F2; --surface:#FFFFFF; --ink:#111A1C; --ink-soft:#4C5A5D; --line:#D2DAD9;
  --stamp:#1D3EC4; --on-stamp:#FFFFFF; --stamp-wash:rgba(29,62,196,.08);
  --on-photo:#FFFFFF; --scrim:rgba(6,10,12,.78); --chip-bg:rgba(255,255,255,.93); --chip-ink:#1D3EC4;
  --f-display:"Unbounded","Arial Black",system-ui,sans-serif;
  --f-body:"Onest","Segoe UI",system-ui,-apple-system,sans-serif;
  --f-mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#0B1011; --surface:#131A1C; --ink:#E4EAE9; --ink-soft:#9BA8AA; --line:#243033;
    --stamp:#8CA1FF; --on-stamp:#0B1011; --stamp-wash:rgba(140,161,255,.1); color-scheme:dark;
  }
}
:root[data-theme="dark"]{
  --paper:#0B1011; --surface:#131A1C; --ink:#E4EAE9; --ink-soft:#9BA8AA; --line:#243033;
  --stamp:#8CA1FF; --on-stamp:#0B1011; --stamp-wash:rgba(140,161,255,.1); color-scheme:dark;
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
.intro{display:grid;gap:clamp(1.75rem,4vw,2.5rem);padding-block:clamp(1.25rem,4vw,3rem) 0;
  grid-template-areas:"text" "spines" "hot"}
@media (min-width:980px){.intro{grid-template-columns:minmax(0,1fr) 25rem;grid-template-areas:"text hot" "spines spines";column-gap:4rem;align-items:end}}
.hero{grid-area:text;display:grid;gap:1.1rem;align-content:start;min-width:0}
.eyebrow{margin:0;font:500 .78rem/1.3 var(--f-mono);letter-spacing:.14em;text-transform:uppercase;color:var(--stamp)}
.hero h1{margin:0;font:600 clamp(2rem,5.6vw,4.3rem)/1.05 var(--f-display);letter-spacing:-.02em;text-wrap:balance;max-width:17ch}
.lead{margin:0;max-width:58ch;font-size:clamp(1.02rem,1.6vw,1.2rem);color:var(--ink-soft)}
.hero-cta{display:flex;flex-wrap:wrap;align-items:center;gap:.75rem 1.25rem;padding-top:.25rem}
.hero-cta .btn{min-width:min(100%,15rem)}
.hero-cta span{font-size:.9rem;color:var(--ink-soft)}

/* горящие места */
.hot{grid-area:hot;min-width:0}
.hot h2{margin:0 0 .35rem;font:600 1.15rem/1.25 var(--f-display);letter-spacing:-.01em}
.hot>p{margin:0 0 .9rem;color:var(--ink-soft);font-size:.95rem}
.hot ul{list-style:none;margin:0;padding:0;border-top:1px solid var(--ink)}
.hot li{border-bottom:1px solid var(--line)}
.hot a{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:.1rem 1rem;align-items:baseline;padding:.65rem .1rem;text-decoration:none}
.hot a:hover .hot-name{color:var(--stamp)}
.hot-name{font:600 1rem/1.3 var(--f-body)}
.hot-name small{font:400 .78rem/1 var(--f-mono);color:var(--ink-soft);margin-left:.45rem;letter-spacing:.04em}
.hot-what{font:500 .8rem/1.3 var(--f-mono);color:var(--stamp);text-align:right}

/* корешки */
.spines-nav{grid-area:spines;min-width:0}
.spines{display:flex;gap:clamp(4px,.8vw,8px);height:clamp(300px,42vw,460px)}
.spine{position:relative;flex:1 1 0;min-width:0;overflow:hidden;border-radius:4px;text-decoration:none;color:var(--on-photo);
  background:#2a3133 var(--img) var(--pos)/cover no-repeat;transition:flex-grow .55s cubic-bezier(.2,.7,.2,1)}
.spine::after{content:"";position:absolute;inset:0;background:linear-gradient(to top,rgba(6,10,12,.82) 0%,rgba(6,10,12,.15) 55%,rgba(6,10,12,.05) 100%)}
.spine-name{position:absolute;z-index:1;left:50%;bottom:3rem;writing-mode:vertical-rl;transform:translateX(-50%) rotate(180deg);
  font:600 clamp(.92rem,2.1vw,1.45rem)/1 var(--f-display);white-space:nowrap;letter-spacing:.01em}
.spine-month{position:absolute;z-index:1;left:0;right:0;bottom:.9rem;text-align:center;font:500 .72rem/1 var(--f-mono);letter-spacing:.12em;text-transform:uppercase;opacity:.9}
.spine-seats{position:absolute;z-index:1;top:.6rem;left:50%;transform:translateX(-50%);display:grid;place-items:center;
  width:1.7rem;height:1.7rem;border-radius:50%;background:var(--chip-bg);color:var(--chip-ink);font:600 .82rem/1 var(--f-mono)}
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
.cap{position:absolute;z-index:1;left:0;right:0;bottom:0;padding:clamp(1rem,3.5vw,2.5rem);display:grid;gap:.35rem;text-shadow:0 1px 14px rgba(0,0,0,.35)}
.kicker{font:500 .75rem/1.2 var(--f-mono);letter-spacing:.14em;text-transform:uppercase;opacity:.92}
.trip h2{margin:0;font:600 clamp(1.85rem,8.2vw,5.4rem)/1 var(--f-display);letter-spacing:-.02em}
.project{font:500 clamp(1rem,2vw,1.3rem)/1.3 var(--f-body)}
.stamp{position:absolute;z-index:1;top:clamp(.8rem,2.5vw,1.4rem);left:clamp(.8rem,2.5vw,1.4rem);transform:rotate(-3deg);
  background:var(--chip-bg);color:var(--chip-ink);border:1.5px solid currentColor;outline:1px solid var(--chip-bg);border-radius:4px;
  padding:.4rem .6rem;font:500 .78rem/1.15 var(--f-mono);letter-spacing:.04em;font-variant-numeric:tabular-nums}
.chips{position:absolute;z-index:1;top:clamp(.8rem,2.5vw,1.4rem);right:clamp(.8rem,2.5vw,1.4rem);display:grid;gap:.35rem;justify-items:end;max-width:44%}
@media (max-width:599px){.stamp{max-width:46%}}
.flag,.status{border-radius:4px;padding:.4rem .6rem;font:500 .75rem/1.2 var(--f-mono);letter-spacing:.04em;text-align:right}
.flag{background:var(--stamp);color:var(--on-stamp)}
.status{background:var(--chip-bg);color:#111A1C}

.trip-body{display:grid;gap:1.75rem;padding-top:clamp(1.25rem,3vw,2rem)}
@media (min-width:880px){.trip-body{grid-template-columns:minmax(0,1fr) 23rem;gap:clamp(2rem,5vw,4.5rem)}}
.trip-main{min-width:0;display:grid;gap:1rem;align-content:start}
.route{margin:0;font:500 .82rem/1.5 var(--f-mono);color:var(--stamp);letter-spacing:.02em}
.trip-text{margin:0;font-size:clamp(1.05rem,1.5vw,1.2rem);line-height:1.62;max-width:60ch}
.facts{margin:0;display:grid;grid-template-columns:7.2rem minmax(0,1fr);gap:.55rem 1rem;padding-top:1rem;border-top:1px solid var(--line)}
.facts dt{font:500 .7rem/1.9 var(--f-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--ink-soft)}
.facts dd{margin:0;font-variant-numeric:tabular-nums}

/* правая колонка: места, цена, действия */
.aside{display:grid;gap:.7rem;align-content:start;min-width:0}
.aside-label{margin:0;font:500 .7rem/1.4 var(--f-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--ink-soft)}
.seats{display:grid;gap:.45rem;padding:.9rem 1rem;border-radius:6px;background:var(--stamp-wash)}
.seats strong{font:600 1.05rem/1.3 var(--f-body);color:var(--stamp)}
.dots{display:flex;flex-wrap:wrap;gap:5px}
.dot{width:11px;height:11px;border-radius:50%;background:var(--ink-soft);opacity:.28}
.dot.free{background:var(--stamp);opacity:1}
.ladder{margin:0;padding:0;list-style:none;display:grid}
.tier{display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:.75rem;align-items:baseline;padding:.5rem 0;border-bottom:1px solid var(--line);font-variant-numeric:tabular-nums}
.tier:first-child{border-top:1px solid var(--line)}
.tier-price{font:600 1.05rem/1.3 var(--f-body)}
.tier-label{font-size:.9rem;color:var(--ink-soft)}
.tier-state{font:500 .7rem/1 var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-soft)}
.tier.is-sold .tier-price{text-decoration:line-through;text-decoration-thickness:1.5px;color:var(--ink-soft);font-weight:500}
.tier.is-now .tier-price{font-size:1.25rem;color:var(--ink)}
.tier.is-now .tier-state{background:var(--stamp);color:var(--on-stamp);padding:.3rem .45rem;border-radius:3px}
.tier.is-next .tier-price{color:var(--ink-soft);font-weight:500}
.btn{display:flex;align-items:center;justify-content:center;gap:.5rem;min-height:3.1rem;padding:.6rem 1.2rem;border-radius:6px;
  font:600 1rem/1.2 var(--f-body);text-decoration:none;text-align:center;transition:background-color .2s,color .2s,border-color .2s}
.btn-primary{background:var(--stamp);color:var(--on-stamp);border:1.5px solid var(--stamp)}
.btn-primary:hover{filter:brightness(1.08)}
.btn-ghost{border:1.5px solid var(--ink);color:var(--ink)}
.btn-ghost:hover{background:var(--ink);color:var(--paper)}
.aside .btn-primary{margin-top:.35rem}
.micro{margin:0;font-size:.82rem;line-height:1.45;color:var(--ink-soft);text-align:center}
.domain{margin:.15rem 0 0;text-align:center;font:400 .78rem/1.3 var(--f-mono);color:var(--ink-soft)}

/* о нас */
.about{padding-block:clamp(3.5rem,8vw,6rem);border-top:1px solid var(--line);display:grid;gap:clamp(2.5rem,6vw,4.5rem)}
.about-head{display:grid;gap:1.5rem 4rem}
@media (min-width:980px){.about-head{grid-template-columns:auto minmax(0,1fr);align-items:start}}
.year{margin:0;display:grid;gap:.4rem}
.year b{font:600 clamp(5.5rem,17vw,12.5rem)/.82 var(--f-display);letter-spacing:-.05em;color:var(--stamp)}
.year span{font:500 .78rem/1.3 var(--f-mono);letter-spacing:.14em;text-transform:uppercase;color:var(--ink-soft)}
.about-text{display:grid;gap:1rem;min-width:0}
.about-text h2{margin:0 0 .25rem;font:600 clamp(1.6rem,3.8vw,2.7rem)/1.08 var(--f-display);letter-spacing:-.02em;text-wrap:balance;max-width:20ch}
.about-text p{margin:0;max-width:62ch;font-size:clamp(1.03rem,1.4vw,1.15rem);line-height:1.65}
.places{margin:.5rem 0 0;padding:0;list-style:none;display:flex;flex-wrap:wrap;gap:.45rem}
.places li{font:500 .78rem/1 var(--f-mono);letter-spacing:.04em;padding:.5rem .65rem;border:1px solid var(--line);border-radius:4px}
.sub{margin:0 0 1.25rem;font:500 .78rem/1.3 var(--f-mono);letter-spacing:.14em;text-transform:uppercase;color:var(--stamp)}
.past{display:grid;gap:clamp(6px,1vw,12px);grid-template-columns:repeat(2,minmax(0,1fr))}
@media (min-width:760px){.past{grid-template-columns:repeat(3,minmax(0,1fr))}}
.past figure{margin:0;display:grid;gap:.45rem;min-width:0}
.past img{display:block;width:100%;height:auto;max-width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:4px;background:var(--line)}
.past figcaption{font:400 .78rem/1.35 var(--f-mono);color:var(--ink-soft)}
.team{display:grid;gap:2rem clamp(1rem,2.5vw,2rem);grid-template-columns:repeat(auto-fit,minmax(min(100%,14.5rem),1fr))}
.person{display:grid;gap:.55rem;align-content:start;min-width:0}
.person img{display:block;width:100%;height:auto;max-width:100%;aspect-ratio:4/5;object-fit:cover;border-radius:4px;background:var(--line);margin-bottom:.35rem}
.person h3{margin:0;font:600 1.15rem/1.25 var(--f-body)}
.person .role{margin:0;font:500 .74rem/1.3 var(--f-mono);letter-spacing:.1em;text-transform:uppercase;color:var(--stamp)}
.person p:last-child{margin:0;color:var(--ink-soft);font-size:.95rem;line-height:1.55}
.guests{margin:1.75rem 0 0;max-width:72ch;padding-top:1.25rem;border-top:1px solid var(--line);color:var(--ink-soft)}
.trust{font-size:.9rem;color:var(--ink-soft)}
.trust a{color:var(--stamp);font-weight:500}
.top nav{display:flex;gap:.5rem}

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
    if(now>e){badge.textContent='Состоялось';badge.hidden=false;if(spine)spine.classList.add('is-past');
      var f=t.querySelector('.flag'); if(f)f.hidden=true;
      var hot=document.querySelector('.hot a[href="#'+t.id+'"]'); if(hot)hot.parentNode.hidden=true; return;}
    if(now>=s){badge.textContent='Идёт сейчас';badge.hidden=false;nextFound=true;return;}
    if(!nextFound){var d=Math.round((s-now)/DAY);badge.textContent='Старт через '+d+' '+plural(d);badge.hidden=false;nextFound=true;}
  });
})();
"""

e = html.escape
STATE = {"sold": "продано", "now": "сейчас", "next": "потом", "option": ""}


def seats_word(n):
    a, b = n % 10, n % 100
    if a == 1 and b != 11:
        return "место"
    if 2 <= a <= 4 and not 12 <= b <= 14:
        return "места"
    return "мест"


def tg(text):
    return f"https://t.me/{META['telegram']}?text={quote(text)}"


def tg_book(t):
    return tg(f"Здравствуйте! Хочу забронировать место: {t['name']}, «{t['project']}», {t['dates']}.")


def image_css(img_src):
    return "\n".join(f'.t-{t["id"]}{{--img:url("{img_src(t["id"])}");--pos:{t["pos"]}}}' for t in TOURS)


def render_seats(t):
    s = t.get("seats")
    if not s:
        return ""
    left, total, of = s["left"], s.get("total"), s.get("of", "")
    word = seats_word(left)
    if total:
        label = f"{'По ранней цене о' if of else 'О'}сталось {left} {word} из {total}"
        dots = "".join('<span class="dot free"></span>' if i >= total - left else '<span class="dot"></span>'
                       for i in range(total))
        meter = f'<span class="dots" aria-hidden="true">{dots}</span>'
    else:
        label = f"Осталось {left} {word}"
        meter = ""
    return f'<div class="seats">{meter}<strong>{e(label)}</strong></div>'


def render_ladder(t):
    rows = []
    for tier in t["tiers"]:
        st = tier.get("state", "")
        rows.append(f'<li class="tier is-{st}"><span class="tier-price">{e(tier["price"])}</span>'
                    f'<span class="tier-label">{e(tier["label"])}</span>'
                    f'<span class="tier-state">{STATE.get(st, "")}</span></li>')
    return f'<p class="aside-label">Стоимость</p><ol class="ladder">{"".join(rows)}</ol>'


def render_about(img_src):
    a = C.get("about")
    if not a:
        return ""
    paras = "".join(f"<p>{e(p)}</p>" for p in a["paragraphs"])
    places = "".join(f"<li>{e(x)}</li>" for x in a["places"])
    past = "".join(
        f'<figure><img src="{img_src(x["img"])}" alt="{e(x["cap"])}" width="600" height="600" loading="lazy" decoding="async">'
        f'<figcaption>{e(x["cap"])}</figcaption></figure>' for x in a["past"])
    team = "".join(
        f'<article class="person"><img src="{img_src(x["img"])}" alt="{e(x["name"])}" width="480" height="600" loading="lazy" decoding="async">'
        f'<h3>{e(x["name"])}</h3><p class="role">{e(x["role"])}</p><p>{e(x["bio"])}</p></article>' for x in a["team"])
    return f"""<section class="wrap about" id="about" aria-labelledby="about-title">
  <div class="about-head">
    <p class="year"><b>{e(a["since"])}</b><span>с этого года мы в пути</span></p>
    <div class="about-text">
      <p class="sub">О нас</p>
      <h2 id="about-title">{e(a["title"])}</h2>
      {paras}
      <ul class="places" aria-label="Где мы бывали">{places}</ul>
    </div>
  </div>
  <div>
    <p class="sub">Как это было</p>
    <div class="past">{past}</div>
  </div>
  <div>
    <p class="sub">Команда</p>
    <div class="team">{team}</div>
    <p class="guests">{e(a["guests"])}</p>
  </div>
</section>"""


def render_body(img_src):
    spines = "\n".join(
        f'    <a class="spine t-{t["id"]}" href="#{t["id"]}" aria-label="{e(t["name"])}, {e(t["dates"])}'
        + (f', осталось {t["seats"]["left"]} {seats_word(t["seats"]["left"])}' if t.get("seats") and not t["seats"].get("of") else "")
        + '">'
        + (f'<span class="spine-seats" aria-hidden="true">{t["seats"]["left"]}</span>' if t.get("seats") and not t["seats"].get("of") else "")
        + f'<span class="spine-name">{e(t["name"])}</span><span class="spine-month">{e(t["month"])}</span></a>'
        for t in TOURS)

    hot = sorted((t for t in TOURS if t.get("hot")), key=lambda t: t["hotOrder"])
    hot_rows = "\n".join(
        f'      <li><a href="#{t["id"]}"><span class="hot-name">{e(t["name"])}<small>{e(t["monthFull"])}</small></span>'
        f'<span class="hot-what">{e(t["hot"])}</span></a></li>' for t in hot)

    trips = []
    for t in TOURS:
        facts = [("Даты", e(t["dates"])), ("Длительность", e(t["days"])), ("Ведут", e(t["leaders"]))]
        if t["group"]:
            facts.append(("Группа", e(t["group"])))
        dl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in facts)
        flag = f'<span class="flag">{e(t["urgency"])}</span>' if t.get("urgency") else ""
        micro = ("Заявка ни к чему не обязывает. " +
                 (f"Место закрепляет предоплата {t['deposit']}." if t.get("deposit") else "Место закрепляет предоплата."))
        trips.append(f"""
  <article class="trip t-{t['id']}" id="{t['id']}" data-start="{t['start']}" data-end="{t['end']}">
    <a class="trip-photo" href="{e(t['url'])}" target="_blank" rel="noopener" aria-label="{e(t['name'])}: открыть сайт поездки">
      <span class="photo" role="img" aria-label="{e(t['alt'])}"></span>
      <span class="stamp">{e(t['dates'])}</span>
      <span class="chips">{flag}<span class="status" hidden></span></span>
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
        {render_seats(t)}
        {render_ladder(t)}
        <a class="btn btn-primary" href="{e(tg_book(t))}" target="_blank" rel="noopener">Забронировать место</a>
        <p class="micro">{e(micro)}</p>
        <a class="btn btn-ghost" href="{e(t['url'])}" target="_blank" rel="noopener">Подробнее о поездке ↗</a>
        <p class="domain">{e(t['domain'])}</p>
      </div>
    </div>
  </article>""")

    credits = "; ".join(
        f'{e(c["what"])}: <a href="{e(c["source"])}" target="_blank" rel="noopener">{e(c["author"])}</a>, '
        f'<a href="{e(c["licenseUrl"])}" target="_blank" rel="noopener">{e(c["license"])}</a>'
        for c in C["credits"])

    handle = META["telegram"]
    return f"""
<div class="wrap top">
  <span class="brand">Авторские путешествия <b>· сезон 26/27</b></span>
  <nav aria-label="Разделы"><a href="#about">О нас</a><a href="https://t.me/{handle}" target="_blank" rel="noopener">@{handle}</a></nav>
</div>

<div class="wrap intro">
  <header class="hero">
    <p class="eyebrow">Ноябрь 2026 · Август 2027</p>
    <h1>Куда поехать с&nbsp;нами в&nbsp;ближайшие месяцы</h1>
    <p class="lead">Риф Красного моря, гранит Патагонии, рисовые террасы Бали, мотоциклы на красных дорогах Камбоджи, туманы Китая, снега Канченджанги и кора вокруг Кайласа. Маленькие группы, авторские маршруты и ведущие, которые едут с вами от первого дня до последнего.</p>
    <div class="hero-cta">
      <a class="btn btn-primary" href="{e(tg('Здравствуйте! Помогите выбрать поездку.'))}" target="_blank" rel="noopener">Помочь с выбором</a>
      <span>Расскажем про сложность и группу в Telegram</span>
    </div>
    <p class="trust">Возим группы с 2009 года. <a href="#about">Кто мы</a></p>
  </header>

  <section class="hot" aria-labelledby="hot-title">
    <h2 id="hot-title">Места заканчиваются</h2>
    <p>Группы маленькие, а цена растёт по мере записи. Первые места всегда дешевле.</p>
    <ul>
{hot_rows}
    </ul>
  </section>

  <nav class="spines-nav" aria-label="Все поездки сезона">
    <div class="spines">
{spines}
    </div>
    <p class="spines-note">Семь поездок по порядку дат. Цифра в кружке: сколько мест осталось.</p>
  </nav>
</div>

<main class="wrap trips">{''.join(trips)}
</main>

{render_about(img_src)}

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
      <p>Напишите Андрею. Расскажем про сложность, погоду и группу каждого маршрута и подберём поездку под ваш темп. Пока места по ранней цене ещё есть.</p>
    </div>
    <div class="contact-links">
      <a class="btn btn-primary" href="{e(tg('Здравствуйте! Помогите выбрать поездку.'))}" target="_blank" rel="noopener">Написать в Telegram</a>
      <small>@{handle}</small>
      <a class="btn btn-ghost" href="https://wa.me/{META['whatsapp']}" target="_blank" rel="noopener">Написать в WhatsApp</a>
      <small>{e(META['whatsappHuman'])}</small>
    </div>
  </div>
</section>

<footer class="wrap">
  <span>Андрей Баранов · авторские путешествия · 2026–2027. Места и цены на {e(META.get('updated', ''))}.</span>
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
    body = render_body(img_src)
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
