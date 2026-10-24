#!/usr/bin/env python3
"""Собирает index.html витрины путешествий из content.json.

    python3 build.py                 -> index.html (картинки из папки img/)
    python3 build.py --inline OUT    -> одна страница с картинками внутри (для превью)

Места, цены и ранние тарифы меняются в content.json:
  seats   {"left": осталось, "total": всего или null, "of": "по ранней цене" или ""}
  tiers   ступени цены, state: sold (продано) / now (сейчас) / next (потом) / option (вариант)
  urgency надпись на фото, hot + hotOrder строка в блоке «Места заканчиваются»

WebP-версии фото, иконки и img/og.jpg готовит python3 images.py (нужен Pillow).
Если WebP для поездки ещё нет, страница возьмёт исходный img/<id>.jpg.
"""
import base64
import hashlib
import html
import json
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
IMG = ROOT / "img"
C = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
META, TOURS = C["meta"], C["tours"]

# Шрифты лежат в fonts/ (файлы Google Fonts, лицензия OFL рядом): без внешнего CSS, который задерживал первую отрисовку.
# Превью --inline берёт их с Google Fonts, потому что открывается без папки fonts/.
FONTS = ("https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500"
         "&family=Onest:wght@400;500;600&family=Unbounded:wght@500;600&display=swap")
FONT_FACES = """
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
@font-face{font-family:"Unbounded";font-style:normal;font-weight:500 600;font-display:swap;src:url(fonts/unbounded-cyrillic.woff2) format("woff2");unicode-range:U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116}
@font-face{font-family:"Unbounded";font-style:normal;font-weight:500 600;font-display:swap;src:url(fonts/unbounded-latin-ext.woff2) format("woff2");unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C4,U+2113,U+2C60-2C7F,U+A720-A7FF}
@font-face{font-family:"Unbounded";font-style:normal;font-weight:500 600;font-display:swap;src:url(fonts/unbounded-latin.woff2) format("woff2");unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}
"""
PRELOAD = ("unbounded-cyrillic", "onest-cyrillic", "onest-latin")

