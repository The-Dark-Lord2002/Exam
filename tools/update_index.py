#!/usr/bin/env python3
"""جدول PDF ها در جزوه/README.md را از روی فایل‌های فصل بازسازی می‌کند."""
import pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
R = ROOT / "جزوه" / "README.md"
SUBJ = [("ریاضیات-گسسته", "ریاضیات گسسته", "گسسته"), ("آمار-و-احتمال", "آمار و احتمال", "آمار-و-احتمال"),
        ("جبر-خطی", "جبر خطی", "جبر-خطی"), ("ساختمان-داده", "ساختمان داده", "ساختمان-داده"),
        ("برنامه-سازی", "برنامه‌سازی", "برنامه-سازی"), ("نظریه-زبان-ها", "نظریهٔ زبان‌ها", "نظریه-زبان-ها"),
        ("مدار-منطقی", "مدار منطقی", "مدار-منطقی"), ("معماری-کامپیوتر", "معماری کامپیوتر", "معماری-کامپیوتر"),
        ("سیستم-عامل", "سیستم‌عامل", "سیستم-عامل"), ("هوش-مصنوعی", "هوش مصنوعی", "هوش-مصنوعی")]
rows = []
for d, name, pre in SUBJ:
    for md in sorted((ROOT / "جزوه" / d).glob("فصل-*.md")):
        title = re.search(r"^# (.+)$", md.read_text(encoding="utf-8"), re.M).group(1).replace("★", "").strip()
        rows.append(f"| {name} | {title} | [PDF](pdf/{pre}-{md.stem}.pdf) |")
s = R.read_text(encoding="utf-8")
table = "| درس | فصل | فایل |\n|---|---|---|\n" + "\n".join(rows) + "\n"
s = re.sub(r"\| درس \| فصل \| فایل \|\n\|---\|---\|---\|\n(?:\|.*\|\n)+", table, s, count=1)
R.write_text(s, encoding="utf-8")
print(len(rows), "chapters indexed")
