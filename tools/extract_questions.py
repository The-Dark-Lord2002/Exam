#!/usr/bin/env python3
"""برش تصویر هر سؤال از «کتاب کار تست‌های مبحثی» بر اساس سرخط «ارشد YYYY · سؤال NN».

اجرا:  python3 tools/extract_questions.py <صفحهٔ شروع> <صفحهٔ پایان> <پوشهٔ خروجی>
خروجی: <پوشه>/YYYY-NN.png  (عددها لاتین)
"""
import pathlib
import re
import subprocess
import sys
import tempfile

from PIL import Image, ImageChops

ROOT = pathlib.Path(__file__).resolve().parent.parent
BOOK = ROOT / "کتاب-کار-تست-مبحثی-دکتری.pdf"
DPI = 200
FA = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
LINE = re.compile(r'<line xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</line>', re.S)


def lines(page: int):
    out = subprocess.run(["pdftotext", "-f", str(page), "-l", str(page), "-bbox-layout", str(BOOK), "-"],
                         capture_output=True, text=True, check=True).stdout
    for m in LINE.finditer(out):
        words = re.findall(r">([^<]+)</word>", m.group(5))
        text = " ".join(words)[::-1]  # متن معکوس ذخیره شده
        yield float(m.group(2)), float(m.group(4)), text


def trim(im: Image.Image) -> Image.Image:
    bg = Image.new(im.mode, im.size, (255, 255, 255))
    box = ImageChops.difference(im, bg).getbbox()
    return im.crop(box) if box else im


def main(first: int, last: int, out_dir: str) -> None:
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    k = DPI / 72
    with tempfile.TemporaryDirectory() as tmp:
        for p in range(first, last + 1):
            ls = list(lines(p))
            heads, stops = [], []
            for y0, y1, t in ls:
                t2 = re.sub(r"\d+", lambda m: m.group(0)[::-1], t.translate(FA))
                m = re.search(r"(\d{4})\s*·\s*(\d+)\s*لاؤس", t2) or re.search(r"(\d{4})\s*·\s*سؤال\s*(\d+)", t2)
                if "ارشد" in t2 or "دشرا" in t2:
                    nums = re.findall(r"\d+", t2)
                    year = next((n for n in nums if len(n) == 4), None)
                    q = next((n for n in nums if len(n) <= 3 and n != year), None)
                    if year and q:
                        heads.append((y0, y1, f"{year}-{int(q):02d}"))
                        continue
                if re.match(r"^\s*\d+\.\d+\s", t2):
                    stops.append(y0)
            if not heads:
                continue
            subprocess.run(["pdftoppm", "-r", str(DPI), "-f", str(p), "-l", str(p), "-png", str(BOOK), f"{tmp}/pg"],
                           check=True)
            img = Image.open(next(pathlib.Path(tmp).glob("pg*.png"))).convert("RGB")
            for i, (y0, y1, name) in enumerate(heads):
                nxt = [h[0] for h in heads[i + 1:]] + [s for s in stops if s > y1] + [img.height / k - 40]
                end = min(nxt) - 12
                crop = img.crop((int(30 * k), int((y1 + 2) * k), img.width - int(30 * k), int(end * k)))
                trim(crop).save(out / f"{name}.png")
                print(p, name)
            for f in pathlib.Path(tmp).glob("pg*.png"):
                f.unlink()


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
