#!/usr/bin/env python3
"""Собирает index.html клуба путешествий Шуньята из content.json.

    python3 build.py                 -> index.html (картинки из папки img/)
    python3 build.py --inline OUT    -> одна страница с картинками внутри (для превью)

Места, цены и ранние тарифы меняются в content.json:
  seats   {"left": осталось, "total": всего или null, "of": "по ранней цене", "по 4 100 €" или ""}
  waitlist true: мест нет, кнопка «Записаться в лист ожидания» (тексты в waitlist), seats.left 0
  tiers   ступени цены, state: sold (продано) / now (сейчас) / next (потом) / option (вариант)
  callout {"title", "text"} плашка в правой колонке с необязательной подписью
          при seats.left = 1 колонка, флажок на фото и строка в «Поездках по месяцам» выделены как последнее место
  urgency надпись на фото, hot статус поездки в «Поездках по месяцам» (там поездки идут по датам)
  pos     точка кадра для карточки и большого фото поездки
  reviews отзывы {"name", "trip", "text", "photo": имя файла в img/ без расширения или пусто};
          пока список пустой, секции на странице нет
  gallery снимки прошлых поездок «Как это было»: img, ratio (3:2, 4:5, 2:1), pos, col, shift, wide, cap, alt
  hero.cover  фото обложки, подпись и точки кадрирования
  season  каталог: заголовок и фильтр (tags; у поездки moods)
  manifesto, meaning, principles  фраза о маршруте, «Почему „Шуньята“», «Как мы путешествуем»
  contact.photo фон блока контактов, файл из img/ без расширения

WebP-версии фото, иконки и img/og.jpg готовит python3 images.py (нужен Pillow).
Если WebP для поездки ещё нет, страница возьмёт исходный img/<id>.jpg.
"""
import base64
import hashlib
import html
import json
import sys
from datetime import date
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
IMG = ROOT / "img"
C = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
META = C["meta"]
# Прошедшие поездки (end раньше дня сборки) на сайт не попадают: записаться на них уже нельзя.
# Между сборками скрипт на странице помечает их «Состоялось» и убирает из «Поездок по месяцам».
TODAY = date.today().isoformat()
TOURS = [t for t in C["tours"] if t["end"] >= TODAY]


FONT_FACES = """
@font-face{font-family:"Noto Serif Display";font-style:normal;font-weight:400;font-display:swap;src:url(fonts/noto-serif-display.woff) format("woff")}
@font-face{font-family:"IBM Plex Mono";font-style:normal;font-weight:400;font-display:swap;src:url(fonts/plex-mono-cyrillic-400.woff2) format("woff2");unicode-range:U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116}
@font-face{font-family:"IBM Plex Mono";font-style:normal;font-weight:400;font-display:swap;src:url(fonts/plex-mono-latin-ext-400.woff2) format("woff2");unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C4,U+2113,U+2C60-2C7F,U+A720-A7FF}
@font-face{font-family:"IBM Plex Mono";font-style:normal;font-weight:400;font-display:swap;src:url(fonts/plex-mono-latin-400.woff2) format("woff2");unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}
@font-face{font-family:"IBM Plex Mono";font-style:normal;font-weight:500;font-display:swap;src:url(fonts/plex-mono-cyrillic-500.woff2) format("woff2");unicode-range:U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116}
@font-face{font-family:"IBM Plex Mono";font-style:normal;font-weight:500;font-display:swap;src:url(fonts/plex-mono-latin-ext-500.woff2) format("woff2");unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C4,U+2113,U+2C60-2C7F,U+A720-A7FF}
@font-face{font-family:"IBM Plex Mono";font-style:normal;font-weight:500;font-display:swap;src:url(fonts/plex-mono-latin-500.woff2) format("woff2");unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}
@font-face{font-family:"Onest";font-style:normal;font-weight:400 600;font-display:swap;src:url(fonts/onest-cyrillic.woff2) format("woff2");unicode-range:U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116}
@font-face{font-family:"Onest";font-style:normal;font-weight:400 600;font-display:swap;src:url(fonts/onest-math.woff2) format("woff2");unicode-range:U+0302-0303,U+0305,U+0307-0308,U+0310,U+0312,U+0315,U+031A,U+0326-0327,U+032C,U+032F-0330,U+0332-0333,U+0338,U+033A,U+0346,U+034D,U+0391-03A1,U+03A3-03A9,U+03B1-03C9,U+03D1,U+03D5-03D6,U+03F0-03F1,U+03F4-03F5,U+2016-2017,U+2034-2038,U+203C,U+2040,U+2043,U+2047,U+2050,U+2057,U+205F,U+2070-2071,U+2074-209F,U+20D0-20DC,U+20E1,U+20E5-20EF,U+2100-2112,U+2114-2115,U+2117-2121,U+2123-214F,U+2190,U+2192,U+2194-21AE,U+21B0-21E5,U+21F1-21F2,U+21F4-2211,U+2213-2214,U+2216-22FF,U+2308-230B,U+2310,U+2319,U+231C-2321,U+2336-237A,U+237C,U+2395,U+239B-23B7,U+23D0,U+23DC-23E1,U+2474-2475,U+25AF,U+25B3,U+25B7,U+25BD,U+25C1,U+25CA,U+25CC,U+25FB,U+266D-266F,U+27C0-27FF,U+2900-2AFF,U+2B0E-2B11,U+2B30-2B4C,U+2BFE,U+3030,U+FF5B,U+FF5D,U+1D400-1D7FF,U+1EE00-1EEFF}
@font-face{font-family:"Onest";font-style:normal;font-weight:400 600;font-display:swap;src:url(fonts/onest-symbols.woff2) format("woff2");unicode-range:U+0001-000C,U+000E-001F,U+007F-009F,U+20DD-20E0,U+20E2-20E4,U+2150-218F,U+2190,U+2192,U+2194-2199,U+21AF,U+21E6-21F0,U+21F3,U+2218-2219,U+2299,U+22C4-22C6,U+2300-243F,U+2440-244A,U+2460-24FF,U+25A0-27BF,U+2800-28FF,U+2921-2922,U+2981,U+29BF,U+29EB,U+2B00-2BFF,U+4DC0-4DFF,U+FFF9-FFFB,U+10140-1018E,U+10190-1019C,U+101A0,U+101D0-101FD,U+102E0-102FB,U+10E60-10E7E,U+1D2C0-1D2D3,U+1D2E0-1D37F,U+1F000-1F0FF,U+1F100-1F1AE,U+1F1E6-1F1FF,U+1F30D-1F30F,U+1F315,U+1F31C,U+1F31E,U+1F320-1F32C,U+1F336,U+1F378,U+1F37D,U+1F382,U+1F393-1F39F,U+1F3A7-1F3A8,U+1F3AC-1F3AF,U+1F3C2,U+1F3C4-1F3C6,U+1F3CA-1F3CE,U+1F3D4-1F3E0,U+1F3ED,U+1F3F1-1F3F3,U+1F3F5-1F3F7,U+1F408,U+1F415,U+1F41F,U+1F426,U+1F43F,U+1F441-1F442,U+1F444,U+1F446-1F449,U+1F44C-1F44E,U+1F453,U+1F46A,U+1F47D,U+1F4A3,U+1F4B0,U+1F4B3,U+1F4B9,U+1F4BB,U+1F4BF,U+1F4C8-1F4CB,U+1F4D6,U+1F4DA,U+1F4DF,U+1F4E3-1F4E6,U+1F4EA-1F4ED,U+1F4F7,U+1F4F9-1F4FB,U+1F4FD-1F4FE,U+1F503,U+1F507-1F50B,U+1F50D,U+1F512-1F513,U+1F53E-1F54A,U+1F54F-1F5FA,U+1F610,U+1F650-1F67F,U+1F687,U+1F68D,U+1F691,U+1F694,U+1F698,U+1F6AD,U+1F6B2,U+1F6B9-1F6BA,U+1F6BC,U+1F6C6-1F6CF,U+1F6D3-1F6D7,U+1F6E0-1F6EA,U+1F6F0-1F6F3,U+1F6F7-1F6FC,U+1F700-1F80B,U+1F810-1F847,U+1F850-1F859,U+1F860-1F887,U+1F890-1F8AD,U+1F8B0-1F8BB,U+1F8C0-1F8C1,U+1F8D0-1F8D8,U+1F900-1F90B,U+1F93B,U+1F946,U+1F984,U+1F996,U+1F9E9,U+1FA00-1FA6F,U+1FA70-1FA7C,U+1FA80-1FAC6,U+1FAC8,U+1FACC-1FADD,U+1FADF-1FAEB,U+1FAEF-1FAFA,U+1FB00-1FBFF}
@font-face{font-family:"Onest";font-style:normal;font-weight:400 600;font-display:swap;src:url(fonts/onest-latin-ext.woff2) format("woff2");unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C4,U+2113,U+2C60-2C7F,U+A720-A7FF}
@font-face{font-family:"Onest";font-style:normal;font-weight:400 600;font-display:swap;src:url(fonts/onest-latin.woff2) format("woff2");unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}
"""

