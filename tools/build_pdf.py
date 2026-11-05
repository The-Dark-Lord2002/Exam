#!/usr/bin/env python3
"""ساخت PDF از جزوه‌های Markdown (فارسی، راست‌به‌چپ).

اجرا (از ریشهٔ ریپازیتوری):
    python3 tools/build_pdf.py            # همهٔ فصل‌ها
    python3 tools/build_pdf.py <file.md>  # فقط یک فصل

نیازها: pandoc، Node.js با Playwright (Chromium)، فونت Vazirmatn
(اگر نباشد با `npm pack vazirmatn` در tools/.fonts دانلود می‌شود).

جواب‌های پنهان (<details>) در PDF به «پاسخ‌نامه» در انتهای فصل منتقل می‌شوند
تا هنگام حل تمرین دیده نشوند.
"""
import html
import json
import pathlib
import re
import subprocess
import sys
import tarfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
NOTES = ROOT / "جزوه"
OUT = NOTES / "pdf"
FONT_DIR = ROOT / "tools" / ".fonts"
SUBJECT_PREFIX = {
    "ریاضیات-گسسته": "گسسته",
    "ساختمان-داده": "ساختمان-داده",
    "برنامه-سازی": "برنامه-سازی",
}

FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
DETAILS_RE = re.compile(
    r"<details>\s*<summary>(.*?)</summary>\s*(.*?)\s*</details>", re.S
)


def ensure_font() -> pathlib.Path:
    ttf = FONT_DIR / "package" / "fonts" / "ttf"
    if not (ttf / "Vazirmatn-Regular.ttf").exists():
        FONT_DIR.mkdir(parents=True, exist_ok=True)
        subprocess.run(["npm", "pack", "vazirmatn@33.0.3", "--silent"],
                       cwd=FONT_DIR, check=True)
        with tarfile.open(next(FONT_DIR.glob("vazirmatn-*.tgz"))) as t:
            t.extractall(FONT_DIR, filter="data")
    return ttf


def move_answers_to_end(md: str) -> str:
    """هر بلوک <details> را با یک ارجاع عوض می‌کند و متنش را به انتها می‌برد."""
    answers = []
    out, pos = [], 0
    for m in DETAILS_RE.finditer(md):
        before = md[:m.start()]
        heads = re.findall(r"^## (.+)$", before, re.M)
        section = heads[-1].strip() if heads else "فصل"
        section = re.sub(r"^[^\w]+", "", section).strip()  # حذف ایموجی ابتدای عنوان
        n = len(answers) + 1
        fa = str(n).translate(FA_DIGITS)
        answers.append((fa, section, m.group(1).strip(), m.group(2).strip()))
        out.append(md[pos:m.start()])
        out.append(f"\n> 🔑 **{m.group(1).strip()}:** پاسخ‌نامهٔ انتهای فصل، بخش {fa} ({section})\n")
        pos = m.end()
    out.append(md[pos:])
    body = "".join(out)
    if answers:
        body += '\n\n<div class="pagebreak"></div>\n\n# 🔑 پاسخ‌نامهٔ فصل\n'
        for n, section, summary, content in answers:
            body += f"\n## بخش {n}: {section}\n\n{content}\n"
    return body


def md_to_html(md: str) -> str:
    return subprocess.run(
        ["pandoc", "-f", "gfm", "-t", "html5", "--wrap=none"],
        input=md, capture_output=True, text=True, check=True,
    ).stdout


