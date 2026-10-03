# -*- coding: utf-8 -*-
"""Render the 9 sketchbook spreads (1760x1240 transparent PNG, paper at x 5.1-94.9%, y 21.8-78.2%)
   so the ThreeUI sketchbook engine's page-turn geometry matches exactly."""
import sys, os, json, glob
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = r"C:\Users\dumok\dev\quoka-character"
OUT = os.path.join(ROOT, "assets", "plates"); os.makedirs(OUT, exist_ok=True)
W, H = 1760, 1240
BX0, BX1, BY0, BY1 = 90, 1670, 270, 970   # paper rect
GUT = (BX0 + BX1) // 2
INK=(25,31,40); SUB=(78,89,97); MUTED=(139,149,161); LINE=(229,232,235); BLUE=(49,130,246); BLUEBG=(232,243,255)
GREEN=(0,167,111); GREENBG=(230,247,241); RED=(240,68,82); REDBG=(255,238,238); G2=(242,244,246)
FB = r"C:\Windows\Fonts\malgunbd.ttf"; FR = r"C:\Windows\Fonts\malgun.ttf"
def f(sz, bold=False): return ImageFont.truetype(FB if bold else FR, sz)
samples = json.load(open(os.path.join(ROOT, "assets", "samples.json"), encoding="utf-8"))
A = lambda *p: os.path.join(ROOT, *p)

def base_canvas():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # two pages
    for x0, x1 in ((BX0, GUT), (GUT, BX1)):
        d.rounded_rectangle((x0, BY0, x1, BY1), radius=6, fill=(255, 255, 255, 255), outline=LINE+(255,), width=1)
    # gutter shading
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for i in range(26):
        a = int(38 * (1 - i / 26))
        gd.line((GUT - i, BY0 + 2, GUT - i, BY1 - 2), fill=(25, 31, 40, a))
        gd.line((GUT + i, BY0 + 2, GUT + i, BY1 - 2), fill=(25, 31, 40, a))
    im.alpha_composite(g)
    return im

def header(d, label, page, n):
    d.text((BX0 + 34 if page == 'L' else GUT + 34, BY0 + 24), label, font=f(15, True), fill=MUTED)
    txt = f"{n:02d}"
    x = GUT - 34 - d.textlength(txt, font=f(15, True)) if page == 'L' else BX1 - 34 - d.textlength(txt, font=f(15, True))
    d.text((x, BY1 - 40), txt, font=f(15, True), fill=MUTED)

def fit(img, w, h):
    im = img.copy(); im.thumbnail((w, h), Image.LANCZOS); return im

def paste_center(im, pic, cx, cy):
    im.alpha_composite(pic.convert("RGBA"), (int(cx - pic.width / 2), int(cy - pic.height / 2)))

