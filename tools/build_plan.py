#!/usr/bin/env python3
"""ساخت «برنامهٔ مطالعه» به‌صورت PDF: جزوه-PDF/00-برنامه-مطالعه.pdf

برنامهٔ ۱۴ هفته‌ای دفترچهٔ راهنما، از شنبه ۱۶ آبان ۱۴۰۵ دوباره شروع شده است (۱۳ هفته تا آزمون):
  - هفته‌های ۱ تا ۸ دفترچه، یک هفته جلوتر.
  - هفته‌های ۹ و ۱۰ دفترچه (سیستم‌عامل + تست) در هفتهٔ ۹ ادغام شده‌اند.
  - فاز ۲ (۱۹ دی تا ۲ بهمن)، فاز ۳ و هفتهٔ آزمون با همان تاریخ‌های دفترچه.
برای هر خانه، کتاب و فصل و درس و شمارهٔ صفحه از نشانگرهای کتاب‌های ساخته‌شده خوانده می‌شود،
پس بعد از هر بار ساختن دوبارهٔ کتاب‌ها، این برنامه را هم دوباره بساز:

    python3 tools/build_plan.py              # فقط PDF
    python3 tools/build_plan.py --progress   # + بازنویسی tutor/progress.md (فقط وقتی خالی است!)
"""
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_book as bb  # noqa: E402
from pypdf import PdfReader, PdfWriter  # noqa: E402

fa = bb.fa
OUT = bb.OUT / "00-برنامه-مطالعه.pdf"

# ---------------------------------------------------------------- کتاب‌ها
BOOKS = {  # کد: (کلید درس، نام کوتاه)
    "G": ("ریاضیات-گسسته", "گسسته"), "P": ("آمار-و-احتمال", "احتمال"), "L": ("جبر-خطی", "جبر خطی"),
    "C": ("برنامه-سازی", "برنامه‌سازی"), "M": ("مدار-منطقی", "مدار"), "R": ("معماری-کامپیوتر", "معماری"),
    "D": ("ساختمان-داده", "ساختمان داده"), "T": ("نظریه-زبان-ها", "نظریه"), "O": ("سیستم-عامل", "سیستم‌عامل"),
    "H": ("هوش-مصنوعی", "هوش"),
}
SUBJ = {s["key"]: s for s in bb.SUBJECTS}
_pages = {}


def pages_of(code):
    key = BOOKS[code][0]
    if key not in _pages:
        pdf = bb.OUT / f"{SUBJ[key]['no']:02d}-{key}.pdf"
        _pages[key] = bb.marker_pages(pdf) if pdf.exists() else None
    return _pages[key]


def ref(spec: str) -> str:
    """'G3:1' درس، 'G3:1-2' یا 'G3:1,5' چند درس، 'G3:x' آزمون فصل، 'G3' کل فصل."""
    code, rest = spec[0], spec[1:]
    ch, _, ls = rest.partition(":")
    ch = int(ch)
    key, short = BOOKS[code]
    color = SUBJ[key]["color"]
    pg = pages_of(code)
    if ls == "x":
        label, mid = f"آزمون فصل {fa(ch)}", f"c{ch}x"
    elif ls:
        if "-" in ls:
            a, b = ls.split("-")
            label, first = f"فصل {fa(ch)} · درس {fa(a)} تا {fa(b)}", a
        elif "," in ls:
            parts = ls.split(",")
            label, first = f"فصل {fa(ch)} · درس {' و '.join(fa(p) for p in parts)}", parts[0]
        else:
            label, first = f"فصل {fa(ch)} · درس {fa(ls)}", ls
        mid = f"c{ch}l{first}"
    else:
        label, mid = f"فصل {fa(ch)}", f"c{ch}"
    if pg is None:
        tail = '<i>کتاب تا ۲۶ آذر آماده می‌شود</i>'
    else:
        tail = f"ص {fa(pg.get(mid, '؟'))}"
    return (f'<span class="ref" style="--rc:{color}"><b>{short}</b> · {label} · {tail}</span>')


def cell(topic: str, refs: str = "", note: str = "", tag: str = "") -> str:
    r = "".join(ref(s) for s in refs.split()) if refs else ""
    t = f'<span class="tag">{tag}</span>' if tag else ""
    n = f'<div class="note">{note}</div>' if note else ""
    return f'<div class="topic">{topic}{t}</div>{r}{n}'


NOB = '<div class="nob">— (کلاس الگوریتم؛ بلوک B نداری)</div>'
EVEN = "فقط یکشنبهٔ زوج"

