#!/usr/bin/env python3
"""ساخت جزوهٔ کتاب‌مانند: برای هر درس یک PDF زیبا از روی فایل‌های Markdown.

اجرا (از ریشهٔ ریپازیتوری):
    python3 tools/build_book.py                 # همهٔ درس‌ها
    python3 tools/build_book.py گسسته معماری    # فقط درس‌هایی که نامشان شامل این کلمه‌هاست
    python3 tools/build_book.py --keep-html ...  # HTML میانی را هم نگه دار (برای اشکال‌یابی)

خروجی: پوشهٔ «جزوه-PDF/»؛ هر کتاب شامل جلد، راهنما، فهرست قابل کلیک با شمارهٔ صفحه،
شروع رنگی فصل‌ها، جعبه‌های مثال/تله/نکته/تمرین، کارت سؤال‌های آزمون، کارت خلاصه،
پاسخ‌نامهٔ آخر هر فصل، سرصفحه و شمارهٔ صفحه، و نشانک‌های PDF (bookmark).

قراردادهای Markdown (منبع در «جزوه/<درس>/فصل-*.md»):
  # فصل N: عنوان [★]          ← شروع فصل؛ بلافاصله بعدش یک > نقل‌قول معرفی (**برچسب:** متن)
  ## درس N: عنوان              ← درس
  ### تمرین ...                ← جعبهٔ تمرین؛ جواب‌ها در <details> بعدش (به پاسخ‌نامه منتقل می‌شود)
  **مثال:** / **قاعده:** / ⚠️  ← جعبهٔ مثال / نکته / تله
  ## 📝 آزمون فصل N (...)      ← آزمون؛ هر سؤال با **N. (ارشد YYYY، سؤال NN)** شروع می‌شود
  ## 🗂 کارت خلاصهٔ فصل N       ← کارت خلاصه

نیازها: pandoc، Node.js + Playwright (Chromium)، پایتون: beautifulsoup4، pypdf،
pdftotext (poppler). فونت‌ها در tools/.fonts (اگر نبود، از npm دانلود می‌شوند).
"""
from __future__ import annotations

import html
import pathlib
import urllib.parse
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from dataclasses import dataclass, field

from bs4 import BeautifulSoup, NavigableString, Tag
from PIL import Image
from pypdf import PdfReader, PdfWriter
import logging

logging.getLogger("pypdf").setLevel(logging.ERROR)

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "جزوه"
OUT = ROOT / "جزوه-PDF"
TOOLS = ROOT / "tools"
FONTS = TOOLS / ".fonts"
PRINT_JS = TOOLS / "print_pdf.js"

FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
LAT_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")


def fa(x) -> str:
    return str(x).translate(FA_DIGITS)


def lat(s: str) -> str:
    return s.translate(LAT_DIGITS)


# ---------------------------------------------------------------- درس‌ها
SUBJECTS = [
    dict(key="ریاضیات-گسسته", name="ریاضیات گسسته", no=1, color="#3949ab", glyph="∀x ∃y  n!"),
    dict(key="آمار-و-احتمال", name="آمار و احتمال مهندسی", no=2, color="#00897b", glyph="P(A | B)"),
    dict(key="جبر-خطی", name="جبر خطی", no=3, color="#6d4c41", glyph="Ax = λx"),
    dict(key="برنامه-سازی", name="مبانی کامپیوتر و برنامه‌سازی", no=4, color="#2e7d32",
         glyph="{ i++; }", code=True),
    dict(key="مدار-منطقی", name="مدار منطقی", no=5, color="#d84315", glyph="A ⊕ B"),
    dict(key="معماری-کامپیوتر", name="معماری کامپیوتر", no=6, color="#c62828", glyph="CPI · ALU"),
    dict(key="ساختمان-داده", name="داده‌ساختارها و الگوریتم‌ها", no=7, color="#1565c0",
         glyph="O(n log n)"),
    dict(key="نظریه-زبان-ها", name="نظریهٔ زبان‌ها و ماشین‌ها", no=8, color="#6a1b9a",
         glyph="δ(q, a)"),
    dict(key="سیستم-عامل", name="سیستم‌عامل", no=9, color="#00838f", glyph="fork()"),
    dict(key="هوش-مصنوعی", name="هوش مصنوعی", no=10, color="#ad1457", glyph="f = g + h"),
]


def _mix(c1: str, c2: str, t: float) -> str:
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def palette(c: str) -> dict:
    return dict(c=c, cd=_mix(c, "#000000", .32), cl=_mix(c, "#ffffff", .92),
                cl2=_mix(c, "#ffffff", .80), cm=_mix(c, "#ffffff", .45))


# ---------------------------------------------------------------- فونت‌ها
def ensure_fonts() -> dict:
    vaz = FONTS / "package" / "fonts" / "ttf"
    if not (vaz / "Vazirmatn-Regular.ttf").exists():
        FONTS.mkdir(parents=True, exist_ok=True)
        subprocess.run(["npm", "pack", "vazirmatn@33.0.3", "--silent"], cwd=FONTS, check=True)
        with tarfile.open(next(FONTS.glob("vazirmatn-*.tgz"))) as t:
            t.extractall(FONTS, filter="data")
    jb = FONTS / "fontsource-jetbrains-mono-5.3.0" / "package" / "files"
    if not (jb / "jetbrains-mono-latin-400-normal.woff2").exists():
        subprocess.run(["npm", "pack", "@fontsource/jetbrains-mono@5.3.0", "--silent"],
                       cwd=FONTS, check=True)
        d = FONTS / "fontsource-jetbrains-mono-5.3.0"
        d.mkdir(exist_ok=True)
        with tarfile.open(FONTS / "fontsource-jetbrains-mono-5.3.0.tgz") as t:
            t.extractall(d, filter="data")
    return dict(vaz=vaz, jb=jb)


def font_css(f: dict) -> str:
    v, jb = f["vaz"], f["jb"]
    weights = [(300, "Light"), (400, "Regular"), (500, "Medium"), (600, "SemiBold"),
               (700, "Bold"), (800, "ExtraBold"), (900, "Black")]
    css = "".join(
        f"@font-face{{font-family:Vazirmatn;src:url('{(v / f'Vazirmatn-{n}.ttf').as_uri()}');"
        f"font-weight:{w};}}" for w, n in weights)
    for w in (400, 700):
        css += (f"@font-face{{font-family:'JB Mono';src:url('{(jb / f'jetbrains-mono-latin-{w}-normal.woff2').as_uri()}');"
                f"font-weight:{w};}}")
    # حروف فارسی داخل کد/فرمول با وزیرمتن (تا به‌هم‌چسبیده و درست نمایش داده شوند)
    css += (f"@font-face{{font-family:CodeFA;src:url('{(v / 'Vazirmatn-Regular.ttf').as_uri()}');"
            "unicode-range:U+0600-06FF,U+200C-200F,U+FB50-FDFF,U+FE70-FEFF;}")
    return css