def pill(d, x, y, text, fg, bg, font):
    tw = d.textlength(text, font=font); h = font.size + 14
    d.rounded_rectangle((x, y, x + tw + 26, y + h), radius=h // 2, fill=bg)
    d.text((x + 13, y + 6), text, font=font, fill=fg)
    return x + tw + 26 + 10

def wrap(d, text, font, width):
    out, line = [], ""
    for ch in text:
        if d.textlength(line + ch, font=font) > width and line:
            out.append(line); line = ch
        else: line += ch
    if line: out.append(line)
    return out

def save(im, n, name):
    im.save(os.path.join(OUT, f"{n:02d}_{name}.png"), optimize=True); print("plate", n, name)

# ---------------- 01 cover / anchor
im = base_canvas(); d = ImageDraw.Draw(im)
header(d, "QUOKA · OFFICIAL CHARACTER KIT", 'L', 1); header(d, "앵커 레퍼런스", 'R', 1)
def anchor_crop():
    src = Image.open(A("assets/sheets/01_turnaround.png")).convert("RGB")
    import numpy as np
    a = np.asarray(src); dark = (a.min(axis=2) < 235)
    cols = dark.any(axis=0); xs = [i for i, v in enumerate(cols) if v]
    # first figure = first run of non-white columns (allow small gaps)
    x0 = xs[0]; x1 = x0
    for i in xs:
        if i - x1 > 40: break
        x1 = i
    rows = dark[:, x0:x1].any(axis=1); ys = [i for i, v in enumerate(rows) if v]
    pad = 20
    crop = src.crop((max(0, x0 - pad), max(0, ys[0] - pad), min(src.width, x1 + pad), min(src.height, ys[-1] + pad))).convert("RGBA")
    # knock out near-white background
    px = crop.load()
    for y in range(crop.height):
        for x in range(crop.width):
            r, g, b, _ = px[x, y]
            if r > 238 and g > 238 and b > 238: px[x, y] = (r, g, b, 0)
    crop.save(A("assets", "anchor.png"))
    return crop
base = anchor_crop()
paste_center(im, fit(base, 560, 560), (BX0 + GUT) / 2, (BY0 + BY1) / 2 + 10)
d = ImageDraw.Draw(im)
x = GUT + 48; y = BY0 + 70
d.text((x, y), "쿼카 공식 캐릭터", font=f(50, True), fill=INK); y += 70
d.text((x, y), "언제 뽑아도 같은 얼굴이 나오도록 이 이미지를 기준으로 삼아요.", font=f(19), fill=SUB); y += 48
rows = [("모델", "gpt_image_2_5 (Higgsfield)"), ("참조 역할", "image_references"), ("media_id", "270a5b4d-6cb1-41fc-bd67-9608277bc648"),
        ("의상·포즈", "quality medium · 2:3 · transparent · 0.5cr"), ("장면·릴스", "quality high · 9:16 또는 16:9 · 1.5cr"), ("시트", "quality high · 16:9 · opaque · 1.5cr")]
for k, v in rows:
    d.text((x, y), k, font=f(16, True), fill=MUTED); d.text((x + 120, y), v, font=f(17), fill=INK); y += 36
    d.line((x, y - 6, BX1 - 48, y - 6), fill=LINE)
y += 14; px = x
for t, fg, bg in (("낙엽 없음", RED, REDBG), ("얼굴 폭 고정", RED, REDBG), ("눈 간격 고정", GREEN, GREENBG), ("골든 브라운", GREEN, GREENBG)):
    px = pill(d, px, y, t, fg, bg, f(15, True))
save(im, 1, "cover")

# ---------------- 02-05 sheets
sheets = [("turnaround", "턴어라운드", "앞 · 3/4 · 옆 · 뒤. 머리 폭과 귀 위치의 기준이에요."),
          ("expressions", "표정 시트", "기본 · 활짝 · 놀람 · 생각 · 졸림 · 윙크. 표정이 바뀌어도 눈 간격은 같아요."),
          ("poses", "포즈 시트", "서기 · 가리키기 · 생각 · 놀람 · 인사 · 앉기. 극장 해설 포즈 4종의 출처."),
          ("colors", "색 · 재질", "머리 털 · 배 털 · 코 · 눈 · 발 색 견본과 털 결 확대.")]
for i, (slug, title, cap) in enumerate(sheets, start=2):
    im = base_canvas(); d = ImageDraw.Draw(im)
    header(d, f"CHARACTER SHEET {i-1:02d}", 'L', i); header(d, title, 'R', i)
    src = glob.glob(A("assets/sheets", f"0{i-1}_{slug}.png"))[0]
    pic = fit(Image.open(src).convert("RGBA"), 1460, 560)
    paste_center(im, pic, (BX0 + BX1) / 2, (BY0 + BY1) / 2 + 14)
    d = ImageDraw.Draw(im)
    d.text((BX0 + 34, BY0 + 50), title, font=f(30, True), fill=INK)
    d.text((GUT + 34, BY1 - 44), cap, font=f(15), fill=SUB)
    save(im, i, slug)

# ---------------- 07 paris 20
im = base_canvas(); d = ImageDraw.Draw(im)
header(d, "PARISIAN · AUTUMN 2026", 'L', 6); header(d, "파리지앵 20종", 'R', 6)
for k, it in enumerate(samples["paris"]):
    page, j = divmod(k, 10); r, c = divmod(j, 5)
    x0 = (BX0 if page == 0 else GUT) + 26 + c * 150; y0 = BY0 + 60 + r * 310
    pic = fit(Image.open(A(it["file"])).convert("RGBA"), 140, 240)
    paste_center(im, pic, x0 + 70, y0 + 125)
    d = ImageDraw.Draw(im)
    nm = it["name"].replace(" · ", "·")
    if d.textlength(nm, font=f(12)) > 140: nm = nm[:11] + "…"
    d.text((x0 + 70 - d.textlength(nm, font=f(12)) / 2, y0 + 258), nm, font=f(12), fill=SUB)
save(im, 6, "paris")

# ---------------- 08 theater keys 42
im = base_canvas(); d = ImageDraw.Draw(im)
header(d, "AI CONCEPT THEATER · WARDROBE", 'L', 7); header(d, "극장 의상 42종", 'R', 7)
keys = [k for k in samples["keys"] if not k.get("dup")][:42]
for k, it in enumerate(keys):
    page, j = divmod(k, 21); r, c = divmod(j, 7)
    x0 = (BX0 if page == 0 else GUT) + 22 + c * 107; y0 = BY0 + 54 + r * 215
    pic = fit(Image.open(A(it["file"])).convert("RGBA"), 98, 165)
    paste_center(im, pic, x0 + 53, y0 + 85)
    d = ImageDraw.Draw(im)
    nm = it["name"]
    if d.textlength(nm, font=f(11)) > 100: nm = nm[:7] + "…"
    d.text((x0 + 53 - d.textlength(nm, font=f(11)) / 2, y0 + 176), nm, font=f(11), fill=SUB)
save(im, 7, "theater")

# ---------------- 09 new year 10
im = base_canvas(); d = ImageDraw.Draw(im)
header(d, "2027 · YEAR OF THE RED SHEEP", 'L', 8); header(d, "2027 붉은 양의 해 · 9:16", 'R', 8)
ny = sorted(glob.glob(A("assets/newyear", "*.webp")))
for k, fp in enumerate(ny):
    page, j = divmod(k, 5)
    x0 = (BX0 if page == 0 else GUT) + 22 + j * 152
    pic = Image.open(fp).convert("RGBA"); pic = fit(pic, 146, 262)
    m = Image.new("L", pic.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, pic.width - 1, pic.height - 1), radius=10, fill=255)
    pic.putalpha(m)
    im.alpha_composite(pic, (x0, BY0 + 130))
    d = ImageDraw.Draw(im)
    nm = os.path.basename(fp)[:-5].split("_", 1)[1].replace("_", " ")
    if d.textlength(nm, font=f(12)) > 146: nm = nm[:10] + "…"
    d.text((x0 + 73 - d.textlength(nm, font=f(12)) / 2, BY0 + 402), nm, font=f(12), fill=SUB)