CSS = r"""
/* Сезонный указатель: заголовок и семь фото-корешков по месяцам, горящие места, затем по одной широкой главе на поездку. */
:root{
  --paper:#F0F3F2; --surface:#FFFFFF; --ink:#111A1C; --ink-soft:#4C5A5D; --line:#D2DAD9;
  --stamp:#1D3EC4; --on-stamp:#FFFFFF; --stamp-wash:rgba(29,62,196,.08);
  --on-photo:#FFFFFF; --scrim:rgba(6,10,12,.78); --chip-bg:rgba(255,255,255,.93); --chip-ink:#1D3EC4;
  --f-display:"Unbounded","Arial Black",system-ui,sans-serif;
  --f-body:"Onest","Segoe UI",system-ui,-apple-system,sans-serif;
  --f-mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  --gutter:max(clamp(16px,4vw,40px),env(safe-area-inset-left,0px),env(safe-area-inset-right,0px));
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
.wrap{max-width:1240px;margin-inline:auto;padding-inline:var(--gutter)}

/* шапка */
.top{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding-block:1.1rem}
.brand{font:500 .78rem/1.2 var(--f-mono);letter-spacing:.14em;text-transform:uppercase}
.brand b{font-weight:500;color:var(--ink-soft)}
.top a{font:500 .85rem/1 var(--f-mono);text-decoration:none;padding:.55rem .8rem;border:1px solid var(--line);border-radius:6px}
.top a:hover{border-color:var(--ink)}

/* первый экран */
.intro{display:grid;gap:clamp(1.75rem,4vw,2.5rem);padding-block:clamp(1.25rem,4vw,3rem) 0;
  grid-template-areas:"text" "spines" "hot"}
.hero{grid-area:text;display:grid;gap:1.1rem;align-content:start;min-width:0}
.eyebrow{margin:0;font:500 .78rem/1.3 var(--f-mono);letter-spacing:.14em;text-transform:uppercase;color:var(--stamp)}
.hero h1{margin:0;font:600 clamp(2rem,5.6vw,4.3rem)/1.05 var(--f-display);letter-spacing:-.02em;text-wrap:balance;max-width:17ch}
.lead{margin:0;max-width:58ch;font-size:clamp(1.02rem,1.6vw,1.2rem);color:var(--ink-soft)}
.hero-cta{display:flex;flex-wrap:wrap;align-items:center;gap:.75rem 1.25rem;padding-top:.25rem}
.hero-cta .btn{min-width:min(100%,15rem)}
.hero-cta span{font-size:.9rem;color:var(--ink-soft)}
/* на широком экране полосы стоят рядом с заголовком и целиком видны на первом экране */
@media (min-width:980px){
  .intro{grid-template-columns:minmax(0,1fr) minmax(0,1.2fr);grid-template-areas:"text spines" "hot hot";
    column-gap:clamp(2.5rem,4.5vw,4rem);row-gap:2.25rem;padding-top:clamp(1rem,2.2vw,2rem)}
  .hero h1{font-size:clamp(2.3rem,3.7vw,3.5rem)}
  .lead{font-size:1.08rem}
  .spines-nav{display:flex;flex-direction:column}
  .spines{flex:1 1 auto;height:auto;min-height:24rem}
}

/* горящие места */
.hot{grid-area:hot;min-width:0}
.hot h2{margin:0 0 .35rem;font:600 1.15rem/1.25 var(--f-display);letter-spacing:-.01em}
.hot>div>p{margin:0 0 .9rem;color:var(--ink-soft);font-size:.95rem}
.hot ul{list-style:none;margin:0;padding:0;border-top:1px solid var(--ink)}
.hot li{border-bottom:1px solid var(--line);break-inside:avoid}
.hot a{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:.1rem 1rem;align-items:baseline;padding:.65rem .1rem;text-decoration:none}
.hot a:hover .hot-name{color:var(--stamp)}
.hot-name{font:600 1rem/1.3 var(--f-body)}
.hot-name small{font:400 .78rem/1 var(--f-mono);color:var(--ink-soft);margin-left:.45rem;letter-spacing:.04em}
.hot-what{font:500 .8rem/1.3 var(--f-mono);color:var(--stamp);text-align:right}
@media (min-width:980px){
  .hot{display:grid;grid-template-columns:minmax(0,18.5rem) minmax(0,1fr);column-gap:clamp(2.5rem,4.5vw,4rem);align-items:start}
}
@media (min-width:1200px){.hot ul{columns:2;column-gap:2.5rem}}

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
/* на телефоне полосы становятся лентой карточек, которая листается пальцем */
@media (max-width:759px){
  .spines{height:auto;gap:10px;margin-inline:calc(var(--gutter)*-1);padding-inline:var(--gutter);overflow-x:auto;overscroll-behavior-x:contain;
    scroll-snap-type:x mandatory;scroll-padding-inline:var(--gutter);scrollbar-width:none}
  .spines::-webkit-scrollbar{display:none}
  .spine{flex:0 0 min(70vw,22rem);aspect-ratio:4/5;border-radius:6px;scroll-snap-align:start}
  .spine::after{background:linear-gradient(to top,rgba(6,10,12,.82) 0%,rgba(6,10,12,.3) 38%,rgba(6,10,12,0) 62%)}
  .spine-name{left:1rem;right:1rem;bottom:2.5rem;writing-mode:horizontal-tb;transform:none;font-size:1.45rem;white-space:normal}
  .spine-month{left:1rem;right:auto;bottom:1rem;text-align:left}
  .spine-seats{top:.75rem;left:auto;right:.75rem;transform:none;width:2rem;height:2rem;font-size:.9rem}
}

/* поездки */
.trips{display:grid;gap:clamp(3.5rem,8vw,6.5rem);padding-block:clamp(3rem,7vw,5.5rem)}
.trip{scroll-margin-top:1rem}
.trip-photo{position:relative;display:block;overflow:hidden;border-radius:6px;aspect-ratio:4/5;max-width:100%;color:var(--on-photo);text-decoration:none;background:#2a3133}
@media (min-width:600px){.trip-photo{aspect-ratio:3/2}}
@media (min-width:1000px){.trip-photo{aspect-ratio:21/9}}
.photo{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:var(--pos);transition:transform 1.4s cubic-bezier(.2,.7,.2,1)}
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
.top nav{display:flex;gap:.5rem;flex-shrink:0}
.top nav a{white-space:nowrap}
@media (max-width:520px){.brand b{display:none}}

/* почему с нами */
.why{padding-block:clamp(3rem,7vw,5rem) 0}
.why h2,.faq h2,.contact h2{margin:0 0 1.75rem;font:600 clamp(1.5rem,3.6vw,2.4rem)/1.1 var(--f-display);letter-spacing:-.015em;text-wrap:balance}
.why-grid{display:grid;gap:2rem clamp(1.5rem,3vw,2.75rem);grid-template-columns:repeat(auto-fit,minmax(min(100%,17rem),1fr))}
.why-item{display:grid;gap:.5rem;align-content:start;padding-top:1rem;border-top:2px solid var(--stamp);min-width:0}
.why-item h3{margin:0;font:600 1.12rem/1.3 var(--f-body)}
.why-item p{margin:0;color:var(--ink-soft);line-height:1.6}

/* частые сомнения */
.faq{padding-block:clamp(3.5rem,8vw,6rem);border-top:1px solid var(--line);display:grid;gap:1.5rem}
@media (min-width:980px){.faq{grid-template-columns:22rem minmax(0,1fr);gap:4.5rem}}
.faq-head h2{margin-bottom:.75rem}
.faq-head p{margin:0;color:var(--ink-soft);max-width:40ch}
.faq-list{border-top:1px solid var(--ink);min-width:0}
.faq details{border-bottom:1px solid var(--line)}
.faq summary{list-style:none;cursor:pointer;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:1rem;align-items:baseline;padding:1.05rem .1rem;font:600 1.08rem/1.35 var(--f-body)}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";font:500 1.3rem/1 var(--f-mono);color:var(--stamp);transition:transform .2s}
.faq details[open] summary::after{transform:rotate(45deg)}
.faq summary:hover{color:var(--stamp)}
.faq details p{margin:0;padding:0 2.5rem 1.2rem .1rem;max-width:64ch;color:var(--ink-soft);line-height:1.62}

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


def image_css(src):
    return "\n".join(f'.t-{t["id"]}{{--img:url("{src(variant(t["id"], 800))}");--pos:{t["pos"]}}}' for t in TOURS)


def render_photo(t, src, inline, first):
    # Первая глава грузится сразу, остальные по мере прокрутки.
    # На узком экране вертикальный кадр 800, тот же файл, что у карточки в ленте.
    i = t["id"]
    load = 'loading="eager"' if first else 'loading="lazy"'
    attrs = f'class="photo" alt="{e(t["alt"])}" {load} decoding="async"'
    small, big = variant(i, 800), variant(i, 1440)
    if inline:
        return f'<img src="{src(big)}" {attrs}>'
    sources = ""
    if small.endswith(".webp"):
        sources += f'<source media="(max-width:599px)" srcset="{src(small)}" type="image/webp">'
    if big.endswith(".webp"):
        sources += f'<source srcset="{src(big)}" type="image/webp">'
    return f'<picture>{sources}<img src="{src(i + ".jpg")}" {attrs}></picture>'


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


def render_why():
    w = C.get("why")
    if not w:
        return ""
    items = "".join(f'<div class="why-item"><h3>{e(x["t"])}</h3><p>{e(x["d"])}</p></div>' for x in w["items"])
    return f"""<section class="wrap why" id="why" aria-labelledby="why-title">
  <h2 id="why-title">{e(w["title"])}</h2>
  <div class="why-grid">{items}</div>