# ---------------------------------------------------------------- CSS
CSS = r"""
:root{--c:%(c)s;--cd:%(cd)s;--cl:%(cl)s;--cl2:%(cl2)s;--cm:%(cm)s;
 --ink:#1d2433;--muted:#6b7385;--line:#e2e6ee;--soft:#f6f8fb;}
@page{size:A4;margin:21mm 15mm 18mm 15mm;}
@page cover{margin:0;}
html{direction:rtl;}
body{margin:0;font-family:Vazirmatn,'Noto Color Emoji',sans-serif;font-size:10.8pt;line-height:1.95;
 color:var(--ink);-webkit-print-color-adjust:exact;print-color-adjust:exact;text-align:start;
 font-feature-settings:"ss01";}
p{margin:1.6mm 0;}
strong{font-weight:800;color:#141a29;}
a{color:var(--c);text-decoration:none;}
.pm{position:absolute;top:0;right:0;font-size:1.5px;line-height:1;color:#fff;direction:ltr;
 unicode-bidi:isolate;white-space:nowrap;}
.ico{font-family:'Noto Color Emoji',Vazirmatn;font-weight:400;}

/* ---------- فرمول و کد ---------- */
code{font-family:'FreeSerif','DejaVu Serif',CodeFA,serif;font-size:1.07em;direction:ltr;
 unicode-bidi:isolate;background:var(--cl);color:#18203a;padding:0 1.1mm;border-radius:1.2mm;
 line-height:1.6;}
code.rtl{direction:rtl;}
code .ltr{direction:ltr;unicode-bidi:isolate;}
body.code code{font-family:'JB Mono','DejaVu Sans Mono',CodeFA,monospace;font-size:.86em;
 background:#eef1f6;}
pre{direction:ltr;text-align:left;background:#f7f8fb;border:1px solid var(--line);
 border-left:3.5px solid var(--c);border-radius:2.5mm;padding:2.6mm 4mm;margin:2.5mm 0;
 font-family:'JB Mono','DejaVu Sans Mono',CodeFA,monospace;font-size:8.9pt;line-height:1.62;
 white-space:pre-wrap;break-inside:avoid;}
pre code,body.code pre code{background:none;padding:0;font:inherit;color:#1e2537;}
div.sourceCode{margin:0;}
code span.kw,code span.cf{color:#7c3aed;font-weight:700;}
code span.dt{color:#0e7490;font-weight:700;}
code span.dv,code span.fl,code span.bn{color:#c2410c;}
code span.st,code span.ch,code span.sc{color:#15803d;}
code span.co{color:#8a94a6;font-style:italic;}
code span.fu{color:#1d4ed8;}
code span.pp,code span.im{color:#b45309;}
code span.op{color:#475569;}

/* ---------- جدول ---------- */
table{border-collapse:collapse;width:100%%;margin:3mm 0;font-size:9.6pt;line-height:1.75;}
thead{display:table-header-group;}
th{background:var(--c);color:#fff;font-weight:700;padding:1.5mm 2.4mm;text-align:right;
 border:1px solid var(--c);}
td{padding:1.3mm 2.4mm;border:1px solid var(--line);vertical-align:top;}
tbody tr:nth-child(even) td{background:#f8f9fc;}
tr{break-inside:avoid;}
th code{background:rgba(255,255,255,.18);color:#fff;}

ul,ol{margin:1.5mm 0;padding-right:6.5mm;}
li{margin:.8mm 0;}
ol{list-style-type:persian;}
li::marker{color:var(--c);font-weight:800;}
img{max-width:100%%;}
p > img:only-child{display:block;margin:2mm auto;}
hr{display:none;}

/* ---------- جلد ---------- */
.cover{page:cover;position:relative;width:210mm;height:296.5mm;overflow:hidden;break-after:page;}
.cv-band{position:absolute;top:0;right:0;left:0;height:178mm;
 background:linear-gradient(155deg,var(--c) 0%%,var(--cd) 100%%);}
.cv-band::before{content:'';position:absolute;inset:0;
 background-image:radial-gradient(rgba(255,255,255,.14) 1.1px,transparent 1.5px);background-size:6mm 6mm;}
.cv-o1{position:absolute;width:160mm;height:160mm;border-radius:50%%;left:-62mm;top:-58mm;
 background:rgba(255,255,255,.07);}
.cv-o2{position:absolute;width:96mm;height:96mm;border-radius:50%%;right:-30mm;top:104mm;
 background:rgba(255,255,255,.06);}
.cv-glyph{position:absolute;left:18mm;top:112mm;font-family:'FreeSerif','DejaVu Serif',serif;
 font-size:54pt;color:rgba(255,255,255,.26);direction:ltr;white-space:nowrap;}
.cv-text{position:absolute;top:30mm;right:20mm;left:20mm;color:#fff;}
.cv-kicker{display:inline-block;font-size:10.5pt;background:rgba(255,255,255,.15);
 border:1px solid rgba(255,255,255,.32);padding:.8mm 4.5mm;border-radius:20mm;}
.cv-no{font-size:11pt;opacity:.85;margin-top:12mm;font-weight:500;}
.cv-title{font-size:38pt;font-weight:900;line-height:1.35;margin:2mm 0 5mm;}
.cv-sub{font-size:12.5pt;line-height:1.95;opacity:.95;max-width:148mm;font-weight:400;}
.cv-stats{position:absolute;top:164mm;right:20mm;left:20mm;display:flex;gap:5mm;}
.cv-stat{flex:1;background:#fff;border-radius:4mm;padding:4.5mm 3mm 3.5mm;text-align:center;
 box-shadow:0 1.6mm 5mm rgba(16,24,40,.16);}
.cv-stat b{display:block;font-size:23pt;font-weight:900;color:var(--c);line-height:1.25;}
.cv-stat span{font-size:9.5pt;color:var(--muted);}
.cv-list-t{position:absolute;top:197mm;right:20mm;font-weight:800;color:var(--cd);font-size:11pt;}
.cv-chapters{position:absolute;top:206mm;right:20mm;left:20mm;columns:2;column-gap:10mm;
 font-size:9.8pt;line-height:1.7;}
.cv-chapters div{break-inside:avoid;padding:1.2mm 0;border-bottom:1px dashed var(--line);}
.cv-chapters i{font-style:normal;display:inline-block;min-width:6mm;color:var(--c);font-weight:900;}
.cv-foot{position:absolute;bottom:11mm;right:20mm;left:20mm;display:flex;justify-content:space-between;
 font-size:8.8pt;color:var(--muted);border-top:1px solid var(--line);padding-top:2.5mm;}

/* ---------- راهنما و فهرست ---------- */
.front{break-after:page;position:relative;}
.pt{font-size:19pt;font-weight:900;color:var(--cd);margin:0 0 1mm;line-height:1.5;}
.pt-sub{color:var(--muted);margin:0 0 5mm;font-size:10pt;}
.legend{display:grid;grid-template-columns:repeat(3,1fr);gap:3mm;margin:2mm 0 6mm;}
.lg{border-radius:3mm;padding:2.6mm 3.5mm;font-size:9.4pt;line-height:1.8;border-right:3.5px solid;}
.lg b{display:block;font-size:10.4pt;}
.lg.l-ex{background:#eef4ff;border-color:#3b82f6;} .lg.l-ex b{color:#1d4ed8;}
.lg.l-trap{background:#fff4e5;border-color:#f08c00;} .lg.l-trap b{color:#b35c00;}
.lg.l-tip{background:#ecfdf3;border-color:#16a34a;} .lg.l-tip b{color:#15803d;}
.lg.l-exr{background:var(--cl);border-color:var(--c);} .lg.l-exr b{color:var(--cd);}
.lg.l-exam{background:#f1f3f9;border-color:var(--cd);} .lg.l-exam b{color:var(--cd);}
.lg.l-sum{background:#fffbea;border-color:#e0b400;} .lg.l-sum b{color:#8a6d00;}
.h-sec{font-size:12.5pt;font-weight:800;color:var(--cd);margin:5mm 0 2.5mm;display:flex;
 align-items:center;gap:2mm;}
.h-sec::before{content:'';width:3mm;height:3mm;border-radius:.8mm;background:var(--c);}
.cycle{display:grid;grid-template-columns:repeat(5,1fr);gap:2.5mm;margin:1mm 0 5mm;}
.step{background:var(--soft);border:1px solid var(--line);border-radius:3mm;padding:2.5mm 2.5mm 2mm;
 text-align:center;font-size:9pt;line-height:1.7;}
.step .n{display:inline-flex;width:6mm;height:6mm;border-radius:50%%;background:var(--c);color:#fff;
 align-items:center;justify-content:center;font-weight:800;font-size:9pt;}
.step b{display:block;color:var(--cd);font-size:10pt;margin-top:1mm;}
.step .m{display:block;color:var(--c);font-weight:900;font-size:13pt;line-height:1.3;}
.golden{background:#fffbea;border:1px solid #f1d675;border-radius:3mm;padding:3mm 4.5mm;
 font-size:10pt;margin:3mm 0;}
.golden b{color:#8a6d00;}
.srcnote{background:var(--soft);border-radius:3mm;padding:2.5mm 4.5mm;font-size:9.3pt;
 color:#3b4252;margin:3mm 0;}

.toc-ch{display:flex;align-items:center;gap:3mm;margin-top:3.2mm;padding:1.4mm 0;
 border-bottom:1.5px solid var(--cl2);break-inside:avoid;break-after:avoid;}
.toc-num{flex:none;width:8.5mm;height:8.5mm;border-radius:50%%;background:var(--c);color:#fff;
 font-weight:900;display:flex;align-items:center;justify-content:center;font-size:11pt;}
.toc-t{font-weight:800;font-size:11.3pt;color:#141a29;}
.toc-chip{font-size:8.3pt;color:var(--cd);background:var(--cl);border-radius:10mm;
 padding:0 2.5mm;white-space:nowrap;}
.toc-fill{flex:1;border-bottom:1.6px dotted #c7ccd8;transform:translateY(-1.3mm);min-width:5mm;}
.pg{font-weight:800;color:var(--c);}
.toc-ch > .pg,.toc-row > .pg{display:inline-block;min-width:8mm;text-align:left;}
.toc-row{display:flex;align-items:center;gap:2mm;padding-right:11.5mm;font-size:9.8pt;
 line-height:1.85;color:#2f3646;break-inside:avoid;}
.toc-row .k{color:var(--c);font-weight:800;min-width:11mm;}
.toc-row.ext{color:var(--muted);font-size:9.3pt;}
.toc-row a,.toc-ch a{color:inherit;}

/* ---------- شروع فصل ---------- */
.chapter{break-before:page;}
.ch-head{position:relative;overflow:hidden;background:linear-gradient(150deg,var(--c),var(--cd));
 color:#fff;border-radius:4mm;padding:6mm 8mm 5mm;margin:0 0 4mm;}
.ch-head::before{content:'';position:absolute;inset:0;
 background-image:radial-gradient(rgba(255,255,255,.12) 1px,transparent 1.4px);background-size:5mm 5mm;}
.ch-no{position:absolute;left:8mm;top:50%%;transform:translateY(-50%%);width:23mm;height:23mm;
 border-radius:50%%;background:rgba(255,255,255,.12);border:1.5px solid rgba(255,255,255,.38);
 display:flex;align-items:center;justify-content:center;font-size:30pt;font-weight:900;color:#fff;
 line-height:1;}
.ch-head{padding-left:36mm !important;}
.ch-kicker{position:relative;font-size:10pt;font-weight:500;opacity:.9;}
.ch-title{position:relative;font-size:21pt;font-weight:900;margin:.5mm 0 2.5mm;line-height:1.5;color:#fff;}
.ch-badges{position:relative;display:flex;flex-wrap:wrap;gap:2mm;}
.ch-badges > span{background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.25);
 border-radius:10mm;padding:0 3mm;font-size:8.8pt;line-height:1.9;}
.ch-badges > span.star{background:#ffd54f;color:#4a3800;border-color:#ffd54f;font-weight:800;}
.ch-info{background:var(--cl);border-radius:3mm;padding:2mm 5mm;margin:0 0 4mm;font-size:10pt;}
.ch-info .row{display:flex;gap:2.5mm;padding:1.1mm 0;border-bottom:1px dashed var(--cl2);}
.ch-info .row:last-child{border-bottom:0;}
.ch-info .lbl{flex:none;font-weight:800;color:var(--cd);white-space:nowrap;}
.ch-map{display:flex;flex-wrap:wrap;gap:1.8mm;margin:0 0 5mm;font-size:9.2pt;align-items:center;}
.ch-map b{color:var(--muted);font-weight:700;margin-left:1mm;}
.ch-map a{display:inline-flex;align-items:center;gap:1.4mm;border:1px solid var(--cl2);border-radius:10mm;
 padding:0 2.8mm;color:var(--cd);line-height:1.85;background:#fff;}
.ch-map a i{font-style:normal;color:var(--c);font-weight:900;}

/* ---------- درس ---------- */
.lesson{position:relative;display:flex;align-items:center;gap:3mm;margin:7mm 0 3mm;
 padding-bottom:1.8mm;border-bottom:2px solid var(--cl2);break-after:avoid;}
.lesson .no{flex:none;background:var(--c);color:#fff;border-radius:2.2mm;padding:0 3mm;
 font-size:9.3pt;font-weight:800;line-height:2;}
.lesson h2{margin:0;font-size:15pt;font-weight:900;color:var(--cd);line-height:1.5;}
h3.sub{font-size:11.8pt;font-weight:800;color:var(--cd);margin:5mm 0 1.8mm;padding-right:2.8mm;
 border-right:3px solid var(--c);line-height:1.6;break-after:avoid;}
p > strong:first-child{color:var(--cd);}

/* ---------- جعبه‌ها ---------- */
.box{border-radius:3mm;padding:2.4mm 4.5mm 2mm;margin:3.5mm 0;border-right:4px solid;break-inside:avoid;}
.box .tag{display:flex;align-items:center;gap:1.6mm;font-weight:800;font-size:9.8pt;margin-bottom:.6mm;}
.box .bx > :first-child{margin-top:0;} .box .bx > :last-child{margin-bottom:0;}
.box.ex{background:#eef4ff;border-color:#3b82f6;} .box.ex .tag{color:#1d4ed8;}
.box.trap{background:#fff4e5;border-color:#f08c00;} .box.trap .tag{color:#b35c00;}
.box.tip{background:#ecfdf3;border-color:#16a34a;} .box.tip .tag{color:#15803d;}
.box.note{background:var(--soft);border-color:#94a3b8;} .box.note .tag{color:#475569;}
.box pre{background:#fff;}

.exercise{border:1.5px solid var(--cl2);border-radius:3.5mm;margin:5mm 0;break-inside:avoid;
 background:#fff;overflow:hidden;}
.ex-head{display:flex;align-items:center;gap:2mm;background:var(--cl);color:var(--cd);
 font-weight:900;padding:1.3mm 4.5mm;font-size:10.6pt;}
.ex-head .hint{margin-right:auto;font-weight:500;font-size:8.6pt;color:var(--muted);}
.ex-body{padding:2mm 4.5mm 1mm;}
.ex-body > :first-child{margin-top:0;}
.keyref{position:relative;display:flex;align-items:center;gap:1.6mm;border-top:1px dashed var(--cl2);
 padding:1mm 4.5mm 1.2mm;font-size:8.8pt;color:var(--muted);}
.keyref a{font-weight:800;}

/* ---------- آزمون ---------- */
.exam{break-before:page;}
.exam-head{position:relative;overflow:hidden;background:linear-gradient(150deg,var(--cd),#151b2d);
 color:#fff;border-radius:4mm;padding:5mm 7mm 4.5mm;margin:0 0 3mm;}
.exam-head::before{content:'';position:absolute;inset:0;
 background-image:radial-gradient(rgba(255,255,255,.10) 1px,transparent 1.4px);background-size:5mm 5mm;}
.exam-kicker{position:relative;font-size:10pt;opacity:.85;}
.exam-title{position:relative;font-size:18pt;font-weight:900;line-height:1.5;margin:0 0 2mm;color:#fff;}
.exam-chips{position:relative;display:flex;flex-wrap:wrap;gap:2mm;}
.exam-chips > span{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.22);
 border-radius:10mm;padding:0 3mm;font-size:8.8pt;line-height:1.9;}
.exam-chips a,.exam-chips .pg{color:#fff;font-weight:800;}
.exam-note{font-size:9.4pt;color:#3b4252;background:var(--soft);border-radius:2.5mm;
 padding:1.8mm 4mm;margin:0 0 3mm;}
.exam-note p{margin:.6mm 0;}
.q{border:1px solid var(--line);border-radius:3.2mm;padding:2.2mm 4mm 1.6mm;margin:0 0 3.2mm;
 break-inside:avoid;background:#fff;}
.q-head{display:flex;align-items:center;gap:2.2mm;margin-bottom:1mm;}
.q-no{flex:none;width:7mm;height:7mm;border-radius:50%%;background:var(--c);color:#fff;
 font-weight:900;font-size:9.5pt;display:flex;align-items:center;justify-content:center;}
.q-src{font-size:8.7pt;color:var(--cd);background:var(--cl);border-radius:10mm;padding:0 2.8mm;
 line-height:1.9;font-weight:600;}
.q-mark{margin-right:auto;display:flex;align-items:center;gap:1.2mm;font-size:7.8pt;color:#9aa2b3;}
.q-mark i{display:inline-block;width:3.8mm;height:3.8mm;border:1.3px solid #aab2c3;border-radius:.9mm;}
.q-body > :first-child{margin-top:0;}
.q-body p{margin:1.2mm 0;}
.q-img img{display:block;max-width:100%%;margin:.5mm 0 0 auto;}
.q-img{margin:0;}
.opts{display:grid;gap:1.2mm 5mm;margin:1.8mm 0 .8mm;}
.opts.c4{grid-template-columns:repeat(4,1fr);} .opts.c2{grid-template-columns:1fr 1fr;}
.opts.c1{grid-template-columns:1fr;}
.opt{display:flex;gap:1.8mm;align-items:baseline;line-height:1.75;}
.opt .on{flex:none;display:inline-flex;width:5mm;height:5mm;border:1.2px solid var(--c);color:var(--c);
 border-radius:50%%;font-size:8pt;font-weight:900;align-items:center;justify-content:center;
 transform:translateY(.6mm);}
ol.opts-list{list-style:none;padding:0;margin:1.5mm 0 .5mm;counter-reset:o;}
ol.opts-list > li{counter-increment:o;display:flex;gap:1.8mm;align-items:baseline;margin:.6mm 0;}
ol.opts-list > li::before{content:counter(o,persian);flex:none;display:inline-flex;width:5mm;height:5mm;
 border:1.2px solid var(--c);color:var(--c);border-radius:50%%;font-size:8pt;font-weight:900;
 align-items:center;justify-content:center;transform:translateY(.6mm);}

/* ---------- کارت خلاصه ---------- */
.summary{position:relative;margin:6mm 0 2mm;border:2px dashed var(--cm);border-radius:4mm;
 padding:4mm 5mm 2.5mm;background:linear-gradient(180deg,#fffbea 0,#fff 24mm);break-inside:avoid;}
.sum-cut{position:absolute;top:-3.6mm;left:9mm;background:#fff;padding:0 1.5mm;color:var(--c);
 font-size:12pt;line-height:1;}
.sum-head{display:flex;align-items:center;gap:2mm;font-weight:900;color:var(--cd);font-size:13pt;
 margin:0 0 1.5mm;}
.sum-head small{font-weight:500;font-size:8.8pt;color:var(--muted);margin-right:auto;}
.summary ul{list-style:none;padding:0;margin:0;}
.summary li{position:relative;padding-right:6mm;margin:1.2mm 0;line-height:1.85;}
.summary li::before{content:'✔';position:absolute;right:0;top:0;color:var(--c);font-weight:900;
 font-family:'DejaVu Sans',sans-serif;}

/* ---------- پاسخ‌نامه ---------- */
.key{break-before:page;}
.key-head{position:relative;display:flex;align-items:center;gap:3mm;background:var(--cl);
 border-radius:4mm;padding:3.5mm 6mm;margin:0 0 4mm;}
.key-head .kico{font-size:20pt;}
.key-head h2{margin:0;font-size:16pt;font-weight:900;color:var(--cd);line-height:1.5;}
.key-head small{display:block;font-size:9pt;color:var(--muted);font-weight:500;}
.key-sec{position:relative;margin:0 0 5mm;}
.key-sec h3{font-size:11.5pt;font-weight:900;color:var(--cd);margin:0 0 1.5mm;padding:0 0 1mm;
 border-bottom:1.5px solid var(--cl2);display:flex;align-items:center;gap:2mm;break-after:avoid;}
.key-sec h3 .back{margin-right:auto;font-size:8.5pt;font-weight:600;color:var(--muted);}
.keygrid{display:flex;flex-wrap:wrap;gap:1.8mm;margin:2mm 0 3.5mm;}
.kc{width:13.5mm;border:1px solid var(--line);border-radius:2.2mm;text-align:center;padding:.8mm 0 1.4mm;
 background:#fff;break-inside:avoid;}
.kc .kq{display:block;font-size:7.8pt;color:var(--muted);line-height:1.7;}
.kc .ka{display:inline-flex;min-width:6mm;height:6mm;padding:0 1mm;border-radius:3mm;background:var(--c);
 color:#fff;font-weight:900;font-size:9pt;align-items:center;justify-content:center;white-space:nowrap;}
.kc.multi{width:auto;padding-left:1.5mm;padding-right:1.5mm;}
.sol{display:flex;gap:3mm;padding:1.8mm 0;border-bottom:1px dashed var(--line);break-inside:avoid;}
.sol:last-child{border-bottom:0;}
.sol .sn{flex:none;width:6.5mm;height:6.5mm;border-radius:50%%;background:var(--cl);color:var(--cd);
 font-weight:900;font-size:9pt;display:flex;align-items:center;justify-content:center;margin-top:.8mm;}
.sol .sb{flex:1;min-width:0;}
.sol .sb > :first-child{margin-top:0;}
.sol .ans{display:inline-block;background:var(--c);color:#fff;border-radius:10mm;padding:0 2.6mm;
 font-size:8.8pt;font-weight:800;margin-left:1.5mm;line-height:1.85;}
.key-sec ol{margin-top:0;}
"""