CSS = r"""
/* Клуб путешествий Шуньята: фотографическая обложка, каталог поездок, подробности маршрутов,
   манифест и «Почему Шуньята», снимки прошлых поездок, о клубе. */
:root{
  --paper:#F7F4EE; --surface:#FFFDF8; --ink:#211D19; --ink-soft:#585048; --line:#D9D1C6;
  --stamp:#873B30; --stamp-wash:rgba(135,59,48,.08);
  --night:#1A1B19; --on-night:#F7F4EE; --on-night-soft:rgba(255,250,241,.87);
  --on-photo:#FFFFFF; --scrim:rgba(6,10,12,.78); --chip-bg:rgba(255,255,255,.93);
  --fill:#873B30; --on-fill:#FFFFFF;
  --f-display:"Noto Serif Display",Georgia,serif;
  --f-body:"Onest","Segoe UI",system-ui,-apple-system,sans-serif;
  --f-mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  --gutter:max(clamp(16px,4vw,40px),env(safe-area-inset-left,0px),env(safe-area-inset-right,0px));
  --edge:max(var(--gutter),calc((100% - 1160px) / 2));
  --bar:2.75rem;
  --ease:cubic-bezier(.22,1,.36,1);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#1A1B19; --surface:#252521; --ink:#F6F0E6; --ink-soft:#C6BEB2; --line:#45413B;
    --stamp:#EDA995; --stamp-wash:rgba(237,169,149,.12); --night:#131A1C; color-scheme:dark;
  }
}
:root[data-theme="dark"]{
  --paper:#1A1B19; --surface:#252521; --ink:#F6F0E6; --ink-soft:#C6BEB2; --line:#45413B;
  --stamp:#EDA995; --stamp-wash:rgba(237,169,149,.12); --night:#131A1C; color-scheme:dark;
}
*,*::before,*::after{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);font:400 1rem/1.6 var(--f-body);-webkit-font-smoothing:antialiased;overflow-x:clip}
a{color:inherit}
p{text-wrap:pretty}
/* ссылка «к поездкам» для клавиатуры: видна только в фокусе */
.skip{position:absolute;z-index:30;left:var(--gutter);top:.75rem;padding:.6rem .9rem;border-radius:4px;background:var(--fill);color:var(--on-fill);
  font:600 .95rem/1.2 var(--f-body);text-decoration:none;transform:translateY(-200%)}
.skip:focus{transform:none}
:focus-visible{outline:2px solid var(--stamp);outline-offset:3px;border-radius:4px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap}
.wrap{max-width:1240px;margin-inline:auto;padding-inline:var(--gutter)}
picture{display:contents}

/* Обложка */
.masthead{padding-bottom:clamp(.75rem,2vw,1.5rem)}
.top{display:flex;align-items:center;justify-content:space-between;gap:1rem;width:100%;min-height:4.9rem;padding-block:.75rem}
.brand{display:inline-flex;align-items:center;gap:.6rem;white-space:nowrap;text-decoration:none}
.brand-name{font:400 clamp(1.5rem,2.8vw,2.15rem)/1 var(--f-display);letter-spacing:-.045em}
.brand small{font-size:.8rem;color:var(--ink-soft);margin-left:.35rem}
.top nav{display:flex;align-items:center;gap:clamp(.65rem,2.7vw,2.3rem)}
.top nav a{padding:.55rem 0;color:var(--ink-soft);font-size:.93rem;text-decoration:none;white-space:nowrap}
.top nav a:hover{text-decoration:underline;text-underline-offset:.25em}
.top nav .top-contact{color:var(--stamp)}
.feature{position:relative;isolation:isolate;display:grid;align-items:end;min-height:clamp(32rem,50vw,44rem);
  max-width:100rem;margin:0 auto;width:calc(100% - clamp(1.5rem,5.4vw,6rem));overflow:hidden;
  color:var(--on-night);background:#34332e}
.feature img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 45%;z-index:-2}
.feature::after{content:"";position:absolute;inset:0;z-index:-1;
  background:linear-gradient(0deg,rgba(22,20,17,.78),rgba(22,20,17,.14) 70%,transparent),
    linear-gradient(90deg,rgba(22,20,17,.50),transparent 79%)}
.hero{display:grid;justify-items:start;gap:clamp(.85rem,2vw,1.25rem);min-width:0}
.feature .hero{padding:clamp(2rem,5.8vw,5.8rem);padding-top:clamp(7rem,22vw,16rem)}
.eyebrow{margin:0;font-size:.9rem;letter-spacing:.05em}
.hero h1{margin:0;font:400 clamp(3rem,7.1vw,7.4rem)/.98 var(--f-display);letter-spacing:-.055em}
.hero h1 .ln{display:block}
.lead{margin:0;max-width:43ch;font-size:clamp(1rem,1.35vw,1.2rem);line-height:1.55;color:var(--on-night-soft)}
.hero-cta{display:flex;align-items:center;flex-wrap:wrap;gap:.6rem 1.35rem;margin-top:.25rem}
.hero-cta .btn{background:#F7F4EE;color:#211D19;border:1px solid #F7F4EE;padding-inline:1.35rem}
.hero-cta .btn:hover{background:#E7DACB;border-color:#E7DACB}
.hero-consult{color:var(--on-night);font-weight:500;text-underline-offset:.35em;text-decoration-color:rgba(255,250,241,.65);padding:.55rem 0}
.hero-consult:hover{text-decoration-color:currentColor}
.cover-caption{position:absolute;right:clamp(1.25rem,4.2vw,4rem);bottom:1.75rem;margin:0;color:var(--on-night);
  font-size:.88rem;border-top:1px solid rgba(255,250,241,.58);padding-top:.5rem}
@media (max-width:900px){.brand small{display:none}}
@media (max-width:699px){
  .top{min-height:4rem;gap:.75rem}
  .top nav a{font-size:.82rem}
  .top nav{gap:clamp(.6rem,3vw,1.1rem)}
  .feature{min-height:clamp(32rem,133vw,42rem);width:calc(100% - 1.5rem)}
  .feature .hero{padding:7rem clamp(1rem,5vw,2rem) 3.8rem}
  .feature img{object-position:50% 28%}
  .feature::after{background:linear-gradient(0deg,rgba(22,20,17,.90),rgba(22,20,17,.53) 51%,transparent 87%)}
  .hero h1{font-size:clamp(2.38rem,10.5vw,4.6rem)}
  .cover-caption{right:clamp(1rem,5vw,2rem);bottom:.9rem;font-size:.78rem}
  .hero-cta{column-gap:.9rem}
  .hero-cta .btn{padding-inline:.85rem}
}

.masthead.notfound{min-height:100svh;display:flex;flex-direction:column;background:var(--night);color:var(--on-night)}
.notfound .top nav a{color:var(--on-night-soft)}
.nf{flex:1;width:100%;display:grid;align-content:center;padding-block:3rem 5rem}
.nf .hero h1{font-size:clamp(2.5rem,6vw,5.8rem)}

/* Каталог */
.season{padding-block:clamp(3rem,6.8vw,6rem) 0}
.season-head{display:flex;align-items:end;justify-content:space-between;flex-wrap:wrap;gap:1.25rem;margin-bottom:clamp(1.5rem,3vw,2.3rem)}
.season h2{margin:0;font:400 clamp(2.65rem,4.9vw,4.8rem)/1.02 var(--f-display);letter-spacing:-.05em}
.season-filter{display:flex;flex-wrap:wrap;align-items:center;gap:.5rem}
.tag{appearance:none;cursor:pointer;padding:.48rem .85rem;border:1px solid var(--line);border-radius:99px;background:none;color:var(--ink);
  font:500 .9rem/1.2 var(--f-body);transition:border-color 150ms ease-out,background-color 150ms ease-out,color 150ms ease-out}
.tag:hover{border-color:var(--ink)}
.tag[aria-pressed="true"]{background:var(--fill);border-color:var(--fill);color:var(--on-fill)}
.season-list{list-style:none;margin:0;padding:0;display:grid;gap:clamp(1.5rem,3.4vw,3rem) clamp(1rem,2.4vw,2.25rem)}
.season-list li{min-width:0}
.season-list li[hidden],.season-list li.is-past{display:none}
.season-list a{display:flex;flex-direction:column;height:100%;border-bottom:1px solid var(--line);text-decoration:none;padding-bottom:.85rem}
.season-list h3{margin:.45rem 0 .15rem;font:400 clamp(1.85rem,3.1vw,3rem)/1.02 var(--f-display);letter-spacing:-.04em;overflow-wrap:anywhere}
.season-list a:hover h3{color:var(--stamp)}
.season-card-media{overflow:hidden;aspect-ratio:16/10;background:#D9D1C6}
.season-card-media img{display:block;width:100%;height:100%;object-fit:cover;object-position:var(--pos,50% 50%)}
.season-card-meta{display:flex;align-items:baseline;justify-content:space-between;gap:.5rem .85rem;margin-top:.8rem}
.se-dates{color:var(--ink-soft);font-size:.89rem;font-variant-numeric:tabular-nums}
.se-price{font-weight:600;font-variant-numeric:tabular-nums;white-space:nowrap}
.se-project{color:var(--ink-soft)}
.season-card-foot{display:flex;align-items:baseline;justify-content:space-between;gap:.5rem 1rem;flex-wrap:wrap;margin-top:auto;padding-top:.8rem;font-size:.88rem}
.se-action{text-decoration:underline;text-underline-offset:.27em;text-decoration-color:var(--line)}
.season-list a:hover .se-action{text-decoration-color:currentColor}
.se-what{font-weight:500;color:var(--stamp)}
.season-empty{color:var(--ink-soft);margin:1.25rem 0 0}
@media (min-width:620px){.season-list{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (min-width:1000px){
  .season-list{grid-template-columns:repeat(6,minmax(0,1fr))}
  .season-list li{grid-column:span 2}
  .season:not(:has(.tag[aria-pressed="true"],.is-past)) .season-list li:nth-child(-n+2),
  .season:not(:has(.tag[aria-pressed="true"],.is-past)) .season-list li:nth-child(n+6):nth-last-child(-n+2){grid-column:span 3}
}

/* строка поездок: появляется, пока на экране главы */
.tripnav{position:fixed;z-index:20;top:env(safe-area-inset-top,0px);left:0;right:0;background:var(--paper);border-bottom:1px solid var(--line);
  transform:translateY(-110%);visibility:hidden;transition:transform .5s var(--ease),visibility 0s linear .5s}
.tripnav.is-on{transform:none;visibility:visible;transition:transform .5s var(--ease)}
.tripnav-in{display:flex;gap:1.5rem;height:var(--bar);overflow-x:auto;scrollbar-width:none}
.tripnav-in::-webkit-scrollbar{display:none}
.tripnav a{display:flex;align-items:center;gap:.45rem;flex-shrink:0;padding-top:2px;border-bottom:2px solid transparent;
  text-decoration:none;font:600 .9rem/1 var(--f-body);color:var(--ink-soft);white-space:nowrap}
.tripnav small{font:400 .8rem/1 var(--f-body);color:var(--ink-soft)}
.tripnav a:hover{color:var(--ink)}
.tripnav a[aria-current]{color:var(--stamp);border-bottom-color:var(--stamp)}
.tripnav a.is-past{opacity:.55}
.tripnav a:focus-visible{outline-offset:-2px}

/* поездки: фото на всю ширину экрана, текст по сетке страницы */
.trips{display:grid;gap:clamp(4.5rem,10vw,8rem);padding-block:clamp(3.5rem,8vw,6.5rem)}
.trip{scroll-margin-top:calc(var(--bar) + env(safe-area-inset-top,0px))}
.trip-photo{position:relative;display:block;overflow:hidden;aspect-ratio:4/5;color:var(--on-photo);text-decoration:none;background:#34332E;max-width:100rem;margin-inline:auto;width:100%}
@media (min-width:600px){.trip-photo{aspect-ratio:auto;height:clamp(22rem,52vw,39rem)}}
.photo{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:var(--pos)}
.trip-photo::after{content:"";position:absolute;inset:0;background:linear-gradient(to top,var(--scrim) 0%,rgba(6,10,12,.45) 30%,rgba(6,10,12,0) 58%)}
.cap{position:absolute;z-index:1;left:0;right:0;bottom:0;padding:0 var(--edge) clamp(1.5rem,4.5vw,3.5rem);display:grid;gap:.55rem}
.kicker{font:500 1rem/1.3 var(--f-body);opacity:.9}
.trip h2{margin:0;font:400 clamp(2.7rem,8.1vw,8rem)/.96 var(--f-display);letter-spacing:-.06em;overflow-wrap:anywhere}
.project{font:500 clamp(1.05rem,2vw,1.4rem)/1.3 var(--f-body)}
/* даты слева, флажки справа: в одной строке, поэтому не наезжают друг на друга на любой ширине */
.badges{position:absolute;z-index:1;top:clamp(1rem,3vw,2rem);left:var(--edge);right:var(--edge);
  display:flex;justify-content:space-between;align-items:flex-start;gap:.9rem}
.stamp{flex:0 1 auto;min-width:0;background:var(--chip-bg);color:#342A24;padding:.45rem .6rem;font:500 .83rem/1.15 var(--f-body);font-variant-numeric:tabular-nums}
.chips{flex:0 1 auto;min-width:0;display:grid;gap:.35rem;justify-items:end}
.flag,.status{padding:.4rem .6rem;font:500 .85rem/1.2 var(--f-body);text-align:right}
.flag{background:var(--fill);color:var(--on-fill)}
.flag.is-last{font-weight:600}
.status{background:var(--chip-bg);color:#111A1C}

/* под фото: маршрут на всю ширину, ниже описание и правая колонка начинаются на одной линии */
.trip-body{display:grid;gap:1.75rem;padding-top:clamp(1.5rem,3.5vw,2.5rem)}
@media (min-width:880px){.trip-body{grid-template-columns:minmax(0,1fr) 23rem;column-gap:clamp(2rem,5vw,4.5rem)}.route{grid-column:1/-1}}
.trip-main{min-width:0;display:grid;gap:1rem;align-content:start}
.route{margin:0 0 -.75rem;font:500 .82rem/1.5 var(--f-mono);color:var(--stamp);letter-spacing:.02em}
.trip-text{margin:0;font-size:clamp(1.05rem,1.5vw,1.2rem);line-height:1.62;max-width:60ch}
.facts{margin:0;display:grid;grid-template-columns:7.2rem minmax(0,1fr);gap:.55rem 1rem;padding-top:1rem;border-top:1px solid var(--line)}
.facts dt{font:400 .95rem/1.6 var(--f-body);color:var(--ink-soft)}
.facts dd{margin:0;font-variant-numeric:tabular-nums}

/* правая колонка: места, цена, действия */
.aside{display:grid;gap:.7rem;align-content:start;min-width:0}
.aside-label{margin:0;font:400 .95rem/1.4 var(--f-body);color:var(--ink-soft)}
.seats{display:grid;gap:.45rem;padding:.9rem 1rem;border-radius:4px;background:var(--stamp-wash)}
.seats strong{font:600 1.05rem/1.3 var(--f-body);color:var(--stamp)}
.seats-note{font-size:.92rem;color:var(--ink-soft)}
/* последнее место: сплошной акцентный блок, самый заметный элемент колонки */
.seats.is-last{background:var(--fill);color:var(--on-fill)}
.seats.is-last strong{font-size:1.45rem;line-height:1.15;color:var(--on-fill)}
.seats.is-last .seats-note{color:var(--on-fill);opacity:.85}
.seats.is-last .dot{background:var(--on-fill);opacity:.3}
.seats.is-last .dot.free{background:var(--on-fill);opacity:1}
.dots{display:flex;flex-wrap:wrap;gap:5px}
.dot{width:11px;height:11px;border-radius:50%;background:var(--ink-soft);opacity:.28}
.dot.free{background:var(--stamp);opacity:1}
.ladder{margin:0;padding:0;list-style:none;display:grid}
.tier{display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:.75rem;align-items:baseline;padding:.5rem 0;border-bottom:1px solid var(--line);font-variant-numeric:tabular-nums}
.tier:first-child{border-top:1px solid var(--line)}
.tier-price{font:600 1.05rem/1.3 var(--f-body)}
.tier-label{font-size:.9rem;color:var(--ink-soft)}
.tier-state{font:500 .8rem/1 var(--f-body);color:var(--ink-soft)}
.tier.is-sold .tier-price{text-decoration:line-through;text-decoration-thickness:1.5px;color:var(--ink-soft);font-weight:500}
.tier.is-now .tier-price{font-size:1.25rem;color:var(--ink)}
.tier.is-now .tier-state{background:var(--fill);color:var(--on-fill);padding:.3rem .45rem;border-radius:3px}
.tier.is-next .tier-price{color:var(--ink-soft);font-weight:500}
.btn{display:flex;align-items:center;justify-content:center;gap:.5rem;min-height:3.1rem;padding:.6rem 1.2rem;border-radius:1px;
  font:600 1rem/1.2 var(--f-body);text-decoration:none;text-align:center;transition:background-color .3s var(--ease),color .3s var(--ease),border-color .3s var(--ease),transform .3s var(--ease)}
.btn:active{transform:translateY(1px)}
.btn-primary{background:var(--fill);color:var(--on-fill);border:1.5px solid var(--fill)}
.btn-primary:hover{filter:brightness(1.08)}
.btn-ghost{border:1.5px solid var(--ink);color:var(--ink)}
.btn-ghost:hover{background:var(--ink);color:var(--paper)}
.aside .btn-primary{margin-top:.35rem}
.micro{margin:0;font-size:.82rem;line-height:1.45;color:var(--ink-soft);text-align:center}
.more{justify-self:center;margin-top:.35rem;font:500 .95rem/1.4 var(--f-body);color:var(--ink);text-align:center;
  text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:.3em;text-decoration-color:var(--line);
  transition:color .3s var(--ease),text-decoration-color .3s var(--ease)}
.more:hover{color:var(--stamp);text-decoration-color:var(--stamp)}

/* как это было: снимки прошлых поездок, одна серия */
.gallery{background:var(--night);color:var(--on-night);padding-block:clamp(4rem,9vw,7rem)}
.gallery h2{margin:0 0 clamp(1.75rem,4vw,3rem);font:400 clamp(1.75rem,4.5vw,3.2rem)/1.05 var(--f-display);letter-spacing:-.02em}
/* журнальный разворот: на телефоне две колонки, ключевые кадры на всю ширину; на широком экране
   снимки разного размера на сетке из 12 колонок со сдвигами по вертикали (--col, --shift из content.json) */
.moments{columns:2;column-gap:10px}
.moments figure{margin:0 0 14px;break-inside:avoid;min-width:0}
.moments figure.wide{column-span:all;margin-bottom:18px}
.moments img{display:block;width:100%;height:auto;border-radius:2px;background:#1B2427}
@media (min-width:760px){.moments{column-gap:16px}.moments figure{margin-bottom:20px}}
@media (min-width:980px){
  .moments{columns:auto;display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:clamp(2rem,4vw,3.5rem) clamp(12px,2vw,28px);align-items:start}
  .moments figure,.moments figure.wide{grid-column:var(--col,auto / span 4);margin:var(--shift,0) 0 0}
}

/* о нас */
.about{padding-block:clamp(4rem,9vw,7rem);display:grid;gap:clamp(3rem,7vw,5rem)}
.about-head{display:grid;gap:1.5rem 4rem}
@media (min-width:980px){.about-head{grid-template-columns:auto minmax(0,1fr);align-items:start}}
/* опыт в цифрах: две большие цифры, под каждой подпись */
.stats{margin:0;padding:0;list-style:none;display:flex;flex-wrap:wrap;gap:1.5rem clamp(2rem,5vw,3.5rem);align-content:start}
@media (min-width:980px){.stats{flex-direction:column}}
.stats li{display:grid;gap:.5rem}
.stats b{font:400 clamp(4.5rem,10vw,7.5rem)/.84 var(--f-display);letter-spacing:-.05em;color:var(--stamp)}
.stats span{max-width:14ch;font:500 .95rem/1.4 var(--f-body);color:var(--ink-soft)}
.about-text{display:grid;gap:1rem;min-width:0}
.about-text h2{margin:0 0 .25rem;font:400 clamp(1.6rem,3.8vw,2.7rem)/1.08 var(--f-display);letter-spacing:-.02em;text-wrap:balance;max-width:20ch}
.about-text p{margin:0;max-width:62ch;font-size:clamp(1.03rem,1.4vw,1.15rem);line-height:1.65}
.places{margin:.5rem 0 0;padding:0;list-style:none;display:flex;flex-wrap:wrap;gap:.45rem}
.places li{font:500 .78rem/1 var(--f-mono);letter-spacing:.04em;padding:.5rem .65rem;border:1px solid var(--line);border-radius:4px}
.sub{margin:0 0 1.5rem;font:400 1.35rem/1.25 var(--f-display);letter-spacing:-.01em}
.team{display:grid;gap:2.5rem clamp(1.25rem,3vw,2.5rem);grid-template-columns:repeat(auto-fit,minmax(min(100%,16rem),1fr))}
.person{display:grid;gap:.55rem;align-content:start;min-width:0}
.person img{display:block;width:100%;height:auto;aspect-ratio:4/5;object-fit:cover;border-radius:2px;background:var(--line);margin-bottom:.5rem}
.person h3{margin:0;font:600 1.25rem/1.25 var(--f-body)}
.person .role{margin:0;font:500 .95rem/1.3 var(--f-body);color:var(--stamp)}
.person p:last-child{margin:0;color:var(--ink-soft);font-size:.95rem;line-height:1.55}
.guests{margin:2rem 0 0;max-width:72ch;padding-top:1.25rem;border-top:1px solid var(--line);color:var(--ink-soft)}

.reviews h2,.faq h2{margin:0 0 1.75rem;font:400 clamp(1.5rem,3.6vw,2.4rem)/1.1 var(--f-display);letter-spacing:-.015em;text-wrap:balance}

/* как мы путешествуем: принципы списком, без одинаковых карточек */
.principles{padding-block:clamp(3.5rem,8vw,6rem);border-top:1px solid var(--line);display:grid;gap:1.5rem}
@media (min-width:980px){.principles{grid-template-columns:minmax(0,22rem) minmax(0,1fr);column-gap:clamp(2.5rem,4.5vw,4rem);align-items:start}}
.principles h2{margin:0;font:400 clamp(1.5rem,2.8vw,2.1rem)/1.1 var(--f-display);letter-spacing:-.015em;text-wrap:balance;overflow-wrap:anywhere}
.principles ol{margin:0;padding:0;list-style:none;border-top:1px solid var(--ink)}
.principles li{display:grid;gap:.5rem 2.5rem;padding-block:1.6rem;border-bottom:1px solid var(--line)}
@media (min-width:760px) and (max-width:979px),(min-width:1200px){.principles li{grid-template-columns:minmax(0,1fr) minmax(0,1.25fr)}}
.principles h3{margin:0;font:400 clamp(1.15rem,2vw,1.45rem)/1.25 var(--f-display);letter-spacing:-.01em;text-wrap:balance}
.principles li p{margin:0;color:var(--ink-soft);line-height:1.6}

/* Фраза о свободном времени в маршруте */
.manifesto{padding-block:clamp(5rem,12vw,9rem)}
.manifesto-text{margin:0;max-width:22ch;font:400 clamp(2rem,5.4vw,4.3rem)/1.08 var(--f-display);letter-spacing:-.02em;text-wrap:balance}

/* Знак клуба: тонкое кольцо с разрывом */
.ring{display:block;overflow:visible;pointer-events:none}
.ring circle{fill:none;stroke:currentColor;stroke-width:1.5;vector-effect:non-scaling-stroke;stroke-linecap:round;
  stroke-dasharray:92 100;transform:rotate(-58deg);transform-origin:50% 50%}
.brand .ring{display:inline-block;width:1.22rem;height:1.22rem;color:var(--stamp);flex:none}
.brand .ring circle{stroke-width:2}
/* почему шуньята: текст и рассвет, кольцо вокруг солнца */
.meaning{padding-block:clamp(4rem,9vw,7rem);display:grid;gap:2rem}
@media (min-width:980px){.meaning{grid-template-columns:minmax(0,5fr) minmax(0,7fr);column-gap:clamp(2.5rem,5vw,5rem);align-items:start}}
.meaning h2{margin:0 0 1.25rem;font:400 clamp(1.9rem,4.4vw,3.4rem)/1.05 var(--f-display);letter-spacing:-.02em}
.meaning-text p{margin:0 0 1rem;max-width:56ch;font-size:clamp(1.03rem,1.4vw,1.15rem);line-height:1.65}
.meaning-zero{display:flex;gap:.75rem;align-items:flex-start;margin-top:1.75rem!important;padding-top:1.25rem;border-top:1px solid var(--line);
  color:var(--ink-soft);font-size:.95rem!important}
.meaning-zero .ring{flex:0 0 1.6rem;height:1.6rem;color:var(--stamp)}
.meaning figure{margin:0}
.meaning-photo{position:relative}
.meaning-photo img{display:block;width:100%;height:auto;border-radius:2px;background:var(--line)}
.meaning-photo .ring{position:absolute;left:var(--rx);top:var(--ry);width:var(--rd);aspect-ratio:1;transform:translate(-50%,-50%);color:#fff}
.meaning-photo .ring circle{stroke-width:2}
.meaning figcaption{padding-top:.6rem;font:400 .8rem/1.4 var(--f-mono);color:var(--ink-soft)}

/* что говорят участники */
.reviews{padding-block:clamp(3.5rem,8vw,6rem);border-top:1px solid var(--line)}
.reviews-grid{display:grid;gap:clamp(1rem,2.5vw,1.75rem);grid-template-columns:repeat(auto-fit,minmax(min(100%,19rem),1fr))}
.review{margin:0;display:grid;gap:1.25rem;align-content:space-between;padding:1.4rem 1.5rem;border:1px solid var(--line);border-radius:4px;background:var(--surface);min-width:0}
.review blockquote{margin:0}
.review blockquote p{margin:0;font-size:1.05rem;line-height:1.62}
.review figcaption{display:flex;align-items:center;gap:.8rem}
.review img{width:3rem;height:3rem;border-radius:50%;object-fit:cover;flex-shrink:0;background:var(--line)}
.review b{display:block;font:600 1rem/1.3 var(--f-body)}
.review small{display:block;margin-top:.2rem;font:500 .74rem/1.3 var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--stamp)}

/* частые сомнения */
.faq{padding-block:clamp(3.5rem,8vw,6rem);border-top:1px solid var(--line);display:grid;gap:1.5rem}
@media (min-width:980px){.faq{grid-template-columns:22rem minmax(0,1fr);gap:4.5rem}}
.faq-head h2{margin:0}
.faq-list{border-top:1px solid var(--ink);min-width:0}
.faq details{border-bottom:1px solid var(--line)}
.faq summary{list-style:none;cursor:pointer;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:1rem;align-items:baseline;padding:1.05rem .1rem;font:600 1.08rem/1.35 var(--f-body)}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";font:500 1.3rem/1 var(--f-mono);color:var(--stamp);transition:transform .3s var(--ease)}
.faq details[open] summary::after{transform:rotate(45deg)}
.faq summary:hover{color:var(--stamp)}
.faq details p{margin:0;padding:0 2.5rem 1.2rem .1rem;max-width:64ch;color:var(--ink-soft);line-height:1.62}

/* контакты: тёмный финал на фоне утренней практики */
.contact{position:relative;overflow:hidden;isolation:isolate;background:var(--night);color:var(--on-night)}
.contact-bg img{position:absolute;inset:0;z-index:-2;width:100%;height:100%;object-fit:cover;object-position:50% 70%}
.contact::before{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(100deg,rgba(6,10,12,.9) 0%,rgba(6,10,12,.72) 55%,rgba(6,10,12,.5) 100%)}
.contact .wrap{padding-block:clamp(4.5rem,11vw,8.5rem);display:grid;gap:1.75rem}
@media (min-width:880px){.contact .wrap{grid-template-columns:minmax(0,1fr) 23rem;align-items:end;gap:4rem}}
.contact h2{margin:0 0 .9rem;font:400 clamp(1.9rem,5vw,3.6rem)/1.05 var(--f-display);letter-spacing:-.02em;text-wrap:balance}
.contact p{margin:0;max-width:52ch;color:var(--on-night-soft);font-size:1.1rem}
.contact-links{display:grid;gap:.65rem}
.contact-links small{display:block;text-align:center;font:400 .78rem/1.3 var(--f-mono);color:var(--on-night-soft);user-select:all}
.contact .btn-ghost{border-color:var(--on-night);color:var(--on-night)}
.contact .btn-ghost:hover{background:var(--on-night);color:#1A1B19}

footer{padding-block:2rem 2.5rem;font-size:.82rem;color:var(--ink-soft);display:grid;gap:.5rem}
footer a{color:var(--ink-soft)}

/* плашка внизу экрана на телефоне: после первого экрана и до контактов */
.dock{position:fixed;z-index:20;left:0;right:0;bottom:0;display:flex;align-items:center;justify-content:space-between;gap:.75rem;
  padding:.6rem var(--gutter) calc(.6rem + env(safe-area-inset-bottom,0px));background:var(--surface);border-top:1px solid var(--line);
  transform:translateY(110%);visibility:hidden;transition:transform .5s var(--ease),visibility 0s linear .5s}
.dock.is-on{transform:none;visibility:visible;transition:transform .5s var(--ease)}
.dock-text{font:600 .95rem/1.25 var(--f-body)}
.dock .btn{flex-shrink:0;min-height:2.85rem;padding:.5rem 1.1rem;font-size:.95rem}
@media (min-width:1280px){.dock{display:none}}
/* на широком экране (поля от 60px) вместо нижней плашки вертикальная кнопка у правого края */
.side-cta{display:none}
@media (min-width:1280px){
  .side-cta{position:fixed;z-index:20;right:0;top:50%;display:block;padding:1.1rem .75rem;border-radius:4px 0 0 4px;
    background:var(--fill);color:var(--on-fill);font:600 .95rem/1 var(--f-body);text-decoration:none;writing-mode:vertical-rl;
    transform:translate(100%,-50%) rotate(180deg);visibility:hidden;transition:transform .5s var(--ease),visibility 0s linear .5s}
  .side-cta.is-on{transform:translate(0,-50%) rotate(180deg);visibility:visible;transition:transform .5s var(--ease)}
  .side-cta:hover{filter:brightness(1.08)}
}

@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  .btn,.top a,.tripnav,.tripnav.is-on,.dock,.dock.is-on,.side-cta,.side-cta.is-on,.faq summary::after{transition:none}
  .btn:active{transform:none}
}
"""