# ---------------------------------------------------------------- فاز ۱ (هفته ۱ تا ۹)
# هر روز: (ریاضی، تخصصی A، تخصصی B)
W = []
W.append(dict(title="منطق و مجموعه · تحلیل پیچیدگی · برنامه‌سازی پایه", note=(
    "هفتهٔ اول: درس‌نامه می‌تواند نیمی از بلوک تست را هم بگیرد (فقط همین هفته). "
    "بلوک B برنامه‌سازی فشرده است؛ اگر تمام نشد، بقیه را از تست‌های همان فصل یاد بگیر."), days=[
    (cell("منطق گزاره‌ها: ادوات، جدول درستی، هم‌ارزی", "G1:1-2"),
     cell("نمادهای O، Ω، Θ و مقایسهٔ رشد", "D1:1"),
     cell("نوع داده، عملگرها، اولویت، تبدیل نوع", "C1:1-5")),
    (cell("استلزام، قواعد استنتاج، صورت‌های نرمال", "G1:2-3"),
     cell("تحلیل حلقه‌ها و شمارش تکرار", "D1:2"),
     cell("شرط، switch، حلقه، break و continue", "C2:1-4", tag=EVEN)),
    (cell("سورها و منطق مسندات", "G1:4 G1:x"),
     cell("روابط بازگشتی: جایگذاری و درخت بازگشت", "D1:4"),
     NOB),
    (cell("مجموعه‌ها، اعمال، مجموعهٔ توانی", "G2:1"),
     cell("قضیهٔ اصلی و حالت‌های خاص", "D1:3"),
     cell("تابع، حوزهٔ متغیر، static، ماکرو", "C3:1-4")),
    (cell("تابع: یک‌به‌یک، پوشا، وارون، ترکیب", "G2:2"),
     cell("تغییر متغیر در بازگشتی، تحلیل سرشکن", "D1:4-5"),
     cell("اشاره‌گر و آرایه", "C5:1-3")),
    (cell("شمارایی، استدلال قطری کانتور", "G2:3 G2:x"),
     cell("تست ترکیبی تحلیل پیچیدگی", "D1:x"),
     cell("تست‌های «خروجی کد»", "C1:x C2:x C3:x")),
]))
W.append(dict(title="شمارش · لیست، درهم‌سازی، درخت و هیپ · برنامه‌سازی", note=(
    "شمارش پرتکرارترین مبحث کل ریاضیات است (۱۵ سؤال در ۷ سال). این هفته حداقل ۱۲۰ تست شمارش بزن: "
    "۱۶ سؤال کنکور در آزمون فصل ۳ گسسته است و بقیه را با «آزمون زمان‌دار» بگیر."), days=[
    (cell("اصل جمع و ضرب، جایگشت", "G3:1"),
     cell("آرایه و لیست پیوندی", "D2:1"),
     cell("بازگشت و ردگیری فراخوانی", "C4:1")),
    (cell("ترکیب، جایگشت با تکرار، ضرایب دوجمله‌ای", "G3:1,5"),
     cell("پشته، صف، تبدیل میانوندی به پسوندی", "D2:2-3 D2:x"),
     cell("بازگشت: هانوی، فیبوناچی، شمردن فراخوانی", "C4:2 C4:x", tag=EVEN)),
    (cell("توزیع اشیا در جعبه، جواب صحیح معادله", "G3:2"),
     cell("درهم‌سازی: زنجیره، آدرس‌دهی باز", "D3:1-3 D3:x"),
     NOB),
    (cell("لانهٔ کبوتری", "G3:3"),
     cell("هیپ و صف اولویت، build-heap", "D4:4"),
     cell("رشته و آرایهٔ دوبعدی", "C5:3-4 C5:x")),
    (cell("شمول و عدم شمول، پریش", "G3:4"),
     cell("درخت دودویی، BST، پیمایش‌ها", "D4:1-2"),
     cell("struct، حافظهٔ پویا، ارسال با مقدار و آدرس", "C6:1-4 C3:2")),
    (cell("تست ترکیبی شمارش", "G3:x"),
     cell("AVL + تست ترکیبی", "D4:3,5 D4:x"),
     cell("تست جمع‌بندی برنامه‌سازی", "C6:x")),
]))
W.append(dict(title="بازگشتی، روابط، اعداد، گراف · مرتب‌سازی تا حریصانه · زبان منظم", note=(
    "ریاضی این هفته چهار فصل کوتاه گسسته را می‌بندد؛ چهارشنبه دو فصل (ترتیب جزئی + نظریهٔ اعداد) است، "
    "پس نظریهٔ اعداد را فقط در حد سه درس کوتاهش بخوان."), days=[
    (cell("روابط بازگشتی خطی همگن", "G4:1-2"),
     cell("مرتب‌سازی درجی، انتخابی، حبابی (جدول اصلی)", "D5:1"),
     cell("زبان، الفبا، عبارت منظم", "T1:1-2")),
    (cell("رابطهٔ بازگشتی ناهمگن", "G4:3"),
     cell("ادغامی و سریع، بهترین و بدترین حالت", "D5:2"),
     cell("DFA", "T1:3", tag=EVEN)),
    (cell("توابع مولد", "G4:4 G4:x"),
     cell("heap sort، کران پایین، مرتب‌سازی خطی", "D5:3-4 D5:x"),
     NOB),
    (cell("روابط: بازتابی، تقارنی، تعدی، هم‌ارزی", "G5:1-3"),
     cell("جستجوی دودویی، انتخاب k‌ام، میانهٔ میانه‌ها", "D6:1-4 D6:x"),
     cell("NFA و تبدیل به DFA", "T1:3")),
    (cell("ترتیب جزئی، هاسه، مشبکه + نظریهٔ اعداد", "G5:4 G5:x G6:1-3 G6:x"),
     cell("تقسیم و حل (و جریان بیشینه در حد تست)", "D7:1-2"),
     cell("عبارت منظم ↔ ماشین", "T1:2-3")),
    (cell("نظریهٔ گراف: اویلری، همیلتونی، رنگ‌آمیزی، مسطح", "G7:1-4 G7:x"),
     cell("حریصانه: انتخاب فعالیت، هافمن", "D7:3-5 D7:x"),
     cell("کمینه‌سازی DFA، مایهیل-نرود", "T1:4 T1:x")),
]))
W.append(dict(title="احتمال گسسته · گراف، پویا و NP · زبان منظم", note=(
    "<b>نقطهٔ کنترل ۱: جمعه ۱۳ آذر.</b> اگر کمتر از ۷۰٪ بلوک‌ها انجام شده یا میانگین آزمون زیر ۳۰٪ است، "
    "دامنه کوچک می‌شود (بخش «قواعد» را ببین)."), days=[
    (cell("فضای نمونه، اصول احتمال", "P1:2"),
     cell("نمایش گراف، BFS، DFS", "D8:1"),
     cell("تشخیص منظم و غیرمنظم", "T2:2", note="لم تزریق در کتاب به‌صورت الگوی «حافظهٔ متناهی» آمده؛ برای اثبات رسمی بپرس.")),
    (cell("احتمال شرطی و استقلال", "P1:2-3"),
     cell("مرتب‌سازی توپولوژیک، مؤلفهٔ قویاً همبند", "D8:1"),
     cell("تشخیص نوع زبان (ادامه)", "T2:2 T1:4", tag=EVEN)),
    (cell("احتمال کل و بیز", "P1:3 P1:x"),
     cell("دایکسترا، بلمن-فورد، فلوید", "D8:3"),
     NOB),
    (cell("متغیر تصادفی گسسته، امید و واریانس", "P2:1"),
     cell("MST (کراسکال، پریم) + جریان بیشینه", "D8:2,4 D8:5 D8:x"),
     cell("خواص بستاری", "T2:1")),
    (cell("برنولی، دوجمله‌ای، هندسی، پواسون", "P2:2"),
     cell("پویا: LCS، کوله‌پشتی، ضرب زنجیره‌ای", "D9:1-2 D9:x"),
     cell("تست ترکیبی زبان منظم", "T1:x", note="دور دوم آزمون فصل ۱ + «آزمون زمان‌دار: زبان منظم»")),
    (cell("فوق‌هندسی، دوجمله‌ای منفی + تست", "P2:2"),
     cell("عقبگرد، شاخه و حد، P و NP", "D10:1-4 D10:x"),
     cell("تست ترکیبی بستاری و تشخیص نوع", "T2:x")),
]))
W.append(dict(title="احتمال پیوسته · مدار ترکیبی · مستقل از متن و تورینگ", note=(
    "تابع مولد گشتاور در کتاب احتمال نیامده (در کنکورهای ۱۳۹۸ تا ۱۴۰۴ سؤال مستقیم نداشته)؛ "
    "اگر خواستی بگو «درس کوتاه: تابع مولد گشتاور»."), days=[
    (cell("متغیر پیوسته، چگالی، تابع توزیع", "P2:3"),
     cell("مبناها، مکمل ۱ و ۲، کد گری، BCD", "M1:1"),
     cell("CFG و اشتقاق", "T3:1")),
    (cell("یکنواخت، نمایی (بی‌حافظگی)، نرمال", "P2:3"),
     cell("جبر بول، مینترم و ماکسترم", "M1:2"),
     cell("ابهام، ساده‌سازی، فرم نرمال چامسکی", "T3:2-3", tag=EVEN)),
    (cell("امید و واریانس (مرور با پیوسته‌ها)", "P2:1 P2:x"),
     cell("جدول کارنو، حالت‌های بی‌اهمیت", "M1:3"),
     NOB),
    (cell("توزیع توأم، حاشیه‌ای، شرطی", "P3:1"),
     cell("مخاطره، پیاده‌سازی با NAND و NOR", "M1:2,4 M1:x"),
     cell("اتوماتون پشته‌ای (PDA)", "T3:4 T3:x")),
    (cell("کوواریانس، همبستگی، تبدیل متغیر", "P3:2 P2:3"),
     cell("MUX، دیکدر، جمع‌کننده، مقایسه‌گر", "M2:1-3"),
     cell("بستاری و تشخیص زبان مستقل از متن", "T2:1-2")),
    (cell("حد مرکزی، چبیشف + تست", "P3:3 P3:x"),
     cell("تأخیر گیت + تست ترکیبی", "M2:4 M2:x"),
     cell("تورینگ، تصمیم‌پذیری، سلسله‌مراتب چامسکی", "T4:1-4 T2:3 T4:x")),
]))
W.append(dict(title="آمار استنباطی · مدار ترتیبی · جستجو در هوش", note=(
    "آمار استنباطی ۱۰ سؤال در ۷ سال داشته؛ با اینکه فرعی به نظر می‌رسد، کامل بخوان. "
    "همهٔ مسائلش با یک فرمول حل می‌شوند، پس امتیاز به ازای ساعت بالاست."), days=[
    (cell("آمار توصیفی", "P1:1"),
     cell("لچ و فلیپ‌فلاپ، جدول تحریک", "M3:1"),
     cell("عامل و محیط، BFS، DFS، UCS، IDS", "H1:1")),
    (cell("توزیع نمونه‌ای، t و χ²", "P4:2 P3:3"),
     cell("تحلیل مدار ترتیبی", "M3:2"),
     cell("جستجوی حریصانه و A*", "H1:2", tag=EVEN)),
    (cell("برآورد: نااریبی، درست‌نمایی", "P4:1"),
     cell("طراحی مدار ترتیبی، شمارنده‌ها", "M3:3 M3:x"),
     NOB),
    (cell("فاصلهٔ اطمینان", "P4:2"),
     cell("ماشین میلی و مور، کمینه‌سازی حالت", "M4:1-2"),
     cell("قابل قبول و سازگار بودن هیوریستیک", "H1:2")),
    (cell("آزمون فرض، خطای نوع ۱ و ۲", "P4:3"),
     cell("ROM، PLA، PAL، Verilog", "M4:3-4 M4:x"),
     cell("تست جستجو", "H1:x")),
    (cell("ANOVA و رگرسیون + تست", "P4:4 P4:x"),
     cell("تست ترکیبی مدار منطقی", note="«آزمون زمان‌دار: مدار منطقی ۲۰»"),
     cell("تست جستجو", note="«آزمون زمان‌دار: جستجو ۱۵»")),
]))
W.append(dict(title="جبر خطی ۱ · محاسبات کامپیوتری · خصمانه و CSP", note=(
    "کتاب جبر خطی (۰۳) تا ۲۶ آذر آماده و فرستاده می‌شود. فصل ۱: دستگاه، ماتریس، دترمینان؛ "
    "فصل ۲: فضای برداری، پایه، بعد، رتبه."), days=[
    (cell("دستگاه معادلات، حذف گاوسی", "L1"),
     cell("واحد حسابی، اعداد علامت‌دار، سرریز، بیت‌های وضعیت", "R1:1-2"),
     cell("مینیمکس", "H2:2")),
    (cell("ماتریس، وارون، ماتریس‌های خاص", "L1"),
     cell("ضرب و الگوریتم بوث", "R1:3"),
     cell("هرس آلفا-بتا", "H2:2", tag=EVEN)),
    (cell("دترمینان", "L1"),
     cell("تقسیم", "R1:3"),
     NOB),
    (cell("فضای برداری، زیرفضا", "L2"),
     cell("ممیز شناور IEEE 754", "R1:4 R1:x"),
     cell("جستجوی محلی: تپه‌نوردی، SA، ژنتیک", "H2:1 H2:x")),
    (cell("استقلال خطی، پایه، بعد", "L2"),
     cell("قالب دستور و شیوه‌های آدرس‌دهی", "R2:1-2"),
     cell("CSP: عقبگرد، MRV، forward checking", "H3:1,3")),
    (cell("رتبه، فضای پوچی، قضیهٔ رتبه + تست", "L2"),
     cell("کارایی، CPI، آمدال + تست", "R3:1"),
     cell("AC-3 و ساختار گراف + تست CSP", "H3:2,4 H3:x")),
]))
W.append(dict(title="جبر خطی ۲ · مسیر داده، خط لوله و نهان · منطق و احتمال در هوش", note=(
    "MDP و یادگیری تقویتی در کتاب هوش نیامده، چون در هفت سال فقط ۱ سؤال (۱۴۰۰) داشته. "
    "بلوک چهارشنبه را تست هوش بزن یا بگو «درس کوتاه: MDP»."), days=[
    (cell("تبدیل خطی و ماتریس آن", "L3"),
     cell("انتقال ثبات و مسیر داده", "R2:3"),
     cell("منطق گزاره‌ای و رزولوشن", "H4:1")),
    (cell("مقادیر و بردارهای ویژه", "L3"),
     cell("واحد کنترل سخت‌افزاری", "R2:4"),
     cell("منطق مرتبهٔ اول", "H4:2", tag=EVEN)),
    (cell("قطری‌سازی، کیلی-همیلتون", "L3"),
     cell("ریزبرنامه‌نویسی", "R2:4 R2:x"),
     NOB),
    (cell("ضرب داخلی، تعامد، گرام-اشمیت", "L4"),
     cell("خط لوله و مخاطرات", "R3:2"),
     cell("احتمال و شبکهٔ بیزی", "H4:3")),
    (cell("ماتریس متقارن، معین مثبت، SVD", "L4"),
     cell("حافظهٔ نهان: نگاشت و جایگزینی", "R3:3"),
     cell("MDP و یادگیری تقویتی", note="در کتاب نیست؛ به‌جایش «آزمون زمان‌دار: هوش ۱۵»")),
    (cell("تست ترکیبی جبر خطی", "L4"),
     cell("زمان دسترسی حافظه + تست معماری", "R3:3 R3:x"),
     cell("بیز ساده + تست", "H4:4 H4:x")),
]))
W.append(dict(title="تست ریاضی و رفع ضعف · سیستم‌عامل فشرده · تست مرور", note=(
    "هفته‌های ۹ و ۱۰ دفترچه اینجا یکی شده‌اند. ریاضی درس‌نامهٔ تازه ندارد: بلوک صبح = رفع ضعف از دفتر خطا، "
    "بلوک تست = تست زمان‌دار. سیستم‌عامل هر روز یک فصل یا نیم‌فصل است (فصل‌هایش کوتاه‌اند). "
    "<b>نقطهٔ کنترل ۲: جمعه ۱۸ دی؛ دور اول همهٔ درس‌ها تمام می‌شود.</b>"), days=[
    (cell("رفع ضعف ۱ (ضعیف‌ترین مبحث دفتر خطا) + تست گسسته"),
     cell("مفاهیم پایه، فرایند، fork، ریسمان", "O1:1-3 O1:x"),
     cell("تست برنامه‌سازی")),
    (cell("رفع ضعف ۲ + تست احتمال"),
     cell("زمان‌بندی پردازنده و بی‌درنگ", "O2:1-2 O2:x"),
     cell("تست زبان منظم و مستقل از متن", tag=EVEN)),
    (cell("رفع ضعف ۳ + تست جبر خطی"),
     cell("ناحیهٔ بحرانی، سمافور، مانیتور", "O3:1-2"),
     NOB),
    (cell("تست ترکیبی هر سه درس + تست شمارش"),
     cell("بن‌بست و بانکدار", "O3:3 O3:x"),
     cell("تست تورینگ و ترکیبی نظریه")),
    (cell("رفع ضعف ۴ + تست آمار"),
     cell("صفحه‌بندی و TLB", "O4:1-2"),
     cell("تست جستجو و خصمانه")),
    (cell("تست ترکیبی زمان‌دار ریاضی"),
     cell("حافظهٔ مجازی، جایگزینی صفحه، دیسک، RAID + تست", "O4:3-4 O4:x"),
     cell("تست CSP، منطق و ترکیبی هوش")),
]))