# ---------------------------------------------------------------- ابزار HTML
def pandoc(md: str) -> str:
    return subprocess.run(["pandoc", "-f", "gfm", "-t", "html5", "--wrap=none"],
                          input=md, capture_output=True, text=True, check=True).stdout


def tx(el) -> str:
    return el.get_text(" ", strip=True) if isinstance(el, Tag) else str(el).strip()


def inner(el: Tag) -> str:
    return el.decode_contents()


def lead_strong(el: Tag):
    """اگر پاراگراف با <strong> شروع شود، همان را برگردان."""
    if not isinstance(el, Tag) or el.name != "p":
        return None
    for c in el.contents:
        if isinstance(c, NavigableString):
            if c.strip():
                return None
            continue
        return c if c.name == "strong" else None
    return None


def is_code(el: Tag) -> bool:
    return el.name == "pre" or (el.name == "div" and "sourceCode" in (el.get("class") or []))


def starts_warn(el: Tag) -> bool:
    return tx(el).startswith("⚠")


TIP_WORDS = ("قاعده", "نکته", "روش", "میان‌بُر", "ترفند", "حفظی", "نتیجه", "شهود", "قالب حل",
             "ایدهٔ کلی", "آزمون سریع", "تیپ", "منطق شمارش", "ریشهٔ")