CSS = """
@font-face { font-family: Vazirmatn; src: url('{ttf}/Vazirmatn-Regular.ttf'); font-weight: 400; }
@font-face { font-family: Vazirmatn; src: url('{ttf}/Vazirmatn-Medium.ttf'); font-weight: 500; }
@font-face { font-family: Vazirmatn; src: url('{ttf}/Vazirmatn-Bold.ttf'); font-weight: 700; }
@font-face { font-family: CodeFA; src: url('{ttf}/Vazirmatn-Regular.ttf');
  unicode-range: U+0600-06FF, U+200C-200F, U+FB50-FDFF, U+FE70-FEFF; }
@page { size: A4; margin: 16mm 15mm 18mm 15mm; }
html { direction: rtl; }
body { font-family: Vazirmatn, 'DejaVu Sans', sans-serif; font-size: 11.5pt; line-height: 1.85;
       color: #1c1c1c; text-align: justify; }
h1 { font-size: 20pt; color: #1f3a5f; border-bottom: 3px solid #1f3a5f; padding-bottom: 6px; margin: 0 0 14px; }
h2 { font-size: 15pt; color: #fff; background: #1f3a5f; padding: 6px 12px; border-radius: 6px;
     margin: 26px 0 12px; break-after: avoid; }
h3 { font-size: 12.5pt; color: #1f3a5f; border-right: 4px solid #e0a100; padding-right: 8px;
     margin: 18px 0 8px; break-after: avoid; }
p { margin: 6px 0; }
strong { color: #0d2a4a; }
blockquote { background: #f3f6fb; border-right: 4px solid #4a78b5; margin: 10px 0; padding: 6px 12px;
             border-radius: 4px; }
blockquote p { margin: 3px 0; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 10.5pt; }
tr { break-inside: avoid; }
thead { display: table-header-group; }
th { background: #e6edf6; color: #1f3a5f; }
th, td { border: 1px solid #b9c6d6; padding: 5px 8px; text-align: right; vertical-align: top; }
tr:nth-child(even) td { background: #fafbfd; }
code { font-family: CodeFA, 'DejaVu Sans Mono', 'DejaVu Sans', Vazirmatn, monospace; font-size: 0.9em;
       direction: ltr; unicode-bidi: isolate; background: #f2f2f2; padding: 1px 4px; border-radius: 3px; }
pre { direction: ltr; text-align: left; background: #f6f8fa; border: 1px solid #d8dee4;
      border-radius: 6px; padding: 8px 12px; font-size: 10pt; line-height: 1.5; break-inside: avoid; }
pre code { background: none; padding: 0; font-size: 1em; }
ol, ul { margin: 6px 0; padding-right: 22px; }
ol { list-style-type: persian; }
li { margin: 2px 0; }
hr { border: none; border-top: 1px dashed #b9c6d6; margin: 18px 0; }
.pagebreak { break-before: page; }
img { display: block; max-width: 55%; max-height: 70mm; margin: 8px auto; }
img[src*="/q/"] { max-width: 100%; max-height: 120mm; margin: 4px 0 10px auto; break-inside: avoid; }
a { color: #1f5fa8; text-decoration: none; }
"""


def build(md_path: pathlib.Path, ttf: pathlib.Path) -> pathlib.Path:
    md = md_path.read_text(encoding="utf-8")
    md = re.sub(r"\s*فایل اجرایی: \[`[^`]+`\]\([^)]+\)", "", md)  # لینک فایل در PDF کاربرد ندارد
    body = md_to_html(move_answers_to_end(md))
    body = re.sub(r'src="(?!https?:|file:|data:)([^"]+)"',
                  lambda m: f'src="{(md_path.parent / html.unescape(m.group(1))).resolve().as_uri()}"', body)
    title = re.search(r"^# (.+)$", md, re.M).group(1).strip()
    doc = (
        '<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8">'
        f"<title>{html.escape(title)}</title><style>{CSS.replace('{ttf}', ttf.as_uri())}</style>"
        f"</head><body>{body}</body></html>"
    )
    OUT.mkdir(parents=True, exist_ok=True)
    prefix = SUBJECT_PREFIX.get(md_path.parent.name, md_path.parent.name)
    pdf = OUT / f"{prefix}-{md_path.stem}.pdf"
    tmp_html = FONT_DIR / f"_{prefix}-{md_path.stem}.html"
    tmp_html.write_text(doc, encoding="utf-8")
    footer = ('<div style="width:100%;font-size:8pt;color:#777;text-align:center;'
              'font-family:DejaVu Sans">'
              '<span class="pageNumber"></span> / <span class="totalPages"></span></div>')
    js = f"""
const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto({json.dumps(tmp_html.as_uri())}, {{ waitUntil: 'networkidle' }});
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({{ path: {json.dumps(str(pdf))}, format: 'A4', printBackground: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: {json.dumps(footer)},
    margin: {{ top: '16mm', bottom: '18mm', left: '15mm', right: '15mm' }} }});
  await b.close();
}})();
"""
    subprocess.run(["node", "-e", js], check=True)
    tmp_html.unlink()
    return pdf


def main() -> None:
    ttf = ensure_font()
    files = [pathlib.Path(a).resolve() for a in sys.argv[1:]] or sorted(NOTES.glob("*/فصل-*.md"))
    for f in files:
        print(build(f, ttf).relative_to(ROOT))


if __name__ == "__main__":
    main()