# ---------------------------------------------------------------- فاز ۲ و ۳
P2 = [
    dict(title="فاز ۲ · هفتهٔ ۱", cols=("ریاضی (۲ بلوک)", "تخصصی (۲ بلوک صبح)", "بلوک عصر"), rows=[
        ("تست گسسته", "ساختمان داده و الگوریتم", "سیستم‌عامل"),
        ("تست احتمال", "ساختمان داده و الگوریتم", "سیستم‌عامل (" + EVEN + ")"),
        ("تست جبر خطی", "مدار منطقی", "الگوریتم (بعد از کلاس)"),
        ("<b>آزمون جامع ۱</b> (۸ تا ۱۲)", "—", "تحلیل کامل آزمون (۱۴ تا ۱۷)"),
        ("تست گسسته", "معماری", "سیستم‌عامل"),
        ("تست آمار", "مدار منطقی + معماری", "نقاط ضعف دفتر خطا"),
        ("<b>آزمون جامع ۲</b> (۸ تا ۱۲) + تحلیل", "", ""),
    ], note="از ۱۹ دی درس‌نامهٔ تازه و منبع تازه نداری؛ همهٔ بلوک‌ها تست زمان‌دار + تحلیل است."),
    dict(title="فاز ۲ · هفتهٔ ۲", cols=("ریاضی (۲ بلوک)", "تخصصی (۲ بلوک صبح)", "بلوک عصر"), rows=[
        ("تست احتمال", "نظریهٔ زبان‌ها", "هوش مصنوعی"),
        ("تست جبر خطی", "نظریهٔ زبان‌ها", "هوش (" + EVEN + ")"),
        ("تست گسسته", "برنامه‌سازی", "الگوریتم"),
        ("<b>آزمون جامع ۳</b>", "—", "تحلیل کامل"),
        ("ضعیف‌ترین مبحث ریاضی", "هوش مصنوعی", "نقاط ضعف تخصصی"),
        ("دومین مبحث ضعیف ریاضی", "ضعیف‌ترین درس تخصصی", "دفتر خطا"),
        ("<b>آزمون جامع ۴</b> + تحلیل", "", ""),
    ], note="<b>ساعت بدن:</b> از شنبه ۲۶ دی هر هفته ۲۵ دقیقه زودتر بخواب و بیدار شو تا در هفتهٔ آزمون "
            "بیداری ۵:۴۵ طبیعی باشد."),
    dict(title="فاز ۳ · جمع‌بندی", cols=("صبح (۸ تا ۱۲)", "عصر"), rows=[
        ("<b>آزمون جامع ۵</b>", "تحلیل"),
        ("رفع ضعف ریاضی (هفتهٔ فرد: کلاس ۸ تا ۱۰)", "برگهٔ خلاصهٔ گسسته، احتمال، جبر خطی"),
        ("رفع ضعف تخصصی", "کلاس + برگهٔ خلاصهٔ ساختمان داده، مدار، معماری"),
        ("<b>آزمون جامع ۶</b>", "تحلیل"),
        ("رفع ضعف", "برگهٔ خلاصهٔ سیستم‌عامل، نظریه، هوش، برنامه‌سازی"),
        ("<b>آزمون جامع ۷</b>", "تحلیل"),
        ("مرور دفتر خطا (۳ ساعت)", "استراحت"),
    ], note="کار شرکت روزی ۱ ساعت (۲۰ تا ۲۱)، پایان‌نامه متوقف. برگهٔ خلاصه = یک صفحهٔ A4 برای هر درس، "
            "از روی کارت‌های خلاصهٔ کتاب‌ها و دفتر خطا."),
]
EXAM_WEEK = [
    "<b>آزمون جامع ۸ (آخرین)</b> + تحلیل",
    "برگه‌های خلاصهٔ ریاضی + ۳۰ تست سبک",
    "برگه‌های خلاصهٔ تخصصی + پرینت کارت ورود به جلسه",
    "کل دفتر خطا",
    "سبک: فقط فرمول‌ها و کارت‌های خلاصه، تا ساعت ۱۶",
    "هیچ مطلب تازه‌ای نه. رفتن به حوزه برای دانستن مسیر، آماده کردن وسایل، خواب ۲۲:۳۰",
    "<b>آزمون</b>",
]