def label_kind(label: str):
    if "مثال" in label:
        return "ex", "✏️"
    if "تله" in label:
        return "trap", "⚠️"
    if any(w in label for w in TIP_WORDS):
        return "tip", "💡"
    return None


def para_label(el: Tag):
    s = lead_strong(el)
    if s is None:
        return None
    lab = s.get_text().strip()
    if not re.search(r"[:؟]\s*$", lab) and lab not in ("نکته‌ها", "روش"):
        return None
    return lab.rstrip(":").strip()


FA_LET = "\u0621-\u064A\u0671-\u06D3\u06FA-\u06FF\u200c\u060C\u061B"
FA_LETTER = re.compile(f"[{FA_LET}]")
NON_FA = re.compile(f"[^{FA_LET}]+")
STRONG = re.compile(r"[A-Za-z0-9\u0370-\u03FF\u2070-\u209F\u00B2\u00B3\u00B9\u2032\u221E\u221A\u2211\u220F\u0394\u03A3]")
PAIRS = {")": "(", "]": "[", "}": "{", "\u2309": "\u2308", "\u230B": "\u230A"}
OPEN = set(PAIRS.values())


def _balance(seg: str, a: int, b: int):
    """هستهٔ seg[a:b] را آن‌قدر گسترش بده که پرانتزهایش جفت شوند."""
    while True:
        stack, bad_l, bad_r = [], False, []
        for ch in seg[a:b]:
            if ch in OPEN:
                stack.append(ch)
            elif ch in PAIRS:
                if stack and stack[-1] == PAIRS[ch]:
                    stack.pop()
                else:
                    bad_l = True
        changed = False
        if bad_l and a > 0:
            a -= 1
            changed = True
        if stack and b < len(seg):
            b += 1
            changed = True
        if not changed:
            return a, b


def rtl_formula(text: str) -> str:
    """فرمولی که کلمهٔ فارسی دارد: راست‌به‌چپ، و هر زیرعبارت لاتین/عددی یک واحد چپ‌به‌راست."""
    out, pos = [], 0
    for m in NON_FA.finditer(text):
        out.append(html.escape(text[pos:m.start()]))
        seg = m.group(0)
        strong = [k for k, ch in enumerate(seg) if STRONG.match(ch)]
        if not strong:
            out.append(html.escape(seg))
        else:
            a, b = _balance(seg, strong[0], strong[-1] + 1)
            out.append(html.escape(seg[:a]) + '<span class="ltr">' + html.escape(seg[a:b]) + "</span>"
                       + html.escape(seg[b:]))
        pos = m.end()
    out.append(html.escape(text[pos:]))
    return "".join(out)


def fix_inline_formulas(soup) -> None:
    for c in soup.find_all("code"):
        if c.find_parent("pre") is not None:
            continue
        t = c.get_text()
        if FA_LETTER.search(t) and STRONG.search(t):
            c["class"] = (c.get("class") or []) + ["rtl"]
            c.clear()
            c.append(BeautifulSoup(rtl_formula(t), "html.parser"))


def mk(i: str) -> str:
    return f'<span class="pm">@@{i}@@</span>'


def box(kind: str, ico: str, label: str, body: str) -> str:
    return (f'<div class="box {kind}"><div class="tag"><span class="ico">{ico}</span>'
            f'<span>{label}</span></div><div class="bx">{body}</div></div>')


# ---------------------------------------------------------------- مدل داده
@dataclass
class Chapter:
    no: int
    title: str
    star: bool = False
    lessons: list = field(default_factory=list)      # (id, no_fa, title)
    exam_id: str = ""
    exam_count: int = 0
    exam_authored: bool = False
    summary_id: str = ""
    key_id: str = ""
    key_entries: list = field(default_factory=list)  # (id, title)
    html: str = ""


INTRO_ICONS = [("سهم", "🎯"), ("زمان", "⏱️"), ("پیش‌نیاز", "🧩"), ("اعتبار", "✅"), ("چرا", "💡"),
               ("فرض", "📐"), ("سؤال‌های آزمون", "🖼️"), ("هدف", "🎯")]


def intro_rows(bq: Tag):
    rows = []
    paras = bq.find_all("p", recursive=False) or [bq]
    for p in paras:
        cur = None
        for node in list(p.contents):
            if isinstance(node, Tag) and node.name == "strong" and re.search(r"[:؟]\s*$", node.get_text()):
                cur = [node.get_text().strip().rstrip(":").strip(), []]
                rows.append(cur)
                continue
            if cur is None:
                cur = ["", []]
                rows.append(cur)
            cur[1].append(str(node))
    out = []
    for lab, parts in rows:
        body = "".join(parts).strip().lstrip("،:").strip()
        if not body and not lab:
            continue
        ico = next((i for k, i in INTRO_ICONS if k in lab), "📌")
        out.append((ico, lab, body))
    return out