JS = r"""
(function(){
  var DAY=864e5, now=new Date(); now.setHours(0,0,0,0);
  function plural(n){var a=n%10,b=n%100;if(a===1&&b!==11)return 'день';if(a>=2&&a<=4&&(b<10||b>=20))return 'дня';return 'дней';}
  var nextFound=false;
  document.querySelectorAll('.trip').forEach(function(t){
    var s=new Date(t.dataset.start+'T00:00:00'), e=new Date(t.dataset.end+'T00:00:00');
    var badge=t.querySelector('.status'), link=document.querySelector('.tripnav a[href="#'+t.id+'"]');
    if(!badge||isNaN(s))return;
    if(now>e){badge.textContent='Состоялось';badge.hidden=false;if(link)link.classList.add('is-past');
      var f=t.querySelector('.flag'); if(f)f.hidden=true;
      var row=document.querySelector('.season-list a[href="#'+t.id+'"]'); if(row)row.parentNode.classList.add('is-past'); return;}
    if(now>=s){badge.textContent='Идёт сейчас';badge.hidden=false;nextFound=true;return;}
    if(!nextFound){var d=Math.round((s-now)/DAY);badge.textContent='Старт через '+d+' '+plural(d);badge.hidden=false;nextFound=true;}
  });

  // Один тег оставляет в списке подходящие поездки, повторное нажатие показывает все
  var tags=document.querySelectorAll('.tag'), rows=document.querySelectorAll('.season-list li');
  var empty=document.querySelector('.season-empty');
  tags.forEach(function(tg){tg.addEventListener('click',function(){
    var on=tg.getAttribute('aria-pressed')!=='true';
    tags.forEach(function(x){x.setAttribute('aria-pressed','false');});
    if(on)tg.setAttribute('aria-pressed','true');
    rows.forEach(function(li){li.hidden=on&&li.dataset.moods.split(' ').indexOf(tg.dataset.mood)<0;});
    empty.hidden=Array.from(rows).some(function(li){return !li.hidden&&!li.classList.contains('is-past');});
  });});

  if(!('IntersectionObserver' in window))return;
  var smooth=!matchMedia('(prefers-reduced-motion: reduce)').matches;

  // строка поездок видна, пока главы пересекают верх экрана; текущая глава подсвечена
  var nav=document.querySelector('.tripnav'), trips=document.querySelector('.trips');
  if(nav&&trips){
    var row=nav.querySelector('.tripnav-in');
    new IntersectionObserver(function(es){nav.classList.toggle('is-on',es[0].isIntersecting);},{rootMargin:'0px 0px -99% 0px'}).observe(trips);
    var current=new IntersectionObserver(function(es){es.forEach(function(en){
      if(!en.isIntersecting)return;
      row.querySelectorAll('a').forEach(function(a){
        if(a.getAttribute('href')!=='#'+en.target.id){a.removeAttribute('aria-current');return;}
        a.setAttribute('aria-current','true');
        var r=a.getBoundingClientRect(), b=row.getBoundingClientRect();
        if(r.left<b.left||r.right>b.right)row.scrollTo({left:row.scrollLeft+r.left-b.left-(b.width-r.width)/2,behavior:smooth?'smooth':'auto'});
      });
    });},{rootMargin:'-40% 0px -55% 0px'});
    document.querySelectorAll('.trip').forEach(function(t){current.observe(t);});
  }

  // плашка «Помочь с выбором»: первый экран уже прокручен, а до контактов ещё не дошли
  var dock=document.querySelector('.dock'), hero=document.querySelector('.masthead'), contact=document.querySelector('.contact');
  if(dock&&hero&&contact){
    var passed=false, reached=false;
    var side=document.querySelector('.side-cta');
    var show=function(){var on=passed&&!reached;dock.classList.toggle('is-on',on);if(side)side.classList.toggle('is-on',on);};
    new IntersectionObserver(function(es){var en=es[0];passed=!en.isIntersecting&&en.boundingClientRect.top<0;show();}).observe(hero);
    new IntersectionObserver(function(es){var en=es[0];reached=en.isIntersecting||en.boundingClientRect.top<0;show();}).observe(contact);
  }
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
    if t.get("waitlist"):
        return tg(f"Здравствуйте! Хочу в лист ожидания: {t['name']}, «{t['project']}», {t['dates']}.")
    return tg(f"Здравствуйте! Хочу забронировать место: {t['name']}, «{t['project']}», {t['dates']}.")


def lines(text):
    return "<br>".join(e(x) for x in text.split("\n"))


def variant(i, size):
    """WebP-версия фото поездки из images.py, а если её нет, исходный JPEG."""
    name = f"{i}-{size}.webp"
    return name if (IMG / name).exists() else f"{i}.jpg"


def picture(src, name, attrs):
    """<img> из img/<name>.jpg с WebP-версией рядом, если она есть."""
    webp = f"{name}.webp"
    img = f'<img src="{src(name + ".jpg")}" {attrs}>'
    if not (IMG / webp).exists():
        return img
    return f'<picture><source srcset="{src(webp)}" type="image/webp">{img}</picture>'


def webp_variants(name, widths):
    return [(w, f"{name}-{w}.webp") for w in widths if (IMG / f"{name}-{w}.webp").exists()]


def webp_source(src, images, sizes, media=""):
    if not images:
        return ""
    srcset = ", ".join(f"{src(f)} {w}w" for w, f in images)
    mq = f' media="{media}"' if media else ""
    return f'<source{mq} srcset="{srcset}" sizes="{sizes}" type="image/webp">'


def variants(src, name, widths, sizes, attrs, inline=False, jpg=None):
    """<picture> с WebP-версиями img/<name>-<ширина>.webp из images.py; браузер берёт нужную ширину.
    Запасной вариант и замена, если версий нет: исходный img/<jpg или name>.jpg."""
    have = webp_variants(name, widths)
    img = f'<img src="{src((jpg or name) + ".jpg")}" {attrs}>'
    if not have:
        return img
    if inline:
        return f'<img src="{src(have[-1][1])}" {attrs}>'
    return f'<picture>{webp_source(src, have, sizes)}{img}</picture>'


def image_css():
    return "\n".join(f'.t-{t["id"]}{{--pos:{t["pos"]}}}' for t in TOURS)


def render_photo(t, src, inline):
    # Все главы ниже первого экрана, поэтому грузятся по мере прокрутки.
    # На узком экране вертикальный кадр 800/1200, на широком полное фото 1440/2400: браузер берёт по плотности экрана.
    i = t["id"]
    attrs = f'class="photo" alt="{e(t["alt"])}" loading="lazy" decoding="async"'
    if inline:
        return f'<img src="{src(variant(i, 1440))}" {attrs}>'

    tall = webp_variants(i, (800, 1200))
    wide = webp_variants(i, (1440, 2400))
    sources = webp_source(src, tall, "100vw", "(max-width:599px)")
    sources += webp_source(src, wide, "(max-width:1600px) 100vw, 1600px")
    return f'<picture>{sources}<img src="{src(i + ".jpg")}" {attrs}></picture>'


def is_last(t):
    s = t.get("seats")
    return bool(s) and s["left"] == 1 and not s.get("of")


def render_seats(t):
    s = t.get("seats")
    if not s:
        c = t.get("callout")
        if not c:
            return ""
        note = f'<span class="seats-note">{e(c["text"])}</span>' if c.get("text") else ""
        return f'<div class="seats"><strong>{e(c["title"])}</strong>{note}</div>'
    if t.get("waitlist"):
        W = C["waitlist"]
        return f'<div class="seats"><strong>{e(W["title"])}</strong></div>'
    left, total, of = s["left"], s.get("total"), s.get("of", "")
    word = seats_word(left)
    # of: «по ранней цене», «по 4 100 €»: с ним «По ранней цене осталось 1 место из 5»
    lead = f"{of[:1].upper()}{of[1:]} осталось" if of else "Осталось"
    if total:
        label = f"{lead} {left} {word} из {total}"
        dots = "".join('<span class="dot free"></span>' if i >= total - left else '<span class="dot"></span>'
                       for i in range(total))
        meter = f'<span class="dots" aria-hidden="true">{dots}</span>'
    else:
        label = f"Осталось {left} {word}"
        meter = ""
    if is_last(t):
        return f'<div class="seats is-last">{meter}<strong>Последнее место</strong><span class="seats-note">{e(label)}</span></div>'
    return f'<div class="seats">{meter}<strong>{e(label)}</strong></div>'


def render_ladder(t):
    rows = []
    for tier in t["tiers"]:
        st = tier.get("state", "")
        rows.append(f'<li class="tier is-{st}"><span class="tier-price">{e(tier["price"])}</span>'
                    f'<span class="tier-label">{e(tier["label"])}</span>'
                    f'<span class="tier-state">{STATE.get(st, "")}</span></li>')
    return f'<p class="aside-label">Стоимость</p><ol class="ladder">{"".join(rows)}</ol>'


def render_gallery(src, inline):
    g = C.get("gallery")
    if not g or not g["items"]:
        return ""
    figs = []
    for x in g["items"]:
        w, h = (int(v) for v in x["ratio"].split(":"))
        attrs = (f'alt="{e(x["alt"])}" width="960" height="{round(960 * h / w)}" '
                 f'loading="lazy" decoding="async"')
        # ширина на сетке: столько колонок из 12, сколько занимает --col (на широком экране ~97px колонка)
        a, z = (int(v) for v in x.get("col", "1 / 5").split("/"))
        wide = x.get("wide")
        sizes = (f"(max-width:979px) {'100vw' if wide else '50vw'}, {round((z - a) * 1160 / 12)}px")
        pic = variants(src, x["img"], (360, 640, 960), sizes, attrs, inline)
        style = f'--col:{x.get("col", "auto / span 4")};--shift:{x.get("shift", "0")}'
        # без подписей: коллаж; место съёмки остаётся в cap в content.json и в alt
        cls = ' class="wide"' if wide else ''
        figs.append(f'<figure{cls} style="{style}">{pic}</figure>')
    return f"""<section class="gallery" id="moments" aria-labelledby="moments-title">
  <div class="wrap">
    <h2 id="moments-title">{e(g["title"])}</h2>
    <div class="moments">{"".join(figs)}</div>
  </div>
