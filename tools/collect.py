# -*- coding: utf-8 -*-
"""Collect every image generated for the character into the site and rebuild samples.json."""
import sys, os, json, glob, shutil, re
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
ROOT = r"C:\Users\dumok\dev\quoka-character"
TH = r"C:\Users\dumok\dev\ai-concept-theater"
BLOG = r"C:\Users\dumok\Downloads\AI개념극장업데이트(1002)\03_블로그_포스팅"
NYV1 = r"C:\Users\dumok\Downloads\쿼카_2027_붉은양의해_릴스\v1_중국풍_보관"
A = lambda *p: os.path.join(ROOT, *p)
S = json.load(open(A("assets", "samples.json"), encoding="utf-8"))

def to_webp(src, dst, max_w=1280, q=84):
    if os.path.exists(dst): return
    im = Image.open(src); im.thumbnail((max_w, 4000)); im.save(dst, "WEBP", quality=q)

# 1) theater outfit sets: key + poses (point/think/oops/wave and any extras)
os.makedirs(A("assets", "char"), exist_ok=True)
POSE_KO = {"point": "가리키기", "think": "생각", "oops": "놀람", "wave": "인사", "tablet": "태블릿", "dice": "주사위", "glass": "돋보기", "globe": "지구본", "idea": "아이디어", "base": "기본"}
for k in S["keys"]:
    if k.get("dup"): continue
    poses = []
    for f in sorted(glob.glob(os.path.join(TH, "assets", "char", k["slug"], "*.webp"))):
        p = os.path.splitext(os.path.basename(f))[0]
        d = A("assets", "char", f'{k["slug"]}_{p}.webp')
        if not os.path.exists(d): shutil.copy(f, d)
        poses.append({"file": f"assets/char/{k['slug']}_{p}.webp", "pose": p, "name": POSE_KO.get(p, p)})
    k["poses"] = poses
print("sets", sum(1 for k in S["keys"] if not k.get("dup")), "poses", sum(len(k.get("poses", [])) for k in S["keys"]))

# 2) common poses (theater, leaf version)
common = []
for f in sorted(glob.glob(os.path.join(TH, "assets", "char", "*.webp"))):
    p = os.path.splitext(os.path.basename(f))[0]
    d = A("assets", "poses", p + ".webp")
    if not os.path.exists(d): shutil.copy(f, d)
    common.append({"file": f"assets/poses/{p}.webp", "name": POSE_KO.get(p, p), "group": "극장 공용 포즈"})
S["common"] = common; print("common", len(common))

# 3) blog infographics 40 x 4
os.makedirs(A("assets", "info"), exist_ok=True)
info = []
for d in sorted(glob.glob(os.path.join(BLOG, "E*"))):
    ep = os.path.basename(d); code = ep.split("_")[0]; slug = ep.split("_", 1)[1]
    heads = {}
    try:
        spec = json.load(open(os.path.join(d, "인포그래픽_스펙.json"), encoding="utf-8"))
        for it in (spec if isinstance(spec, list) else spec.get("items", [])):
            heads[int(it.get("n", 0))] = it.get("headline", "")
    except Exception: pass
    for n in range(1, 5):
        src = os.path.join(d, f"인포그래픽_{n}.png")
        if not os.path.exists(src): continue
        dst = A("assets", "info", f"{code}_{n}.webp"); to_webp(src, dst, 1280, 82)
        info.append({"file": f"assets/info/{code}_{n}.webp", "name": f"{code} · {heads.get(n) or slug}", "group": "블로그 인포그래픽", "scene": True, "wide": True})
S["info"] = info; print("info", len(info))

# 4) new year v1 (archived, Chinese-flavoured)
os.makedirs(A("assets", "newyear_v1"), exist_ok=True)
v1 = []
for f in sorted(glob.glob(os.path.join(NYV1, "*.png"))):
    b = os.path.splitext(os.path.basename(f))[0]
    if b.startswith("_"): continue
    dst = A("assets", "newyear_v1", b + ".webp"); to_webp(f, dst, 1000, 84)
    v1.append({"file": f"assets/newyear_v1/{b}.webp", "name": b.replace("_", " · "), "group": "2027 새해 1차(보관)", "scene": True})
S["newyear_v1"] = v1; print("newyear_v1", len(v1))

json.dump(S, open(A("assets", "samples.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("samples.json ok")