Q_START = re.compile(r"^\s*([۰-۹0-9]+)\.\s*(?:\((.+)\))?\s*$")
OPT_SPLIT = re.compile(r"(?:^|(?<=\s))([۱۲۳۴])\)\s")


def split_options(p):
    """«[متن] ۱) … ۲) … ۳) … ۴) …» → (متن پیش از گزینه‌ها، چهار گزینه) یا None."""
    h = (inner(p) if isinstance(p, Tag) else str(p)).strip()
    parts = OPT_SPLIT.split(h)
    if len(parts) != 9:
        return None
    labels, bodies = parts[1::2], [b.strip() for b in parts[2::2]]
    if labels != ["۱", "۲", "۳", "۴"]:
        return None
    return parts[0].strip(), bodies


def opts_html(bodies) -> str:
    plain = [BeautifulSoup(b, "html.parser").get_text() for b in bodies]
    longest = max(len(s) for s in plain)
    cls = "c4" if longest <= 16 else ("c2" if longest <= 40 else "c1")
    items = "".join(f'<div class="opt"><span class="on">{fa(i + 1)}</span><span>{b}</span></div>'
                    for i, b in enumerate(bodies))
    return f'<div class="opts {cls}">{items}</div>'


# ---------------------------------------------------------------- ساخت یک فصل
FULL_W, MAX_H, CROP_DPI = 171.0, 225.0, 200


def size_image(img: Tag) -> None:
    """اندازهٔ چاپی تصویر از روی اندازهٔ برش اصلی (۲۰۰ dpi): تصویرهای تمام‌عرض = عرض کارت،
    و ارتفاع هیچ تصویری از یک صفحه بیشتر نشود (تصویر شکسته نمی‌شود)."""
    src = img.get("src", "")
    if not src.startswith("file:"):
        return
    path = pathlib.Path(urllib.parse.unquote(urllib.parse.urlparse(src).path))
    try:
        w, h = Image.open(path).size
    except OSError:
        return
    width = FULL_W if w >= 1000 else w * 25.4 / CROP_DPI
    if width * h / w > MAX_H:
        width = MAX_H * w / h
    img["style"] = f"width:{min(width, FULL_W):.1f}mm"


def build_chapter(md_path: pathlib.Path) -> Chapter:
    md = md_path.read_text(encoding="utf-8")
    md = re.sub(r"\s*فایل اجرایی: \[`[^`]+`\]\([^)]+\)", "", md)
    soup = BeautifulSoup(pandoc(md), "html.parser")
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not re.match(r"^(https?:|file:|data:)", src):
            img["src"] = (md_path.parent / html.unescape(src)).resolve().as_uri()
        size_image(img)
    for a in soup.select("pre a[aria-hidden]"):
        a.decompose()
    fix_inline_formulas(soup)
    blocks = [c for c in soup.contents if isinstance(c, Tag)]

    h1 = next(b for b in blocks if b.name == "h1")
    h1t = tx(h1)
    no = int(lat(re.search(r"فصل\s*([۰-۹0-9]+)", h1t).group(1)))
    title = re.sub(r"^\s*فصل\s*[۰-۹0-9]+\s*[:：]\s*", "", h1t).replace("★", "").strip()
    ch = Chapter(no=no, title=title, star="★" in h1t)
    cid = f"c{no}"
    ch.key_id = f"{cid}k"

    parts: list[str] = []
    keyparts: list[str] = []
    intro = []
    lesson_k = 0
    ctx_title = ""

    def add_key(det: Tag, title: str, kind: str) -> str:
        kid = f"{cid}k{len(ch.key_entries) + 1}"
        back_id = f"{cid}x" if kind == "exam" else f"{kid}b"
        ch.key_entries.append((kid, title))
        summ = det.find("summary")
        sub = ""
        if summ is not None:
            st = summ.get_text(" ", strip=True)
            m = re.search(r"\((.+)\)", st)
            if m and "سنجش" in m.group(1):
                sub = m.group(1)
            summ.decompose()
        body = key_body(det, kind)
        back = (f'<span class="back">برگشت ← <a href="#{back_id}">صفحهٔ '
                f'<span class="pg" data-for="{back_id}">۰۰۰</span></a></span>')
        subh = f'<small style="font-weight:600;color:var(--muted)">{sub}</small>' if sub else ""
        keyparts.append(f'<div class="key-sec" id="{kid}">{mk(kid)}<h3>{title} {subh}{back}</h3>{body}</div>')
        return kid

    def keyref(kid: str) -> str:
        return (f'<div class="keyref" id="{kid}b">{mk(kid + "b")}<span class="ico">🔑</span>'
                f'<span>پاسخ‌ها در پاسخ‌نامهٔ آخر فصل:</span>'
                f'<a href="#{kid}">صفحهٔ <span class="pg" data-for="{kid}">۰۰۰</span></a></div>')

    def absorb(j: int, prev_code: bool, lead_empty: bool):
        got = []
        while j < len(blocks):
            b = blocks[j]
            if b.name in ("ul", "ol"):
                got.append(b); j += 1; prev_code = False; lead_empty = False; continue
            if is_code(b):
                got.append(b); j += 1; prev_code = True; continue
            if (b.name == "p" and (prev_code or lead_empty) and not starts_warn(b)
                    and para_label(b) is None and lead_strong(b) is None and len(tx(b)) < 320
                    and not b.find("img")):
                got.append(b); j += 1; prev_code = False; lead_empty = False; continue
            break
        return got, j

    i = 0
    while i < len(blocks):
        b = blocks[i]
        name, t = b.name, tx(b)

        if name == "h1":
            if i + 1 < len(blocks) and blocks[i + 1].name == "blockquote":
                intro = intro_rows(blocks[i + 1])
                i += 2
            else:
                i += 1
            continue
        if name == "hr":
            i += 1
            continue

        if name == "h2" and "آزمون فصل" in t:
            j = i + 1
            while j < len(blocks) and blocks[j].name not in ("h1", "h2"):
                j += 1
            parts.append(build_exam(ch, cid, blocks[i:j], add_key))
            i = j
            continue

        if name == "h2" and "کارت خلاصه" in t:
            j = i + 1
            while j < len(blocks) and blocks[j].name not in ("h1", "h2"):
                j += 1
            ch.summary_id = f"{cid}s"
            body = "".join(str(x) for x in blocks[i + 1:j])
            parts.append(f'<div class="summary" id="{cid}s">{mk(cid + "s")}<span class="sum-cut">✂</span>'
                         f'<div class="sum-head"><span class="ico">🗂️</span>کارت خلاصهٔ فصل {fa(no)}'
                         f'<small>برای مرور سریع، شب قبل از آزمون</small></div>{body}</div>')
            i = j
            continue

        if name == "h2":
            m = re.match(r"^\s*درس\s*([۰-۹0-9]+)\s*[:：]\s*(.+)$", t)
            lesson_k += 1
            lid = f"{cid}l{lesson_k}"
            if m:
                lno, ltitle = fa(lat(m.group(1))), m.group(2).strip()
                badge = f'<span class="no">درس {lno}</span>'
            else:
                lno, ltitle = "", t
                badge = ""
            ch.lessons.append((lid, lno, ltitle))
            ctx_title = f"درس {lno}" if lno else ltitle
            parts.append(f'<div class="lesson" id="{lid}">{mk(lid)}{badge}<h2>{ltitle}</h2></div>')
            i += 1
            continue

        if name == "h3" and t.startswith("تمرین"):
            j = i + 1
            body, det = [], None
            while j < len(blocks) and blocks[j].name not in ("h1", "h2", "h3", "hr"):
                if blocks[j].name == "details":
                    det = blocks[j]; j += 1; break
                body.append(blocks[j]); j += 1
            ref = keyref(add_key(det, t, "ex")) if det is not None else ""
            parts.append(f'<div class="exercise"><div class="ex-head"><span class="ico">✍️</span>{t}'
                         f'<span class="hint">اول خودت حل کن، بعد پاسخ‌نامه</span></div>'
                         f'<div class="ex-body">{"".join(str(x) for x in body)}</div>{ref}</div>')
            i = j
            continue

        if name == "h3":
            parts.append(f'<h3 class="sub">{inner(b)}</h3>')
            i += 1
            continue

        if name == "details":
            parts.append(keyref(add_key(b, f"پاسخ — {ctx_title or 'فصل'}", "ex")))
            i += 1
            continue

        if name == "blockquote":
            if starts_warn(b):
                parts.append(trap_box(b))
            else:
                parts.append(box("note", "📌", "یادداشت", inner(b)))
            i += 1
            continue

        if name == "p" and starts_warn(b):
            parts.append(trap_box(b))
            i += 1
            continue

        lab = para_label(b) if name == "p" else None
        kind = label_kind(lab) if lab else None
        if kind:
            k, ico = kind
            s = lead_strong(b)
            s.extract()
            rest = inner(b).strip().lstrip(":").strip()
            got, j = absorb(i + 1, False, not rest)
            body = (f"<p>{rest}</p>" if rest else "") + "".join(str(x) for x in got)
            parts.append(box(k, ico, lab, body))
            i = j
            continue

        parts.append(str(b))
        i += 1

    ch.html = render_chapter(ch, cid, intro, parts, keyparts)
    return ch