</section>"""


def season_price(t):
    current = [tier["price"] for tier in t["tiers"] if tier.get("state") == "now"]
    prices = current or [tier["price"] for tier in t["tiers"] if tier.get("state") == "option"]
    if len(prices) == 1:
        return prices[0]
    if not prices:
        return ""
    values = []
    for price in prices:
        parts = price.rsplit(maxsplit=1)
        if len(parts) != 2:
            return ""
        amount, currency = parts
        digits = "".join(amount.split())
        if not digits.isdecimal():
            return ""
        values.append((int(digits), currency, price))
    return f"от {min(values)[2]}" if len({v[1] for v in values}) == 1 else ""


def render_season(src, inline):
    S = C["season"]
    tags = "".join(f'<button type="button" class="tag" data-mood="{x["id"]}" aria-pressed="false">{e(x["label"])}</button>'
                   for x in S.get("tags", []))
    rows = []
    for i, t in enumerate(sorted(TOURS, key=lambda t: t["start"])):
        wide_card = i < 2 or (i >= 5 and i >= len(TOURS) - 2)
        column_sizes = "46vw, 560px" if wide_card else "31vw, 370px"
        card_sizes = f"(max-width:619px) 92vw, (max-width:999px) 46vw, (max-width:1239px) {column_sizes}"
        attrs = 'alt="" loading="lazy" decoding="async" width="960" height="600"'
        pic = variants(src, f'{t["id"]}-card', (480, 960), card_sizes, attrs, inline, t["id"])
        price = season_price(t)
        price_label = f'<span class="se-price">{e(price)}</span>' if price else ""
        status = "Лист ожидания" if t.get("waitlist") else t.get("hot", "")
        status_label = f'<span class="se-what">{e(status)}</span>' if status and status != "Запись открыта" else ""
        rows.append(f'''<li data-moods="{" ".join(t.get("moods", []))}">
  <a href="#{t["id"]}">
    <div class="season-card-media t-{t["id"]}">{pic}</div>
    <div class="season-card-meta"><span class="se-dates">{e(t["dates"])}</span>{price_label}</div>
    <h3>{e(t["name"])}</h3>
    <span class="se-project">{e(t["project"])}</span>
    <span class="season-card-foot"><span class="se-action">Программа</span>{status_label}</span>
  </a>
</li>''')
    flt = (f'<div class="season-filter" role="group" aria-label="{e(S["filter"])}">{tags}</div>'
           if tags else "")
    return f"""<section class="wrap season" id="season" aria-labelledby="season-title">
  <div class="season-head">
    <h2 id="season-title">{e(S["title"])}</h2>
    {flt}
  </div>
  <ul class="season-list" aria-live="polite">{"".join(rows)}</ul>
  <p class="season-empty" role="status"{' hidden' if rows else ''}>По этому направлению пока нет поездок.</p>