d.text((BX0 + 34, BY0 + 50), "쿼카 × 붉은 양", font=f(30, True), fill=INK)
d.text((GUT + 34, BY0 + 50), "설빔 한복 5종", font=f(30, True), fill=INK)
d.text((BX0 + 34, BY1 - 100), "한옥·청사초롱·솟대·방패연·떡국·색동·호건·당의. 홍등과 중국식 처마는 프롬프트에서 금지.", font=f(14), fill=SUB)
save(im, 8, "newyear")

# ---------------- 09 blog infographics (40 of 160)
im = base_canvas(); d = ImageDraw.Draw(im)
header(d, "BLOG INFOGRAPHICS · 40 EPISODES x 4", 'L', 9); header(d, "블로그 인포그래픽 160장", 'R', 9)
infos = sorted(glob.glob(A("assets/info", "E*_1.webp")))[:40]
for k, fp in enumerate(infos):
    page, j = divmod(k, 20); r, c = divmod(j, 5)
    x0 = (BX0 if page == 0 else GUT) + 22 + c * 150; y0 = BY0 + 70 + r * 140
    pic = Image.open(fp).convert("RGBA"); pic = fit(pic, 142, 80)
    m = Image.new("L", pic.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, pic.width - 1, pic.height - 1), radius=8, fill=255); pic.putalpha(m)
    im.alpha_composite(pic, (x0, y0))
    d = ImageDraw.Draw(im)
    d.text((x0, y0 + 86), os.path.basename(fp)[:3], font=f(11, True), fill=MUTED)
d.text((BX0 + 34, BY0 + 46), "E01 ~ E20", font=f(22, True), fill=INK)
d.text((GUT + 34, BY0 + 46), "E21 ~ E40", font=f(22, True), fill=INK)
d.text((GUT + 34, BY1 - 44), "편당 4장, 프리미엄 글래스 스타일(gpt_image_2_5 high 16:9). 1번 장만 표시.", font=f(14), fill=SUB)
save(im, 9, "info")

# ---------------- 10 rules
im = base_canvas(); d = ImageDraw.Draw(im)
header(d, "CONSISTENCY RULES", 'L', 10); header(d, "일관성 규칙", 'R', 10)
do = ["앵커 이미지를 image_references로 첨부하고 마스터 프롬프트로 시작해요.", "둥근 머리 · 큰 검은 눈 · 작은 코 · 짧은 주둥이 · 작고 둥근 귀. 비율을 바꾸는 말은 넣지 않아요.",
      "새 의상 세트는 키비주얼부터 뽑고, 포즈는 그 키비주얼을 참조해요.", "소품은 한 개만. 모자·베레모·헤드폰은 허용.", "투명 PNG → 여백 트림 → 세로 900px webp로 저장(극장 규격)."]
dont = ["얼굴을 넓적하게 그리는 표현(wide face, chubby cheeks). 몸은 통통해도 얼굴 폭은 고정.", "앵커 없이 글로만 생성하기. 다른 캐릭터가 나와요.",
        "머리 위 낙엽. 'nothing on the head, no autumn leaf'를 항상 넣어요.", "이미지 안 한국어 글자. 글자는 편집 단계에서 얹어요.", "실존 브랜드 로고 소품, 중국풍 요소(홍등·매듭·금박 처마)."]
for page, (title, items, fg, bg, mark) in enumerate((("해도 되는 것", do, GREEN, GREENBG, "✓"), ("하지 말 것", dont, RED, REDBG, "✕"))):
    x = (BX0 if page == 0 else GUT) + 40; y = BY0 + 60
    d.text((x, y), title, font=f(30, True), fill=INK); y += 64
    for t in items:
        d.rounded_rectangle((x, y, x + 30, y + 30), radius=15, fill=bg)
        d.text((x + 8, y + 2), mark, font=f(17, True), fill=fg)
        lines = wrap(d, t, f(17), 640)
        for ln in lines:
            d.text((x + 44, y + 3), ln, font=f(17), fill=INK); y += 28
        y += 20
save(im, 10, "rules")
print("done")