# ---------------------------------------------------------------- تاریخ
MONTHS = [("آبان", 30), ("آذر", 30), ("دی", 30), ("بهمن", 30)]
WD = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"]
START_DAY = 16  # شنبه ۱۶ آبان ۱۴۰۵


def jd(off: int):
    d, m = START_DAY + off, 0
    while d > MONTHS[m][1]:
        d -= MONTHS[m][1]
        m += 1
    return d, MONTHS[m][0]


def dstr(off: int, wd=True) -> str:
    d, m = jd(off)
    return f"{WD[off % 7]} {fa(d)} {m}" if wd else f"{fa(d)} {m}"


def wrange(w: int) -> str:
    a, b = jd(7 * w), jd(7 * w + 6)
    return f"{fa(a[0])} {a[1]} تا {fa(b[0])} {b[1]}" if a[1] != b[1] else f"{fa(a[0])} تا {fa(b[0])} {b[1]}"


# ---------------------------------------------------------------- HTML
CSS = """
@page{size:A4;margin:12mm 12mm 13mm}
*{box-sizing:border-box}
body{font-family:Vazirmatn;color:#1d2433;font-size:9.6pt;line-height:1.75;margin:0;direction:rtl}
.sec{break-after:page;position:relative}
.sec:last-child{break-after:auto}
.mk{position:absolute;top:0;left:0;font-size:1.5px;color:#fff}
h1{font-size:22pt;margin:0}
h2{font-size:14pt;margin:0 0 4pt}
h3{font-size:11pt;margin:10pt 0 4pt;color:#283593;border-right:4px solid #283593;padding-right:7px}
.band{background:linear-gradient(135deg,#1a237e,#3949ab);color:#fff;border-radius:12px;padding:12px 16px;
 margin-bottom:9pt;display:flex;align-items:center;gap:14px}
.band .wn{font-size:30pt;font-weight:900;line-height:1;min-width:48px;text-align:center}
.band .wt{font-size:13pt;font-weight:800}
.band .wd{font-size:9.5pt;opacity:.9}
.band.p2{background:linear-gradient(135deg,#4a148c,#7b1fa2)}
.band.p3{background:linear-gradient(135deg,#b71c1c,#e53935)}
.wnote{background:#fff8e1;border:1px solid #ffe082;border-radius:8px;padding:6px 10px;margin-bottom:8pt;font-size:9pt}
table{width:100%;border-collapse:separate;border-spacing:0;font-size:8.9pt}
th{background:#283593;color:#fff;font-weight:700;padding:5px 6px;text-align:right}
th:first-child{border-top-right-radius:8px}th:last-child{border-top-left-radius:8px}
td{border-bottom:1px solid #e2e6ee;padding:5px 6px;vertical-align:top}
tr:nth-child(even) td{background:#f7f8fc}
td.day{width:70px;font-weight:800;white-space:nowrap;color:#283593}
td.day small{display:block;font-weight:500;color:#6b7385}
td.chk{width:56px;text-align:center;color:#9aa3b5;font-size:11pt;letter-spacing:1px}
.topic{font-weight:700;line-height:1.5}
.tag{display:inline-block;font-size:7.4pt;font-weight:600;background:#e8eaf6;color:#3949ab;border-radius:9px;
 padding:0 6px;margin-right:4px}
.ref{display:block;font-size:7.8pt;color:#3b4255;border-right:3px solid var(--rc);background:#fff;
 border-radius:4px;padding:0 5px;margin-top:2px;line-height:1.6}
.ref b{color:var(--rc)}
.ref i{color:#b26a00;font-style:normal}
.note{font-size:7.8pt;color:#8a5a00;margin-top:2px}
.nob{color:#9aa3b5;font-size:8.2pt}
tr.fri td{background:#eef7ee!important}
.legend{font-size:8.3pt;color:#4a5263;margin-top:6pt}
.cover{height:265mm;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;
 background:radial-gradient(circle at 30% 20%,#5c6bc0,#1a237e 70%);color:#fff;border-radius:18px}
.cover .big{font-size:40pt;font-weight:900;line-height:1.2}
.cover .sub{font-size:14pt;margin-top:8pt;opacity:.95}
.cover .pill{margin-top:22pt;background:rgba(255,255,255,.15);border-radius:30px;padding:8px 22px;font-size:12pt}
.cover .ft{margin-top:40pt;font-size:10pt;opacity:.8}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:9pt}
.dayp{font-size:8.6pt;line-height:1.55}.dayp td{padding:3px 6px}.dayp .card{padding:6px 10px}
.card{border:1px solid #e2e6ee;border-radius:10px;padding:8px 11px;background:#fbfcfe}
.card h4{margin:0 0 3pt;font-size:10.5pt;color:#283593}
ul{margin:2pt 0;padding-right:16px}li{margin:1pt 0}
.ph{display:inline-block;border-radius:6px;padding:0 7px;font-size:8pt;font-weight:700;color:#fff}
.ph1{background:#3949ab}.ph2{background:#7b1fa2}.ph3{background:#e53935}.ph4{background:#2e7d32}
.cp td{background:#fff3e0!important}
code{font-family:'JB Mono',CodeFA,monospace;font-size:8.5pt;background:#eef1f7;border-radius:4px;padding:0 4px;
 direction:ltr;unicode-bidi:isolate}
"""


def mk(i):
    return f'<span class="mk">@@{i}@@</span>'


def cover():
    return f"""<section class="sec">{mk('cover')}<div class="cover">
<div style="font-size:12pt;opacity:.85">کنکور دکتری ۱۴۰۶ · مجموعهٔ ۲۳۵۴</div>
<div class="big">برنامهٔ مطالعه<br>۹۱ روز تا آزمون</div>
<div class="sub">شروع دوباره: <b>شنبه ۱۶ آبان ۱۴۰۵</b> · آزمون: <b>جمعه ۱۶ بهمن ۱۴۰۵</b></div>
<div class="pill">هر روز: کدام کتاب، کدام فصل، کدام درس، کدام صفحه</div>
<div class="ft">بر پایهٔ دفترچهٔ راهنمای اجرای برنامه · ساعت‌ها از tutor/schedule.md</div>
</div></section>"""