</section>"""


def render_principles():
    p = C.get("principles")
    if not p:
        return ""
    items = "".join(f'<li><h3>{e(x["t"])}</h3><p>{e(x["d"])}</p></li>'
                    for x in p["items"])
    return f"""<section class="wrap principles" id="why" aria-labelledby="principles-title">
  <h2 id="principles-title">{e(p["title"])}</h2>
  <ol>{items}</ol>
</section>"""


RING = '<svg class="ring" viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="48" pathLength="100"/></svg>'


def render_meaning(src, inline):
    """Почему шуньята: что значит слово и при чём тут путешествия; фото с кольцом вокруг солнца."""
    m = C.get("meaning")
    if not m:
        return ""
    paras = "".join(f"<p>{e(x)}</p>" for x in m["paragraphs"])
    zero = f'<p class="meaning-zero">{RING}<span>{e(m["zero"])}</span></p>' if m.get("zero") else ""
    ph, fig = m.get("photo"), ""
    if ph:
        w, h = (int(v) for v in ph["ratio"].split(":"))
        attrs = f'alt="{e(ph["alt"])}" width="960" height="{round(960 * h / w)}" loading="lazy" decoding="async"'
        pic = variants(src, ph["img"], (360, 640, 960), "(max-width:979px) 100vw, 680px", attrs, inline)
        r = ph.get("ring", {})
        style = f' style="--rx:{r["x"]};--ry:{r["y"]};--rd:{r["d"]}"' if r else ""
        fig = (f'<figure><div class="meaning-photo"{style}>{pic}{RING if r else ""}</div>'
               f'<figcaption>{e(ph["cap"])}</figcaption></figure>')
    return f"""<section class="wrap meaning" id="shunyata" aria-labelledby="meaning-title">
  <div class="meaning-text">
    <h2 id="meaning-title">{e(m["title"])}</h2>
    {paras}{zero}
  </div>
  {fig}