</section>"""


def render_faq():
    f = C.get("faq")
    if not f:
        return ""
    items = "".join(f'<details><summary>{e(x["q"])}</summary><p>{e(x["a"])}</p></details>' for x in f["items"])
    return f"""<section class="wrap faq" id="faq" aria-labelledby="faq-title">
  <div class="faq-head"><h2 id="faq-title">{e(f["title"])}</h2><p>{e(f["lead"])}</p></div>
  <div class="faq-list">{items}</div>
</section>"""


def render_about(src):
    a = C.get("about")
    if not a:
        return ""
    def photo(name, alt, w, h):
        return picture(src, name, f'alt="{e(alt)}" width="{w}" height="{h}" loading="lazy" decoding="async"')

    paras = "".join(f"<p>{e(p)}</p>" for p in a["paragraphs"])
    places = "".join(f"<li>{e(x)}</li>" for x in a["places"])
    past = "".join(
        f'<figure>{photo(x["img"], x["cap"], 600, 600)}'
        f'<figcaption>{e(x["cap"])}</figcaption></figure>' for x in a["past"])
    team = "".join(
        f'<article class="person">{photo(x["img"], x["name"], 480, 600)}'
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


def render_body(src, inline=False):
    H, HOT, CT = C["hero"], C["hot"], C["contact"]
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
    for n, t in enumerate(TOURS):
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
      {render_photo(t, src, inline, n == 0)}
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
    choose = e(tg(H["ctaMessage"]))
    return f"""