def overview():
    rows = []
    for i, w in enumerate(W):
        rows.append(f'<tr{" class=cp" if i in (3, 8) else ""}><td class="day">هفتهٔ {fa(i + 1)}</td>'
                    f'<td>{wrange(i)}</td><td><span class="ph ph1">فاز ۱</span></td><td>{w["title"]}'
                    f'{"<br><b>نقطهٔ کنترل " + ("۱" if i == 3 else "۲") + ": جمعه " + dstr(7 * i + 6, False) + "</b>" if i in (3, 8) else ""}'
                    f'</td></tr>')
    extra = [(9, "ph2", "فاز ۲", "تست زمان‌دار درس‌به‌درس + آزمون جامع ۱ و ۲"),
             (10, "ph2", "فاز ۲", "تست زمان‌دار + آزمون جامع ۳ و ۴"),
             (11, "ph3", "فاز ۳", "آزمون جامع ۵ تا ۷ + برگه‌های خلاصه"),
             (12, "ph4", "هفتهٔ آزمون", "آزمون جامع ۸، مرور سبک، آزمون جمعه ۱۶ بهمن")]
    for i, c, p, t in extra:
        rows.append(f'<tr><td class="day">هفتهٔ {fa(i + 1)}</td><td>{wrange(i)}</td>'
                    f'<td><span class="ph {c}">{p}</span></td><td>{t}</td></tr>')
    return f"""<section class="sec">{mk('overview')}
<h2>نقشهٔ ۱۳ هفته</h2>
<table><tr><th>هفته</th><th>تاریخ</th><th>فاز</th><th>محتوا</th></tr>{''.join(rows)}</table>
<div class="grid" style="margin-top:10pt">
<div class="card"><h4>چه چیزی نسبت به دفترچه عوض شد؟</h4><ul>
<li>هفتهٔ ۱ دفترچه (۹ تا ۱۵ آبان) انجام نشد؛ پس <b>فاز ۱ از ۱۶ آبان از اول</b> شروع می‌شود.</li>
<li>هفته‌های ۱ تا ۸ دفترچه دقیقاً همان مبحث‌ها را دارند، فقط یک هفته جلوتر.</li>
<li>هفته‌های ۹ و ۱۰ دفترچه (سیستم‌عامل + تست مرور) در هفتهٔ ۹ ادغام شدند تا <b>فاز ۲، فاز ۳ و هفتهٔ آزمون دست نخورند</b> (۸ آزمون جامع حفظ شد).</li>
<li>تاریخ‌های نقاط کنترل: جمعه ۱۳ آذر و جمعه ۱۸ دی.</li>
</ul></div>
<div class="card"><h4>منبع تست‌ها</h4><ul>
<li><b>آزمون فصل کتاب‌ها:</b> سؤال‌های ارشد ۱۳۹۸ تا ۱۴۰۴ (۳ تا ۱۶ سؤال در هر فصل).</li>
<li><b>حجم بیشتر:</b> به Claude بگو <code>آزمون زمان‌دار: مبحث تعداد</code>.</li>
<li><b>آزمون‌های جامع فاز ۲ و ۳:</b> چون ۱۳۹۸ تا ۱۴۰۴ در کتاب‌ها آمده، از دفترچه‌های ارشد <b>۱۳۹۷، ۱۳۹۶، ۱۳۹۵ …</b> (پوشهٔ <code>exam/</code>) ساخته می‌شوند؛ آزمون جامع ۸ از <b>دکتری ۱۴۰۳</b>، یعنی همین مجموعه. Claude هر آزمون را پیش از موعد آماده می‌کند.</li>
</ul></div></div>
</section>"""


def day_page():
    return f"""<section class="sec dayp">{mk('day')}
<h2>یک روز معمولی</h2>
<table><tr><th>ساعت</th><th>بلوک</th><th>کار</th></tr>
<tr><td class="day">۰۷:۰۰</td><td>صبح</td><td>بیداری، صبحانه، ۱۰ دقیقه لغت</td></tr>
<tr><td class="day">۰۸:۰۰</td><td><b>ریاضی: درس‌نامه</b></td><td>ستون «ریاضی» در جدول هفته (تا ۰۹:۳۰؛ ۱۵ دقیقه استراحت بدون گوشی)</td></tr>
<tr><td class="day">۰۹:۴۵</td><td><b>تخصصی A: درس‌نامه</b></td><td>ستون «تخصصی A» (تا ۱۱:۱۵؛ ۱۵ دقیقه استراحت)</td></tr>
<tr><td class="day">۱۱:۳۰</td><td>تست ریاضی کوتاه</td><td>۱۰ تا ۱۲ تست زمان‌دار همان مبحث صبح (تا ۱۲:۱۵)</td></tr>
<tr><td class="day">۱۲:۱۵</td><td>ناهار</td><td>+ ۲۰ دقیقه چرت؛ بدون صفحه‌نمایش</td></tr>
<tr><td class="day">۱۴:۰۰</td><td><b>تخصصی A: تست</b></td><td>۱۵ تا ۲۰ تست زمان‌دار همان مبحث + تحلیل</td></tr>
<tr><td class="day">۱۵:۴۵</td><td><b>تخصصی B</b></td><td>ستون «تخصصی B»: نیم درس‌نامه، نیم تست</td></tr>
<tr><td class="day">۱۷:۱۵</td><td>مرور</td><td>کارت خلاصهٔ ۱، ۳ و ۷ روز پیش · دفتر خطا · «پایان جلسه» (تا ۱۷:۴۵)</td></tr>
<tr><td class="day">۱۷:۴۵</td><td>پیاده‌روی</td><td>۳۰ دقیقه؛ بعد شام و استراحت تا ۲۰:۰۰، بدون درس</td></tr>
<tr><td class="day">۲۰ تا ۲۲</td><td>کار شرکت</td><td>سقف سخت: ۲۲:۰۰</td></tr>
<tr><td class="day">۲۲:۰۰</td><td>زبان</td><td>۲۰ لغت + لایتنر؛ سه‌شنبه و پنجشنبه درک مطلب · خواب ۲۳:۳۰</td></tr></table>
<div class="grid" style="margin-top:9pt">
<div class="card"><h4>روزهای خاص</h4><ul>
<li><b>یکشنبهٔ فرد:</b> ۸ تا ۱۰ کلاس · ۱۰:۱۵ ریاضی درس‌نامه · ۱۲ تا ۱۳ جلسهٔ کار · ۱۳:۱۵ استاد راهنما · ۱۴:۴۵ تخصصی A درس‌نامه · ۱۶:۳۰ تخصصی A تست کوتاه · ۱۷:۳۰ مرور (تست ریاضی و B ندارد).</li>
<li><b>یکشنبهٔ زوج:</b> صبح عادی · ۱۱:۱۵ مرور و رفتن به جلسه · ۱۲ تا ۱۳ جلسهٔ کار · ۱۴:۰۰ تخصصی A تست · ۱۵:۴۵ B · ۱۷:۱۵ تست ریاضی کوتاه.</li>
<li><b>دوشنبه:</b> صبح عادی · ۱۴ تا ۱۶ کلاس الگوریتم · ۱۶:۱۵ تخصصی A تست · ۱۷:۴۵ مرور (B ندارد).</li>
<li><b>جمعه:</b> ۸ تا ۱۱ آزمون هفتگی · ۱۱:۱۵ تحلیل و دفتر خطا · ۱۴ تا ۱۶ پایان‌نامه و مقاله · از ۱۶ آزاد · ۲۲:۰۰ جدول هفتگی.</li>
<li><b>روز سخت (کار سنگین یا خستگی):</b> «حالت حداقل» = فقط درس ریاضی و درس تخصصی A همان روز، هر کدام ۴۵ تا ۹۰ دقیقه. تست‌ها و B بدهی می‌شوند. روز حداقل، روز شکست نیست.</li>
<li><b>بیماری:</b> استراحت؛ فقط اگر حالت خوب بود، ۱۰ دقیقه کارت خلاصه. بعد از خوب شدن، از روز جاری برنامه ادامه بده، نه از عقب.</li>
</ul></div>
<div class="card"><h4>بلوک یادگیری (۹۰ دقیقه) = یک درس کتاب</h4><ul>
<li><b>۰–۱۰ پیش‌آزمون:</b> ۲ سؤال از آزمون همان فصل.</li>
<li><b>۱۰–۵۵ درس‌نامه:</b> هر جعبهٔ ✏️ مثال را بپوشان و در دفتر حل کن؛ قبل از هر ⚠️ تله حدس بزن.</li>
<li><b>۵۵–۸۰ تمرین ✍️</b> بدون پاسخ‌نامه.</li>
<li><b>۸۰–۹۰ کتاب بسته:</b> ۳ خط + فرمول‌ها، و مقایسه با کارت خلاصه.</li>
</ul></div>
<div class="card"><h4>بلوک تست</h4><ul>
<li>حداکثر ۴ دقیقه هر تست؛ کنار هر جواب ✓ (مطمئن) یا ? (حدسی).</li>
<li>نمره = (۳ × درست − غلط) ÷ (۳ × کل).</li>
<li>همهٔ تست‌ها حتی درست‌های حدسی تحلیل؛ هر غلط یا حدسی یک سطر دفتر خطا (مفهوم / دقت / زمان).</li>
</ul></div>
<div class="card"><h4>جدول هفته را چطور بخوانم؟</h4><ul>
<li>هر خانه = مبحث <b>یادگیری</b> صبح؛ بلوک تست همان روز روی همان مبحث است.</li>
<li>زیر هر مبحث: کتاب · فصل · درس · <b>صفحه</b>. «آزمون فصل» یعنی کارت‌های سؤال آخر فصل.</li>
<li>ستون ✓: هر بلوک انجام‌شده را علامت بزن (۵ بلوک در روز). هدف هفته: ۲۴ از ۲۸.</li>
<li>شب قبل فقط ردیف فردا را بخوان و کتاب‌ها را باز بگذار؛ صبح بدون تصمیم‌گیری شروع کن.</li>
</ul></div></div>
</section>"""