</section>"""


def render_manifesto():
    m = C.get("manifesto")
    if not m:
        return ""
    return f"""<section class="wrap manifesto">
  <p class="manifesto-text">{lines(m["text"])}</p>
</section>"""


def render_faq():
    f = C.get("faq")
    if not f:
        return ""
    items = "".join(f'<details><summary>{e(x["q"])}</summary><p>{e(x["a"])}</p></details>' for x in f["items"])
    return f"""<section class="wrap faq" id="faq" aria-labelledby="faq-title">
  <div class="faq-head"><h2 id="faq-title">{e(f["title"])}</h2></div>
  <div class="faq-list">{items}</div>
</section>"""


def render_reviews(src):
    items = C.get("reviews") or []
    if not items:
        return ""
    cards = []
    for r in items:
        photo = (picture(src, r["photo"], 'alt="" width="96" height="96" loading="lazy" decoding="async"')
                 if r.get("photo") else "")
        cards.append(f'<figure class="review"><blockquote><p>{e(r["text"])}</p></blockquote>'
                     f'<figcaption>{photo}<span><b>{e(r["name"])}</b><small>{e(r["trip"])}</small></span></figcaption></figure>')
    return f"""<section class="wrap reviews" id="reviews" aria-labelledby="reviews-title">
  <h2 id="reviews-title">{e(C.get("reviewsTitle", "Что говорят участники"))}</h2>
  <div class="reviews-grid">{"".join(cards)}</div>