<div class="wrap top">
  <span class="brand">Авторские путешествия <b>· сезон 26/27</b></span>
  <nav aria-label="Разделы"><a href="#about">О нас</a><a href="https://t.me/{handle}" target="_blank" rel="noopener">@{handle}</a></nav>
</div>

<div class="wrap intro">
  <header class="hero">
    <p class="eyebrow">{e(H["eyebrow"])}</p>
    <h1>{lines(H["title"])}</h1>
    <p class="lead">{e(H["lead"])}</p>
    <div class="hero-cta">
      <a class="btn btn-primary" href="{choose}" target="_blank" rel="noopener">{e(H["cta"])}</a>
      <span>{e(H["ctaNote"])}</span>
    </div>
    <p class="trust"><a href="#why">Почему с нами</a> · <a href="#about">Кто мы</a> · <a href="#faq">Частые сомнения</a></p>
  </header>

  <nav class="spines-nav" aria-label="Все поездки сезона">
    <div class="spines">
{spines}
    </div>
    <p class="spines-note">{e(C["spinesNote"])}</p>
  </nav>

  <section class="hot" aria-labelledby="hot-title">
    <div>
      <h2 id="hot-title">{e(HOT["title"])}</h2>
      <p>{e(HOT["lead"])}</p>
    </div>
    <ul>
{hot_rows}
    </ul>
  </section>
</div>

{render_why()}

<main class="wrap trips">{''.join(trips)}
</main>

{render_about(src)}

{render_faq()}

<section class="contact" aria-labelledby="contact-title">
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
</section>

<footer class="wrap">
  <span>Андрей Баранов · авторские путешествия · 2026–2027. Места и цены на {e(META.get('updated', ''))}.</span>
  <span>Фото с Wikimedia Commons, кадрировано: {credits}. Остальные снимки из материалов поездок.</span>
</footer>
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
        style = f"<style>{CSS}\n{image_css(src)}\n</style>"
        fonts = (f'<link rel="preconnect" href="https://fonts.googleapis.com">'
                 f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
                 f'<link rel="stylesheet" href="{FONTS}">')
        page = f"<title>{e(META['title'])}</title>\n{fonts}\n{style}\n{body}\n{script}\n"
        Path(inline_out).write_text(page, encoding="utf-8")
        return

    style = f"<style>{FONT_FACES}{CSS}\n{image_css(src)}\n</style>"
    fonts = "".join(f'<link rel="preload" href="fonts/{f}.woff2" as="font" type="font/woff2" crossorigin>' for f in PRELOAD)

    site = META["siteUrl"].rstrip("/")
    # Версия в адресе картинки: Telegram кэширует превью, новая картинка получит новый адрес.
    og_ver = hashlib.sha1((IMG / "og.jpg").read_bytes()).hexdigest()[:8]
    og_img = f"{site}/img/og.jpg?v={og_ver}" if site else "img/og.jpg"
    head = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(META['title'])}</title>
<meta name="description" content="{e(META['description'])}">
<link rel="canonical" href="{site}/">
<link rel="icon" href="favicon.ico" sizes="32x32">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="theme-color" content="#F0F3F2" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0B1011" media="(prefers-color-scheme: dark)">
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
<body>"""
    (ROOT / "index.html").write_text(f"{head}\n{body}\n{script}\n</body>\n</html>\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--inline":
        build(sys.argv[2])
    else:
        build()