def week_page(i, w):
    rows = []
    for d, (m, a, b) in enumerate(w["days"]):
        off = 7 * i + d
        dd, mm = jd(off)
        rows.append(f'<tr><td class="day">{WD[d]}<small>{fa(dd)} {mm}</small></td><td>{m}</td><td>{a}</td>'
                    f'<td>{b}</td><td class="chk">☐☐☐<br>☐☐</td></tr>')
    dd, mm = jd(7 * i + 6)
    cp = ""
    if i == 3:
        cp = " · <b>نقطهٔ کنترل ۱</b>"
    if i == 8:
        cp = " · <b>نقطهٔ کنترل ۲</b>"
    rows.append(f'<tr class="fri"><td class="day">جمعه<small>{fa(dd)} {mm}</small></td><td colspan="4">'
                f'۸ تا ۱۱ <b>آزمون هفتگی</b> («آزمون هفتگی» به Claude) · ۱۱:۱۵ تحلیل و دفتر خطا · ۱۴ تا ۱۶ پایان‌نامه و مقاله · '
                f'۲۲:۰۰ جدول هفتگی{cp}</td></tr>')
    return f"""<section class="sec">{mk(f'w{i + 1}')}
<div class="band"><div class="wn">{fa(i + 1)}</div><div><div class="wt">هفتهٔ {fa(i + 1)} · {w['title']}</div>
<div class="wd">{wrange(i)} · فاز ۱</div></div></div>
<div class="wnote">{w['note']}</div>
<table><tr><th>روز</th><th>ریاضی (۰۸:۰۰ + تست ۱۱:۳۰)</th><th>تخصصی A (۰۹:۴۵ + تست ۱۴:۰۰)</th>
<th>تخصصی B (۱۵:۴۵)</th><th>✓</th></tr>{''.join(rows)}</table>
<div class="legend">«{EVEN}»: در یکشنبهٔ فرد کلاس داری و بلوک B نیست؛ آن مبحث را فقط با تست، در بلوک B روز بعدی که خالی است جبران کن.</div>
</section>"""


def p2_page():
    out = []
    for k, w in enumerate(P2):
        wi = 9 + k
        cols = "".join(f"<th>{c}</th>" for c in w["cols"])
        rows = []
        for d, r in enumerate(w["rows"]):
            dd, mm = jd(7 * wi + d)
            cls = ' class="fri"' if d == 6 else ""
            if d == 6 and not any(r[1:]):
                cells = f'<td colspan="{len(w["cols"])}">{r[0]}</td>'
            else:
                cells = "".join(f"<td>{c}</td>" for c in r)
            rows.append(f'<tr{cls}><td class="day">{WD[d]}<small>{fa(dd)} {mm}</small></td>{cells}</tr>')
        band = "p3" if k == 2 else "p2"
        out.append(f"""<div class="band {band}">
<div class="wn">{fa(wi + 1)}</div><div><div class="wt">هفتهٔ {fa(wi + 1)} · {w['title']}</div>
<div class="wd">{wrange(wi)}</div></div></div><div class="wnote">{w['note']}</div>
<table><tr><th>روز</th>{cols}</tr>{''.join(rows)}</table>""")
    first = (f'<section class="sec">{mk("p2")}{out[0]}</section>'
             f'<section class="sec">{mk("p2b")}{out[1]}</section>')
    rows = []
    for d, t in enumerate(EXAM_WEEK):
        dd, mm = jd(7 * 12 + d)
        rows.append(f'<tr{" class=fri" if d == 6 else ""}><td class="day">{WD[d]}<small>{fa(dd)} {mm}</small></td>'
                    f'<td>{t}</td></tr>')
    second = f"""<section class="sec">{mk('p3')}{out[2]}</section>
<section class="sec">{mk('p4')}
<div class="band p3" style="background:linear-gradient(135deg,#1b5e20,#43a047)"><div class="wn">۱۳</div>
<div><div class="wt">هفتهٔ ۱۳ · هفتهٔ آزمون</div><div class="wd">{wrange(12)}</div></div></div>
<table><tr><th>روز</th><th>کار</th></tr>{''.join(rows)}</table>
<div class="card" style="margin-top:9pt"><h4>روز آزمون</h4><ul>
<li>☐ کارت ورود به جلسهٔ چاپی + کارت ملی و هر چیزی که راهنمای آزمون می‌خواهد.</li>
<li>☐ بیداری ۵:۴۵، صبحانهٔ همیشگی، رسیدن ۴۵ دقیقه زودتر.</li>
<li>☐ دور اول فقط سؤال‌های مطمئن؛ دور دوم سؤال‌هایی که دو گزینه‌شان رد می‌شود؛ بقیه سفید.</li>
<li>☐ ترتیب همان آزمون‌های جامع: اول ریاضی، بعد تخصصی، زبان آخر. روز آزمون هیچ روش تازه‌ای امتحان نمی‌شود.</li>
</ul></div></section>"""
    return first + second


def rules_page():
    tr = "".join(f'<tr{" class=cp" if n in (4, 9) else ""}><td class="day">هفتهٔ {fa(n)}</td><td></td><td></td>'
                 f'<td></td><td></td><td></td></tr>' for n in range(1, 14))
    return f"""<section class="sec">{mk('rules')}
<h2>قواعد و پیگیری</h2>
<div class="grid">
<div class="card"><h4>جبران عقب‌افتادگی</h4><ul>
<li><b>یک بلوک از دست رفت:</b> همان هفته، بلوک B یکی از روزهای بعد جایش را می‌گیرد.</li>
<li><b>یک روز کامل:</b> مبحث ریاضی آن روز جمعه عصر همان هفته؛ مبحث تخصصی فقط تستی، در بلوک تست روز بعد.</li>
<li><b>بیش از ۲ روز:</b> برنامه را جابه‌جا نکن؛ از مباحث عقب‌مانده فقط اولویت ۱ را در فاز ۲ بگیر.</li>
<li><b>هرگز:</b> کم کردن خواب، حذف بلوک ریاضی، یا تعطیل کردن آزمون جمعه.</li>
</ul></div>
<div class="card"><h4>تصمیم هفتگی (جمعه ۲۲:۰۰)</h4><ul>
<li>درس بالای ۵۰٪ در آزمون هفتگی: برنامهٔ عادی.</li>
<li>۳۰ تا ۵۰٪: یک بلوک B هفتهٔ بعد به تست همان درس می‌رسد.</li>
<li>زیر ۳۰٪: دو بلوک B؛ اول درس‌نامهٔ مباحث «مفهوم»ی دفتر خطا.</li>
</ul></div>
<div class="card"><h4>نقاط کنترل</h4><ul>
<li><b>جمعه ۱۳ آذر:</b> اگر کمتر از ۷۰٪ بلوک‌ها انجام شده یا میانگین آزمون زیر ۳۰٪ است: از هوش فقط A*، منطق، CSP و خصمانه می‌ماند و برنامه‌سازی فقط در فاز ۲ تست می‌شود. ریاضی دست نمی‌خورد.</li>
<li><b>جمعه ۱۸ دی:</b> هر درس زیر ۳۰٪، در فاز ۲ فقط مباحث «اولویت ۱».</li>
</ul></div>
<div class="card"><h4>آزمون هفتگی و دفتر خطا</h4><ul>
<li>۴۰٪ از همین هفته و ۶۰٪ از هفته‌های قبل؛ هفتهٔ ۱ حدود ۳۰ تست، از هفتهٔ ۴ حدود ۶۰ تست.</li>
<li>هر تست غلط، سفید، یا درستِ حدسی = یک سطر دفتر خطا: تاریخ، درس، مبحث، منبع، علت، نکته.</li>
<li>علت: <b>مفهوم</b> (درس‌نامه را دوباره بخوان) · <b>دقت</b> (روش چک بساز) · <b>زمان</b> (راه سریع‌تر پیدا کن).</li>
</ul></div></div>
<h3>جدول پیگیری هفتگی (جمعه‌ها پر کن؛ هدف: ۲۴ بلوک از ۲۸)</h3>
<table><tr><th>هفته</th><th>بلوک انجام‌شده</th><th>ریاضی ٪</th><th>تخصصی ٪</th><th>ضعیف‌ترین مبحث</th><th>تصمیم هفتهٔ بعد</th></tr>{tr}</table>
</section>"""