</section>"""


def render_about(src, inline):
    a = C.get("about")
    if not a:
        return ""
    paras = "".join(f"<p>{e(p)}</p>" for p in a["paragraphs"])
    places = "".join(f"<li>{e(x)}</li>" for x in a["places"])
    team = []
    for x in a["team"]:
        attrs = f'alt="{e(x["name"])}" width="800" height="1000" loading="lazy" decoding="async"'
        pic = variants(src, x["img"], (400, 800), "(max-width:599px) 100vw, (max-width:979px) 50vw, 380px", attrs, inline)
        team.append(f'<article class="person">{pic}<h3>{e(x["name"])}</h3>'
                    f'<p class="role">{e(x["role"])}</p><p>{e(x["bio"])}</p></article>')
    guests = f'\n    <p class="guests">{e(a["guests"])}</p>' if a.get("guests") else ""
    return f"""<section class="wrap about" id="about" aria-labelledby="about-title">
  <div class="about-head">
    <ul class="stats">{"".join(f'<li><b>{e(x["num"])}</b><span>{e(x["label"])}</span></li>' for x in a["stats"])}</ul>
    <div class="about-text">
      <h2 id="about-title">{e(a["title"])}</h2>
      {paras}
      <ul class="places" aria-label="Где мы бывали">{places}</ul>
    </div>
  </div>
  <div>
    <h3 class="sub">Команда</h3>
    <div class="team">{"".join(team)}</div>{guests}
  </div>
</section>"""


def render_contact(src, inline, choose, handle):
    CT = C["contact"]
    bg = ""
    if CT.get("photo"):
        pic = variants(src, f'{CT["photo"]}-bg', (800, 1280), "100vw",
                       'alt="" width="1280" height="960" loading="lazy" decoding="async"', inline, CT["photo"])
        bg = f'<div class="contact-bg" aria-hidden="true">{pic}</div>'
    return f"""<section class="contact" aria-labelledby="contact-title">
  {bg}
  <div class="wrap">
    <div>
      <h2 id="contact-title">{e(CT["title"])}</h2>
      <p>{e(CT["text"])}</p>
    </div>
    <div class="contact-links">
      <a class="btn btn-primary" href="{choose}" target="_blank" rel="noopener">{e(CT["telegram"])}</a>
      <small>@{handle}</small>
      <a class="btn btn-ghost" href="https://wa.me/{META['whatsapp']}" target="_blank" rel="noopener">{e(CT["whatsapp"])}</a>
      <small>{e(META['whatsappHuman'])}</small>
    </div>
  </div>