def trap_box(el: Tag) -> str:
    target = el.find("p") if el.name == "blockquote" else el
    s = lead_strong(target) if target is not None else None
    # «⚠️ **برچسب:** متن» یا «⚠️ متن»
    for node in list(target.contents):
        if isinstance(node, NavigableString) and "⚠" in node:
            node.replace_with(NavigableString(node.replace("⚠️", "").replace("⚠", "").lstrip()))
            break
    s = lead_strong(target)
    label = "تلهٔ تستی"
    if s is not None and re.search(r"[:؟]\s*$", s.get_text()):
        label = s.get_text().strip().rstrip(":").strip()
        s.extract()
        first = target.contents[0] if target.contents else None
        if isinstance(first, NavigableString):
            first.replace_with(NavigableString(first.lstrip()))
    body = inner(el) if el.name == "blockquote" else f"<p>{inner(target)}</p>"
    return box("trap", "⚠️", label, body)


def key_body(det: Tag, kind: str) -> str:
    els = [c for c in det.contents if isinstance(c, Tag)]
    if kind != "exam":
        return "".join(str(e) for e in els)
    out, cur = [], None

    def flush():
        nonlocal cur
        if cur:
            n, ans, body = cur
            out.append(f'<div class="sol"><span class="sn">{n}</span><div class="sb">'
                       f'{f"<span class=ans>{ans}</span>" if ans else ""}{"".join(body)}</div></div>')
        cur = None

    for e in els:
        if e.name == "table":
            rows = e.find_all("tr")
            if len(rows) == 2:
                hs = [tx(c) for c in rows[0].find_all(["th", "td"])]
                vs = [tx(c) for c in rows[1].find_all(["th", "td"])]
                if hs and hs[0] == "سؤال" and vs and vs[0] in ("کلید", "جواب"):
                    flush()
                    cells = "".join(
                        f'<div class="kc{" multi" if len(v) > 2 else ""}"><span class="kq">سؤال {h}</span>'
                        f'<span class="ka">{v}</span></div>' for h, v in zip(hs[1:], vs[1:]))
                    out.append(f'<div class="keygrid">{cells}</div>')
                    continue
        s = lead_strong(e)
        if s is not None:
            m = re.match(r"^\s*([۰-۹0-9]+)\.\s*(.*?)\s*$", s.get_text())
            if m:
                flush()
                ans = m.group(2).rstrip(".").strip()
                s.extract()
                rest = inner(e).strip()
                cur = [m.group(1), ans, [f"<p>{rest}</p>" if rest else ""]]
                continue
        if cur:
            cur[2].append(str(e))
        else:
            out.append(str(e))
    flush()
    return "".join(out)


def add_q_para(cur: dict, p: Tag) -> None:
    """یک پاراگراف از بدنهٔ سؤال: تصویر سؤال، متن، یا متن + چهار گزینه."""
    if p.find("img") and not tx(p):
        cur["body"].append(f'<div class="q-img">{inner(p)}</div>')
        return
    split = split_options(p)
    if split:
        lead, bodies = split
        if lead:
            cur["body"].append(f"<p>{lead}</p>")
        cur["body"].append(opts_html(bodies))
        return
    h = inner(p).strip()
    if h:
        cur["body"].append(f"<p>{h}</p>")


def build_exam(ch: Chapter, cid: str, blocks, add_key) -> str:
    h2 = blocks[0]
    t = tx(h2).replace("📝", "").strip()
    m = re.match(r"^(آزمون فصل\s*[۰-۹0-9]+)\s*(?:\((.+)\))?", t)
    kicker = m.group(1) if m else t
    sub = (m.group(2) if m and m.group(2) else "تست‌های تألیفی (خروجی همه با gcc اجرا و تأیید شده)")
    ch.exam_id = f"{cid}x"
    chips, notes, qs = [], [], []
    cur = None
    key_id = None
    for b in blocks[1:]:
        if b.name == "details":
            key_id = add_key(b, f"آزمون فصل {fa(ch.no)} — کلید و راه‌حل", "exam")
            continue
        s = lead_strong(b)
        if s is not None and s.get_text().strip().startswith("زمان"):
            chips.append(f'<span><span class="ico">⏱️</span> {s.get_text().strip().rstrip(".")}</span>')
            s.extract()
            rest = inner(b).strip()
            if rest:
                notes.append(f"<p>{rest}</p>")
            continue
        if b.name == "blockquote" and cur is None:
            notes.append(inner(b))
            continue
        qm = Q_START.match(s.get_text()) if s is not None else None
        if qm:
            src = qm.group(2)
            if src:
                src = re.sub(r"\s*،\s*", " · ", src.strip())
            s.extract()
            cur = dict(no=qm.group(1), src=src or "تألیفی", body=[])
            qs.append(cur)
            add_q_para(cur, b)
            continue
        if cur is None:
            notes.append(str(b))
            continue
        if b.name == "p":
            add_q_para(cur, b)
        elif b.name == "ol" and len(b.find_all("li", recursive=False)) == 4:
            b["class"] = ["opts-list"]
            cur["body"].append(str(b))
        else:
            cur["body"].append(str(b))
    ch.exam_count = len(qs)
    ch.exam_authored = all(q["src"] == "تألیفی" for q in qs)
    if key_id:
        chips.append(f'<span><span class="ico">🔑</span> کلید و راه‌حل: '
                     f'<a href="#{key_id}">صفحهٔ <span class="pg" data-for="{key_id}">۰۰۰</span></a></span>')
    chips.insert(0, f'<span>{fa(len(qs))} سؤال</span>')
    cards = "".join(
        f'<div class="q"><div class="q-head"><span class="q-no">{q["no"]}</span>'
        f'<span class="q-src">{q["src"]}</span><span class="q-mark">غلط یا حدسی؟<i></i></span></div>'
        f'<div class="q-body">{"".join(q["body"])}</div></div>' for q in qs)
    rule = "" if "۴ دقیقه" in "".join(notes) else "روی هیچ سؤالی بیشتر از ۴ دقیقه نمان، "
    tip = ('<div class="exam-note">' + "".join(notes) + f'<p>✔ مثل جلسهٔ کنکور: زمان بگیر، {rule}'
           'و در مربع کنار سؤال‌های غلط یا حدسی علامت بزن تا در دور دوم فقط همان‌ها را حل کنی.</p></div>')
    note = ""
    return (f'<section class="exam" id="{cid}x"><div class="exam-head">{mk(cid + "x")}'
            f'<div class="exam-kicker">📝 {kicker}</div><div class="exam-title">{sub}</div>'
            f'<div class="exam-chips">{"".join(chips)}</div></div>{note}{tip}{cards}</section>')


def render_chapter(ch: Chapter, cid: str, intro, parts, keyparts) -> str:
    badges = []
    if ch.star:
        badges.append('<span class="star">★ پرتکرار در کنکور</span>')
    if ch.lessons:
        badges.append(f"<span>{fa(len(ch.lessons))} درس</span>")
    if ch.exam_count:
        badges.append(f"<span>{fa(ch.exam_count)} {'تست تألیفی' if ch.exam_authored else 'سؤال کنکور'}"
                      " در آزمون فصل</span>")
    rows = "".join(f'<div class="row"><span class="lbl"><span class="ico">{ico}</span> {lab}</span>'
                   f'<span>{body}</span></div>' if lab else f'<div class="row"><span>{body}</span></div>'
                   for ico, lab, body in intro)
    info = f'<div class="ch-info">{rows}</div>' if rows else ""
    lmap = "".join(f'<a href="#{lid}"><i>{lno}</i><span>{lt}</span></a>' for lid, lno, lt in ch.lessons)
    if ch.exam_id:
        lmap += f'<a href="#{ch.exam_id}"><i class="ico">📝</i><span>آزمون فصل</span></a>'
    cmap = f'<div class="ch-map"><b>نقشهٔ فصل:</b>{lmap}</div>' if lmap else ""
    head = (f'<div class="ch-head">{mk(cid)}<div class="ch-no">{fa(ch.no)}</div>'
            f'<div class="ch-kicker">فصل {fa(ch.no)}</div><h1 class="ch-title">{ch.title}</h1>'
            f'<div class="ch-badges">{"".join(badges)}</div></div>')
    key = ""
    if keyparts:
        key = (f'<section class="key" id="{ch.key_id}"><div class="key-head">{mk(ch.key_id)}'
               f'<span class="kico ico">🔑</span><div><h2>پاسخ‌نامهٔ فصل {fa(ch.no)}</h2>'
               '<small>تا تمرین‌ها و آزمون فصل را خودت حل نکرده‌ای، این صفحه‌ها را نخوان.</small></div></div>'
               f'{"".join(keyparts)}</section>')
    return f'<section class="chapter" id="{cid}">{head}{info}{cmap}{"".join(parts)}{key}</section>'