# ---------------------------------------------------------------- جدول هفتگی (ساعت‌ها، v3)
GRID_CSS = """
@page wide{size:A4 landscape;margin:9mm 10mm}
.wide{page:wide}
.wk{width:100%;border-collapse:separate;border-spacing:3px;font-size:8.2pt;line-height:1.35;table-layout:fixed}
.wk th{background:#1f2a44;color:#fff;border-radius:7px;padding:6px 3px;text-align:center;font-size:9pt}
.wk th small{display:block;font-weight:400;opacity:.8;font-size:7pt}
.wk td{border-radius:7px;padding:5px 4px;text-align:center;vertical-align:middle;border:none;background:#f0efec}
.wk td.t{background:#fff;border:1px solid #e2e6ee;font-weight:700;color:#1f2a44;white-space:nowrap;font-size:7.8pt}
.wk td b{display:block;font-size:8.6pt}
.wk td small{display:block;color:#5b6475;font-size:7pt;margin-top:1px}
.wk .m{background:#dbe7fb}.wk .mt{background:#eaf2fd}
.wk .a{background:#d6f0dc}.wk .at{background:#e9f7ec}
.wk .bb{background:#e6defa}
.wk .cls{background:#3c4a6b;color:#fff}.wk .cls small{color:#dfe5f2}
.wk .ex{background:#c94040;color:#fff}.wk .ex small{color:#fde}
.wk .exa{background:#f4d4d4}
.wk .th{background:#f9d9e6}
.wk .wo{background:#fbe1cf}
.wk .en{background:#fdf1c2}
.wk .rv{background:#e8e6f5}
.wk .fr{background:#f3f3f0;color:#7a8191}
.wkleg{font-size:7.6pt;color:#4a5263;margin-top:4pt;display:flex;flex-wrap:wrap;gap:4px 12px}
.wkleg span:before{content:"";display:inline-block;width:9px;height:9px;border-radius:3px;margin-left:4px;
 background:var(--c);vertical-align:middle}
.wknote{font-size:7.8pt;background:#fff;border:1px solid #e2e6ee;border-radius:8px;padding:5px 9px;margin-top:5pt}
"""


def _c(cls, title, sub="", rs=1, cs=1):
    span = (f' rowspan="{rs}"' if rs > 1 else "") + (f' colspan="{cs}"' if cs > 1 else "")
    s = f"<small>{sub}</small>" if sub else ""
    return f'<td class="{cls}"{span}><b>{title}</b>{s}</td>'


def week_grid() -> str:
    days = ["شنبه", "یکشنبه<small>هفتهٔ فرد</small>", "یکشنبه<small>هفتهٔ زوج</small>", "دوشنبه",
            "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"]
    M = _c("m", "ریاضی", "درس‌نامه + مثال")
    A = _c("a", "تخصصی A", "درس‌نامه")
    MT = _c("mt", "تست ریاضی", "۱۰ تا ۱۲ تست")
    AT = _c("at", "تست تخصصی A", "۱۵ تا ۲۰ تست + تحلیل")
    B = _c("bb", "تخصصی B", "نیم درس‌نامه، نیم تست")
    L = _c("fr", "ناهار + ۲۰ دقیقه چرت")
    R = _c("rv", "مرور", "کارت‌ها ۱، ۳، ۷ روز + دفتر خطا")
    W = _c("fr", "پیاده‌روی / ورزش")
    rows = [
        ("۰۷:۰۰ تا ۰۸:۰۰", [_c("fr", "بیداری، صبحانه، ۱۰ دقیقه لغت", cs=8)]),
        ("۰۸:۰۰ تا ۰۹:۳۰", [M, _c("cls", "کلاس طراحی الگوریتم", "۰۸:۰۰ تا ۱۰:۰۰"), M, M, M, M, M,
                            _c("ex", "آزمون هفتگی زمان‌دار", "۰۸:۰۰ تا ۱۱:۰۰ · مباحث همین هفته و قبل", rs=2)]),
        ("۰۹:۴۵ تا ۱۱:۱۵", [A, _c("m", "ریاضی", "درس‌نامه · ۱۰:۱۵ تا ۱۱:۴۵"), A, A, A, A, A]),
        ("۱۱:۳۰ تا ۱۲:۱۵", [MT, _c("cls", "جلسهٔ حضوری کار", "۱۲:۰۰ تا ۱۳:۰۰"),
                            _c("rv", "مرور کارت‌ها", "۱۱:۱۵ تا ۱۲:۰۰ · رفتن به جلسه"), MT, MT, MT, MT,
                            _c("exa", "تحلیل آزمون + دفتر خطا", "۱۱:۱۵ تا ۱۲:۴۵")]),
        ("۱۲:۱۵ تا ۱۴:۰۰", [L, _c("cls", "استاد راهنما", "۱۳:۱۵ تا ۱۴:۰۰ (پیشنهادی)"),
                            _c("cls", "جلسهٔ حضوری کار", "۱۲ تا ۱۳ · ناهار ۱۳ تا ۱۴"), L, L, L, L, _c("fr", "ناهار")]),
        ("۱۴:۰۰ تا ۱۵:۳۰", [AT, _c("a", "تخصصی A", "ناهار ۱۴ تا ۱۴:۴۵ · درس‌نامه ۱۴:۴۵ تا ۱۶:۱۵"), AT,
                            _c("cls", "کلاس طراحی الگوریتم", "۱۴:۰۰ تا ۱۶:۰۰"), AT, AT, AT,
                            _c("th", "پایان‌نامه و مقاله", "۱۴:۰۰ تا ۱۶:۰۰")]),
        ("۱۵:۴۵ تا ۱۷:۱۵", [B, _c("at", "تست تخصصی A", "کوتاه · ۱۶:۳۰ تا ۱۷:۳۰"), B,
                            _c("at", "تست تخصصی A", "۱۶:۱۵ تا ۱۷:۴۵"), B, B, B, _c("fr", "آزاد", rs=5)]),
        ("۱۷:۱۵ تا ۱۷:۴۵", [R, _c("rv", "مرور", "۱۷:۳۰ تا ۱۸:۰۰"), _c("mt", "تست ریاضی", "کوتاه · ۱۷:۱۵ تا ۱۸:۰۰"),
                            _c("rv", "مرور", "۱۷:۴۵ تا ۱۸:۱۵"), R, R, R]),
        ("۱۷:۴۵ تا ۱۸:۱۵", [W, _c("fr", "—"), W, _c("fr", "—"), W, W, W]),
        ("۱۸:۱۵ تا ۲۰:۰۰", [_c("fr", "شام و استراحت (بدون درس)", cs=7)]),
        ("۲۰:۰۰ تا ۲۲:۰۰", [_c("wo", "کار شرکت", "سقف سخت: ۲۲:۰۰", cs=7)]),
        ("۲۲:۰۰ تا ۲۲:۳۰", [_c("en", "زبان", "۲۰ لغت + لایتنر · سه‌شنبه و پنجشنبه: درک مطلب", cs=7),
                            _c("en", "مرور برنامهٔ هفتهٔ بعد", "+ جدول هفتگی")]),
        ("۲۳:۳۰", [_c("fr", "خواب (بیداری ۰۷:۰۰)", cs=8)]),
    ]
    head = "<tr><th>ساعت</th>" + "".join(f"<th>{d}</th>" for d in days) + "</tr>"
    body = "".join(f'<tr><td class="t">{t}</td>{"".join(cells)}</tr>' for t, cells in rows)
    leg = [("#dbe7fb", "ریاضی (گسسته / احتمال / جبر خطی)"), ("#d6f0dc", "تخصصی A: درس سنگین هفته"),
           ("#e6defa", "تخصصی B: درس سبک هفته"), ("#3c4a6b", "کلاس و جلسه"), ("#fbe1cf", "کار شرکت"),
           ("#f9d9e6", "پایان‌نامه"), ("#fdf1c2", "زبان"), ("#c94040", "آزمون"), ("#e8e6f5", "مرور")]
    legend = "".join(f'<span style="--c:{c}">{t}</span>' for c, t in leg)
    return (f'<table class="wk">{head}{body}</table><div class="wkleg">{legend}</div>'
            '<div class="wknote">مبحث هر خانه از جدول هفتهٔ همین برنامه خوانده می‌شود · '
            '<b>روز سخت:</b> فقط درس‌نامهٔ ریاضی و تخصصی A · <b>بیماری:</b> استراحت · '
            '<b>از ۳ بهمن:</b> آزمون جامع شنبه، سه‌شنبه و پنجشنبه ۰۸:۰۰ تا ۱۲:۰۰؛ کار فقط ۱ ساعت؛ پایان‌نامه متوقف · '
            '<b>آزمون: جمعه ۱۶ بهمن</b></div>')