</section>"""


def render_cover(src, cover, inline):
    name = cover["img"]
    attrs = f'alt="{e(cover["alt"])}" width="1600" height="900" fetchpriority="high" loading="eager"'
    wide = webp_variants(f"{name}-cover", (960, 1600))
    if inline:
        image = wide[-1][1] if wide else name + ".jpg"
        return f'<img src="{src(image)}" {attrs}>'
    tall = webp_variants(f"{name}-cover-portrait", (640, 960))
    sources = webp_source(src, tall, "calc(100vw - 24px)", "(max-width:699px)")
    sources += webp_source(src, wide, "(max-width:1690px) 95vw, 1600px")
    return f'<picture>{sources}<img src="{src(name + ".jpg")}" {attrs}></picture>'


def render_brand(link=False):
    tag = 'a href="./"' if link else 'span'
    end = "a" if link else "span"
    ring = RING if C.get("ring") else ""
    return (f'<{tag} class="brand">{ring}<span class="brand-name">{e(C["brand"])}</span>'
            f'<small>{e(C["brandSub"])}</small></{end}>')


def render_body(src, inline=False):
    H = C["hero"]
    nav_links = "".join(f'<a href="#{t["id"]}">{e(t["name"])} <small>{e(t["monthFull"])}</small></a>' for t in TOURS)

    trips = []
    for t in TOURS:
        facts = [("Даты", e(t["dates"])), ("Длительность", e(t["days"])), ("Ведут", e(t["leaders"]))]
        if t["group"]:
            facts.append(("Группа", e(t["group"])))
        dl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in facts)
        flag = (f'<span class="flag{" is-last" if is_last(t) else ""}">{e(t["urgency"])}</span>'
                if t.get("urgency") else "")
        book = "Забронировать место"
        micro = ""
        if t.get("waitlist"):
            book = C["waitlist"]["button"]
        else:
            deposit = f' {e(t["deposit"])}' if t.get("deposit") else ""
            micro = f'\n        <p class="micro">Место закрепляет предоплата{deposit}.</p>'
        trips.append(f"""
  <article class="trip t-{t['id']}" id="{t['id']}" data-start="{t['start']}" data-end="{t['end']}">
    <a class="trip-photo" href="{e(t['url'])}" target="_blank" rel="noopener" aria-label="{e(t['name'])}: открыть сайт поездки">
      {render_photo(t, src, inline)}
      <span class="badges"><span class="stamp">{e(t['dates'])}</span><span class="chips">{flag}<span class="status" hidden></span></span></span>
      <div class="cap">
        <span class="kicker">{e(t['kicker'])}</span>
        <h2>{e(t['name'])}</h2>
        <span class="project">«{e(t['project'])}»</span>
      </div>
    </a>
    <div class="wrap trip-body">
      <p class="route">{e(t['route'])}</p>
      <div class="trip-main">
        <p class="trip-text">{e(t['text'])}</p>
        <dl class="facts">{dl}</dl>
      </div>
      <div class="aside">
        {render_seats(t)}
        {render_ladder(t)}
        <a class="btn btn-primary" href="{e(tg_book(t))}" target="_blank" rel="noopener">{e(book)}</a>{micro}
        <a class="more" href="{e(t['url'])}" target="_blank" rel="noopener">{e(C['tripLink'])} · {e(t['domain'])} <span aria-hidden="true">↗</span></a>
      </div>
    </div>
  </article>""")

    credits = "; ".join(
        f'{e(c["what"])}: <a href="{e(c["source"])}" target="_blank" rel="noopener">{e(c["author"])}</a>, '
        f'<a href="{e(c["licenseUrl"])}" target="_blank" rel="noopener">{e(c["license"])}</a>'
        for c in C["credits"])

    handle = META["telegram"]
    choose = e(tg(H["ctaMessage"]))
    return f"""
<div class="masthead">
  <div class="wrap top">
    {render_brand()}
    <nav aria-label="Разделы">
      <a href="#season">{e(C["nav"]["season"])}</a>
      <a href="#about">{e(C["nav"]["about"])}</a>
      <a class="top-contact" href="https://t.me/{handle}" target="_blank" rel="noopener">Telegram</a>
    </nav>
  </div>
  <div class="feature">
    {render_cover(src, H["cover"], inline)}
    <header class="hero">
      <p class="eyebrow">{e(H["eyebrow"])}</p>
      <h1>{" ".join(f'<span class="ln">{e(x)}</span>' for x in H["title"].splitlines())}</h1>
      <p class="lead">{e(H["lead"])}</p>
      <div class="hero-cta">
        <a class="btn btn-primary" href="#season">Посмотреть поездки</a>
        <a class="hero-consult" href="{choose}" target="_blank" rel="noopener">Спросить Андрея</a>
      </div>
    </header>
    <p class="cover-caption">{e(H["cover"]["caption"])}</p>
  </div>
</div>

{render_season(src, inline)}

<nav class="tripnav" aria-label="{e(C["tripNav"])}"><div class="wrap tripnav-in">{nav_links}</div></nav>

<main class="trips" id="trips">{''.join(trips)}
</main>

{render_gallery(src, inline)}

{render_manifesto()}

{render_meaning(src, inline)}

{render_about(src, inline)}

{render_principles()}

{render_reviews(src)}

{render_faq()}

{render_contact(src, inline, choose, handle)}

<footer class="wrap">
  <span>{e(C["brandSub"])} {e(C["brand"])} · Андрей Баранов · 2026–2027. Места и цены на {e(META.get('updated', ''))}.</span>
  <span>Фото с Wikimedia Commons, кадрировано: {credits}. Остальные снимки из материалов поездок.</span>
</footer>

<a class="side-cta" href="{choose}" target="_blank" rel="noopener">{e(C['sideCta'])}</a>

<div class="dock">
  <span class="dock-text">{e(C["dock"]["label"])}</span>
  <a class="btn btn-primary" href="{choose}" target="_blank" rel="noopener">{e(H["cta"])}</a>
</div>
"""


def build(inline_out=None):
    if inline_out:
        def src(name):
            mime = "image/webp" if name.endswith(".webp") else "image/jpeg"
            return f"data:{mime};base64,{base64.b64encode((IMG / name).read_bytes()).decode()}"
    else:
        def src(name):
            return f"img/{name}"

    body = render_body(src, inline=bool(inline_out))
    script = f"<script>{JS}</script>"

    if inline_out:
        style = f"<style>{CSS}\n{image_css()}\n</style>"
        fonts = (f'<link rel="preconnect" href="https://fonts.googleapis.com">'
                 f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
                 '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&amp;family=Noto+Serif+Display&amp;family=Onest:wght@400;500;600&amp;display=swap">')
        page = f"<title>{e(META['title'])}</title>\n{fonts}\n{style}\n{body}\n{script}\n"
        Path(inline_out).write_text(page, encoding="utf-8")
        return

    style = f"<style>{FONT_FACES}{CSS}\n{image_css()}\n</style>"
    fonts = (
        '<link rel="preload" href="fonts/noto-serif-display.woff" as="font" type="font/woff" crossorigin>'
        '<link rel="preload" href="fonts/onest-cyrillic.woff2" as="font" type="font/woff2" crossorigin>'
    )

    site = META["siteUrl"].rstrip("/")
    # Версия в адресе картинки: Telegram кэширует превью, новая картинка получит новый адрес.
    og_ver = hashlib.sha1((IMG / "og.jpg").read_bytes()).hexdigest()[:8]
    og_img = f"{site}/img/og.jpg?v={og_ver}" if site else "img/og.jpg"

    def head(title, robots=""):
        return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>{robots}
<meta name="description" content="{e(META['description'])}">
<link rel="canonical" href="{site}/">
<link rel="icon" href="favicon.ico" sizes="32x32">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="theme-color" content="#F7F4EE" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#1A1B19" media="(prefers-color-scheme: dark)">
<meta property="og:type" content="website">
<meta property="og:locale" content="ru_RU">
<meta property="og:url" content="{site}/">
<meta property="og:title" content="{e(META['title'])}">
<meta property="og:description" content="{e(META['description'])}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(C['og']['alt'])}">
<meta name="twitter:card" content="summary_large_image">
{fonts}
{style}
</head>
<body>
<a class="skip" href="#trips">{e(C['skip'])}</a>"""

    (ROOT / "index.html").write_text(f"{head(META['title'])}\n{body}\n{script}\n</body>\n</html>\n", encoding="utf-8")
    build_404(site, fonts, style)


def build_404(site, fonts, style):
    """404.html для GitHub Pages: тот же вид, ссылки от адреса сайта, потому что страница открывается по любому пути."""
    N, handle = C["notFound"], META["telegram"]
    page = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<base href="{site}/">
<title>{e(N['title'])} · {e(META['title'])}</title>
<meta name="robots" content="noindex">
<link rel="icon" href="favicon.ico" sizes="32x32">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
{fonts}
{style}
</head>
<body>
<div class="masthead notfound">
  <div class="wrap top">
    {render_brand(link=True)}
    <nav aria-label="Разделы"><a href="https://t.me/{handle}" target="_blank" rel="noopener">@{handle}</a></nav>
  </div>
  <main class="wrap nf"><div class="hero">
    <p class="eyebrow">404</p>
    <h1>{e(N['title'])}</h1>
    <p class="lead">{e(N['text'])}</p>
    <div class="hero-cta"><a class="btn btn-primary" href="./">{e(N['cta'])}</a></div>
  </div></main>
</div>
</body>
</html>
"""
    (ROOT / "404.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--inline":
        build(sys.argv[2])
    else:
        build()