# ---------------------------------------------------------------- جلد، راهنما، فهرست
def cover_html(subj, chapters) -> str:
    n_q = sum(c.exam_count for c in chapters if not c.exam_authored)
    n_a = sum(c.exam_count for c in chapters if c.exam_authored)
    n_l = sum(len(c.lessons) for c in chapters)
    stat_q = (f'<div class="cv-stat"><b>{fa(n_q)}</b><span>سؤال واقعی کنکور با کلید رسمی</span></div>'
              if n_q else f'<div class="cv-stat"><b>{fa(n_a)}</b><span>تست تألیفیِ اجراشده با gcc</span></div>')
    chs = "".join(f"<div><i>{fa(c.no)}</i>{c.title}</div>" for c in chapters)
    return f"""<section class="cover"><div class="cv-band"><div class="cv-o1"></div><div class="cv-o2"></div>
<div class="cv-glyph">{html.escape(subj['glyph'])}</div></div>
<div class="cv-text"><span class="cv-kicker">جزوهٔ آموزشی · کنکور دکتری ۱۴۰۶ · مجموعهٔ ۲۳۵۴</span>
<div class="cv-no">درس {fa(subj['no'])} از ۱۰ سرفصل</div><div class="cv-title">{subj['name']}</div>
<div class="cv-sub">درس‌نامهٔ کوتاه و فصل‌به‌فصل، مثال و تلهٔ تستی، تمرین با پاسخ،
و آزمون آخر هر فصل از سؤال‌های واقعی کنکور</div></div>
<div class="cv-stats"><div class="cv-stat"><b>{fa(len(chapters))}</b><span>فصل</span></div>
<div class="cv-stat"><b>{fa(n_l)}</b><span>درس</span></div>{stat_q}</div>
<div class="cv-list-t">فصل‌های این جزوه</div><div class="cv-chapters">{chs}</div>
<div class="cv-foot"><span>مهندسی و علم کامپیوتر · کنکور دکتری ۱۴۰۶</span><span>نسخهٔ آبان ۱۴۰۵</span></div>
</section>"""


def guide_html(subj, chapters) -> str:
    authored = all(c.exam_authored for c in chapters if c.exam_count)
    src = ("تست‌های آزمون فصل‌های این درس <b>تألیفی</b>اند (این درس در کنکور ارشد کامپیوتر سؤال سابقه "
           "ندارد) و خروجی همهٔ کدها با کامپایلر gcc اجرا و تأیید شده است."
           if authored else
           "سؤال‌های آزمون فصل از کنکور <b>ارشد مهندسی کامپیوتر ۱۳۹۸ تا ۱۴۰۴</b> هستند و کلید آن‌ها "
           "<b>کلید رسمی سازمان سنجش</b> است. جاهایی که کلید رسمی مبهم یا مشکوک است، در راه‌حل توضیح داده شده.")
    steps = [("۵", "پیش‌آزمون", "سؤال اول آزمون فصل را قبل از خواندن امتحان کن"),
             ("۳۵", "درس‌نامه", "مثال‌ها را قبل از دیدن حل، خودت امتحان کن"),
             ("۳۰", "تمرین", "بدون نگاه به پاسخ‌نامه حل کن"),
             ("۱۵+", "آزمون فصل", "با زمان، مثل جلسهٔ کنکور"),
             ("۵", "دفتر خطا", "هر غلط یا حدسی = یک سطر در دفتر خطا")]
    cyc = "".join(f'<div class="step"><span class="n">{fa(k + 1)}</span><b>{t}</b>'
                  f'<span class="m">{m} دقیقه</span>{d}</div>' for k, (m, t, d) in enumerate(steps))
    return f"""<section class="front guide">{mk('guide')}
<div class="pt">راهنمای استفاده از جزوه</div>
<div class="pt-sub">هر فصل با یک برگهٔ رنگی شروع می‌شود و همیشه همین ترتیب را دارد:
درس‌ها ← آزمون فصل ← کارت خلاصه ← پاسخ‌نامه.</div>
<div class="legend">
<div class="lg l-ex"><b><span class="ico">✏️</span> مثال</b>یک مسئلهٔ حل‌شده برای اینکه قاعده را در عمل ببینی.</div>
<div class="lg l-trap"><b><span class="ico">⚠️</span> تلهٔ تستی</b>جایی که طراح کنکور بیشتر از همه داوطلب‌ها را غافلگیر می‌کند.</div>
<div class="lg l-tip"><b><span class="ico">💡</span> نکته و قاعده</b>میان‌بُرها و قاعده‌هایی که سر جلسه وقت می‌خرند.</div>
<div class="lg l-exr"><b><span class="ico">✍️</span> تمرین</b>آخر هر درس؛ پاسخ‌ها در پاسخ‌نامهٔ آخر همان فصل است (با شمارهٔ صفحه).</div>
<div class="lg l-exam"><b><span class="ico">📝</span> آزمون فصل</b>سؤال‌ها در کارت‌های جدا، با منبع و مربعی برای علامت غلط یا حدسی.</div>
<div class="lg l-sum"><b><span class="ico">🗂️</span> کارت خلاصه</b>چکیدهٔ یک‌صفحه‌ای فصل برای مرور شب قبل از آزمون.</div>
</div>
<div class="h-sec">چرخهٔ مطالعهٔ هر فصل (یک بلوک ۹۰ دقیقه‌ای)</div>
<div class="cycle">{cyc}</div>
<div class="golden"><b>قانون طلایی:</b> خواندن یعنی بلد بودن نیست. جزوه‌ای که روان خوانده شد ولی آزمونش را
نزدی، یاد گرفته نشده است. معیار فقط <b>درصد تست</b> است، با فرمول نمرهٔ منفی:
<b style="unicode-bidi:isolate;direction:rtl">(۳ × درست − غلط) ÷ (۳ × کل)</b>.</div>
<div class="srcnote"><b>منبع سؤال‌ها:</b> {src} فهرست قابل کلیک است: روی هر عنوان بزن تا به همان صفحه بروی.
در نمایشگر PDF، نشانک‌ها (bookmark) هم فصل‌ها و درس‌ها را نشان می‌دهند.</div>
</section>"""


def toc_html(chapters, pages) -> str:
    def pg(i):
        return f'<span class="pg">{fa(pages[i]) if pages and i in pages else "۰۰۰"}</span>'
    rows = []
    for c in chapters:
        cid = f"c{c.no}"
        chip = (f'<span class="toc-chip">{fa(c.exam_count)} '
                f'{"تست تألیفی" if c.exam_authored else "سؤال کنکور"}</span>') if c.exam_count else ""
        star = ' <span style="color:#e0a800">★</span>' if c.star else ""
        rows.append(f'<a class="toc-ch" href="#{cid}"><span class="toc-num">{fa(c.no)}</span>'
                    f'<span class="toc-t">{c.title}{star}</span>{chip}<span class="toc-fill"></span>{pg(cid)}</a>')
        for lid, lno, lt in c.lessons:
            k = f"درس {lno}" if lno else "•"
            rows.append(f'<a class="toc-row" href="#{lid}"><span class="k">{k}</span><span>{lt}</span>'
                        f'<span class="toc-fill"></span>{pg(lid)}</a>')
        ext = []
        if c.exam_id:
            ext.append(f'<a href="#{c.exam_id}">📝 آزمون فصل {pg(c.exam_id)}</a>')
        if c.summary_id:
            ext.append(f'<a href="#{c.summary_id}">🗂️ کارت خلاصه {pg(c.summary_id)}</a>')
        if c.key_entries:
            ext.append(f'<a href="#{c.key_id}">🔑 پاسخ‌نامه {pg(c.key_id)}</a>')
        if ext:
            sep = ' <span style="color:#c7ccd8">|</span> '
            rows.append(f'<div class="toc-row ext"><span class="k"></span>{sep.join(ext)}</div>')
    return (f'<section class="front toc">{mk("toc")}<div class="pt">فهرست</div>'
            f'<div class="pt-sub">روی هر سطر بزن تا مستقیم به همان صفحه بروی.</div>{"".join(rows)}</section>')