def grid_page() -> str:
    return (f'<section class="sec wide">{mk("grid")}<h2 style="margin-bottom:5pt">برنامهٔ هفتگی (ساعت‌ها) '
            f'<span style="font-size:9pt;font-weight:400;color:#6b7385">· از ۲۲ آبان ۱۴۰۵ · خواب ۲۳:۳۰ و بیداری ۰۷:۰۰ ثابت</span>'
            f'</h2>{week_grid()}</section>')


def export_grid_png(path: pathlib.Path):
    fonts = bb.ensure_fonts()
    html = (f'<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><style>{bb.font_css(fonts)}{CSS}'
            f'{GRID_CSS}body{{background:#f7f6f3;padding:22px 26px;width:1500px}}.wk{{font-size:10.5pt}}'
            f'.wk td b{{font-size:11pt}}.wk td small{{font-size:8.6pt}}.wk th{{font-size:11.5pt}}'
            f'.wkleg,.wknote{{font-size:9.5pt}}</style></head><body>'
            f'<h1 style="font-size:24pt">برنامهٔ هفتگی کنکور دکتری ۱۴۰۶</h1>'
            f'<div style="color:#6b7385;margin-bottom:12px">نسخهٔ ۳ · از ۲۲ آبان ۱۴۰۵ · بلوک‌ها ۹۰ دقیقه، بدون گوشی · '
            f'خواب ۲۳:۳۰ و بیداری ۰۷:۰۰ ثابت</div>{week_grid()}</body></html>')
    with tempfile.TemporaryDirectory() as tmp:
        h = pathlib.Path(tmp) / "grid.html"
        h.write_text(html, encoding="utf-8")
        import subprocess
        subprocess.run(["node", str(bb.TOOLS / "screenshot.js"), str(h), str(path)], check=True)
    print(f"{path.relative_to(bb.ROOT)}")


def build():
    fonts = bb.ensure_fonts()
    body = cover() + overview() + grid_page() + day_page() + "".join(week_page(i, w) for i, w in enumerate(W)) + p2_page() + rules_page()
    html = (f'<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><style>{bb.font_css(fonts)}{CSS}{GRID_CSS}'
            f'</style></head><body>{body}</body></html>')
    with tempfile.TemporaryDirectory() as tmp:
        h, p = pathlib.Path(tmp) / "plan.html", pathlib.Path(tmp) / "plan.pdf"
        h.write_text(html, encoding="utf-8")
        if "--keep-html" in sys.argv:
            (bb.ROOT / "plan-debug.html").write_text(html, encoding="utf-8")
        bb.print_pdf([(h, p)])
        pages = bb.marker_pages(p)
        r = PdfReader(p)
        wr = PdfWriter()
        wr.append(r)
        marks = [("overview", "نقشهٔ ۱۳ هفته"), ("grid", "برنامهٔ هفتگی (ساعت‌ها)"), ("day", "یک روز معمولی")]
        marks += [(f"w{i + 1}", f"هفتهٔ {fa(i + 1)} · {wrange(i)}") for i in range(len(W))]
        marks += [("p2", f"هفتهٔ ۱۰ · فاز ۲ · {wrange(9)}"), ("p2b", f"هفتهٔ ۱۱ · فاز ۲ · {wrange(10)}"),
                  ("p3", f"هفتهٔ ۱۲ · فاز ۳ · {wrange(11)}"), ("p4", f"هفتهٔ ۱۳ · هفتهٔ آزمون · {wrange(12)}"),
                  ("rules", "قواعد و پیگیری")]
        for k, t in marks:
            if k in pages:
                wr.add_outline_item(t, pages[k] - 1)
        wr.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
        with open(OUT, "wb") as f:
            wr.write(f)
    print(f"{OUT.relative_to(bb.ROOT)}  ({len(PdfReader(OUT).pages)} صفحه)")


def write_progress():
    """progress.md تازه بر اساس برنامه (فقط یک بار، وقتی هنوز چیزی ثبت نشده)."""
    import re
    lines = ["# پیشرفت", "",
             "**شروع دوباره:** شنبه ۱۶ آبان ۱۴۰۵ · **آزمون:** جمعه ۱۶ بهمن ۱۴۰۵ · **روز مانده در شروع:** ۹۱", "",
             "برنامهٔ روزبه‌روز: `جزوه-PDF/00-برنامه-مطالعه.pdf` (منبع: `tools/build_plan.py`).", "",
             "تسلط: ۰ = شروع نشده · ۱ = گنگ · ۲ = مفهوم را می‌فهمم · ۳ = تست ساده را می‌زنم · "
             "۴ = تست کنکور را می‌زنم · ۵ = سریع و مطمئن", ""]
    for i, w in enumerate(W):
        seen = []
        for day in w["days"]:
            for c in day:
                for m in re.finditer(r'<b>([^<]+)</b> · فصل ([۰-۹]+)', c):
                    k = (m.group(1), m.group(2))
                    if k not in seen:
                        seen.append(k)
        lines += [f"## هفتهٔ {fa(i + 1)} ({wrange(i)}): {w['title']}",
                  "| درس | فصل | تسلط | درصد تست | آخرین مرور |", "|---|---|---|---|---|"]
        lines += [f"| {b} | {c} | ۰ | | |" for b, c in seen]
        lines.append("")
    lines += ["## جدول هفتگی (جمعه پر شود)",
              "| هفته | بلوک انجام‌شده (از ۲۸) | ریاضی ٪ | تخصصی ٪ | ضعیف‌ترین مبحث | تصمیم هفتهٔ بعد |",
              "|---|---|---|---|---|---|"]
    lines += [f"| {fa(n)}{' (کنترل ۱)' if n == 4 else ' (کنترل ۲)' if n == 9 else ''} | | | | | |" for n in range(1, 14)]
    (bb.ROOT / "tutor" / "progress.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("tutor/progress.md نوشته شد")


if __name__ == "__main__":
    build()
    export_grid_png(bb.ROOT / "tutor" / "weekly-schedule-v3.png")
    if "--progress" in sys.argv:
        write_progress()