def book_html(subj, chapters, fonts, pages=None) -> str:
    pal = palette(subj["color"])
    css = font_css(fonts) + (CSS % pal)
    body = cover_html(subj, chapters) + guide_html(subj, chapters) + toc_html(chapters, pages)
    body += "".join(c.html for c in chapters)
    if pages:
        def fill(m):
            pid = m.group(1)
            return f'<span class="pg" data-for="{pid}">{fa(pages[pid]) if pid in pages else "۰۰۰"}</span>'
        body = re.sub(r'<span class="pg" data-for="([a-z0-9]+)">۰۰۰</span>', fill, body)
    cls = "code" if subj.get("code") else ""
    return (f'<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8">'
            f'<title>{subj["name"]}</title><style>{css}</style></head>'
            f'<body class="{cls}">{body}</body></html>')


# ---------------------------------------------------------------- سرصفحه و پاصفحه
OVERLAY_CSS = """
@page{size:A4;margin:0;} html{direction:rtl;} body{margin:0;font-family:Vazirmatn,sans-serif;
 -webkit-print-color-adjust:exact;print-color-adjust:exact;}
.p{position:relative;width:210mm;height:296.9mm;break-after:page;overflow:hidden;}
.hd{position:absolute;top:9mm;right:15mm;left:15mm;display:flex;align-items:center;gap:3mm;
 font-size:8.4pt;color:#8a93a6;border-bottom:.6pt solid #e2e6ee;padding-bottom:1.3mm;line-height:1.6;}
.hd .s{color:var(--c);font-weight:800;display:flex;align-items:center;gap:1.6mm;}
.hd .s i{display:inline-block;width:2.3mm;height:2.3mm;border-radius:.6mm;background:var(--c);}
.hd .t{margin-right:auto;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:110mm;}
.ft{position:absolute;bottom:7.5mm;right:15mm;left:15mm;display:flex;align-items:center;
 justify-content:space-between;font-size:7.8pt;color:#a0a8b8;line-height:1.6;}
.ft .n{background:var(--c);color:#fff;font-weight:800;font-size:8.6pt;border-radius:10mm;
 padding:0 3.2mm;min-width:5mm;text-align:center;}
"""


def overlay_html(subj, labels, fonts) -> str:
    pal = palette(subj["color"])
    css = font_css(fonts) + f":root{{--c:{pal['c']};}}" + OVERLAY_CSS
    pages = []
    for i, lab in enumerate(labels):
        if lab is None:
            pages.append('<div class="p"></div>')
            continue
        pages.append(f'<div class="p"><div class="hd"><span class="s"><i></i>{subj["name"]}</span>'
                     f'<span class="t">{lab}</span></div><div class="ft"><span>کنکور دکتری ۱۴۰۶</span>'
                     f'<span class="n">{fa(i + 1)}</span><span>مجموعهٔ ۲۳۵۴</span></div></div>')
    return (f'<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><style>{css}</style>'
            f'</head><body>{"".join(pages)}</body></html>')


# ---------------------------------------------------------------- چاپ و مونتاژ
def print_pdf(jobs) -> None:
    args = []
    for h, p in jobs:
        args += [str(h), str(p)]
    subprocess.run(["node", str(PRINT_JS), *args], check=True)


def marker_pages(pdf: pathlib.Path) -> dict:
    txt = subprocess.run(["pdftotext", "-raw", str(pdf), "-"], capture_output=True, text=True,
                         check=True).stdout
    pages = {}
    for i, pg in enumerate(txt.split("\f")):
        for m in re.finditer(r"@@([a-z0-9]+)@@", pg):
            pages.setdefault(m.group(1), i + 1)
    return pages


def build_subject(subj, fonts, keep_html=False) -> pathlib.Path | None:
    d = SRC / subj["key"]
    files = sorted(d.glob("فصل-*.md"))
    if not files:
        return None
    chapters = [build_chapter(f) for f in files]
    OUT.mkdir(exist_ok=True)
    out = OUT / f"{subj['no']:02d}-{subj['key']}.pdf"
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        h1, p1 = tmp / "pass1.html", tmp / "pass1.pdf"
        h1.write_text(book_html(subj, chapters, fonts), encoding="utf-8")
        print_pdf([(h1, p1)])
        pages = marker_pages(p1)
        h2, p2 = tmp / "pass2.html", tmp / "pass2.pdf"
        h2.write_text(book_html(subj, chapters, fonts, pages), encoding="utf-8")
        print_pdf([(h2, p2)])
        n = len(PdfReader(p2).pages)
        starts = sorted((pages[f"c{c.no}"], c) for c in chapters if f"c{c.no}" in pages)
        labels = []
        for i in range(1, n + 1):
            if i == 1:
                labels.append(None)
                continue
            cur = "راهنما و فهرست"
            for sp, c in starts:
                if i >= sp:
                    cur = f"فصل {fa(c.no)} · {c.title}"
            labels.append(cur)
        ho, po = tmp / "overlay.html", tmp / "overlay.pdf"
        ho.write_text(overlay_html(subj, labels, fonts), encoding="utf-8")
        print_pdf([(ho, po)])
        reader, ov = PdfReader(p2), PdfReader(po)
        w = PdfWriter(clone_from=reader)
        for i, page in enumerate(w.pages):
            if i < len(ov.pages):
                page.merge_page(ov.pages[i])
            page.compress_content_streams(level=9)
        # نشانک‌ها
        if "guide" in pages:
            w.add_outline_item("راهنمای استفاده", pages["guide"] - 1)
        if "toc" in pages:
            w.add_outline_item("فهرست", pages["toc"] - 1)
        for c in chapters:
            cid = f"c{c.no}"
            if cid not in pages:
                continue
            par = w.add_outline_item(f"فصل {fa(c.no)}: {c.title}", pages[cid] - 1)
            for lid, lno, lt in c.lessons:
                if lid in pages:
                    w.add_outline_item(f"درس {lno}: {lt}" if lno else lt, pages[lid] - 1, parent=par)
            for key, lab in ((c.exam_id, "آزمون فصل"), (c.summary_id, "کارت خلاصه"), (c.key_id, "پاسخ‌نامه")):
                if key and key in pages:
                    w.add_outline_item(lab, pages[key] - 1, parent=par)
        w.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
        w.add_metadata({"/Title": f"{subj['name']} — جزوهٔ کنکور دکتری ۱۴۰۶",
                        "/Subject": "جزوهٔ آموزشی فصل‌به‌فصل با آزمون از سؤال‌های واقعی کنکور"})
        w.page_mode = "/UseOutlines"
        with open(out, "wb") as fh:
            w.write(fh)
        if keep_html:
            shutil.copy(h2, OUT / f"{subj['no']:02d}-{subj['key']}.html")
    return out


def book_stats(subj):
    files = sorted((SRC / subj["key"]).glob("فصل-*.md"))
    if not files:
        return None
    text = "\n".join(f.read_text(encoding="utf-8") for f in files)
    n_q = len(re.findall(r"^\*\*[۰-۹0-9]+\.\s*\(ارشد", text, re.M))
    authored = n_q == 0
    if authored:
        n_q = sum(len(re.findall(r"^\*\*[۰-۹0-9]+\.\*\*", re.split(r"^## 📝", t, flags=re.M)[-1], re.M))
                  for t in (f.read_text(encoding="utf-8") for f in files))
    return len(files), n_q, authored


def update_root_readme() -> None:
    """جدول کتاب‌ها در README.md ریشه را بین دو نشانگر بازنویسی می‌کند."""
    readme = ROOT / "README.md"
    if not readme.exists():
        return
    rows = []
    for subj in SUBJECTS:
        pdf = OUT / f"{subj['no']:02d}-{subj['key']}.pdf"
        st = book_stats(subj)
        if st is None or not pdf.exists():
            rows.append(f"| {fa(subj['no'])} | {subj['name']} | — | — | — | به‌زودی |")
            continue
        n_ch, n_q, authored = st
        pages = len(PdfReader(pdf).pages)
        q = f"{fa(n_q)} {'تست تألیفی' if authored else 'سؤال کنکور'}"
        link = urllib.parse.quote(f"جزوه-PDF/{pdf.name}")
        rows.append(f"| {fa(subj['no'])} | **{subj['name']}** | {fa(n_ch)} | {fa(pages)} | {q} | [📕 باز کردن PDF]({link}) |")
    table = ("| # | درس | فصل | صفحه | آزمون‌های فصل | فایل |\n|---|---|---|---|---|---|\n"
             + "\n".join(rows) + "\n")
    s = readme.read_text(encoding="utf-8")
    s = re.sub(r"(<!-- books:start -->\n).*?(<!-- books:end -->)", lambda m: m.group(1) + table + m.group(2),
               s, flags=re.S)
    readme.write_text(s, encoding="utf-8")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    keep = "--keep-html" in sys.argv
    fonts = ensure_fonts()
    for subj in SUBJECTS:
        if args and not any(a in subj["key"] or a in subj["name"] for a in args):
            continue
        out = build_subject(subj, fonts, keep)
        if out:
            print(f"{out.relative_to(ROOT)}  ({len(PdfReader(out).pages)} صفحه)")
    update_root_readme()


if __name__ == "__main__":
    main()
