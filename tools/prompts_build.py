# -*- coding: utf-8 -*-
"""Build assets/prompts.json: site image path -> generation prompt + settings.
Sources: tools/_session_prompts.json (extracted from the session transcript), theater manifests, blog _prompts.json."""
import sys, os, json, glob, re
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r"C:\Users\dumok\dev\quoka-character"
TH = r"C:\Users\dumok\dev\ai-concept-theater"
BLOG = r"C:\Users\dumok\Downloads\AI개념극장업데이트(1002)\03_블로그_포스팅"
A = lambda *p: os.path.join(ROOT, *p)
S = json.load(open(A("tools", "_session_prompts.json"), encoding="utf-8"))
byjob = {x["job_id"]: x for x in S if x.get("job_id")}
OUT = {}
def put(path, x, note=""):
    if not x or not x.get("prompt"): return
    OUT[path] = {"prompt": x["prompt"], "model": x.get("model"), "quality": x.get("quality"), "ar": x.get("ar"), "bg": x.get("bg"), "refs": x.get("refs") or [], "note": note}
def batch(prefix):  # all requests of batches whose timestamp starts with prefix, sorted by index
    return sorted([x for x in S if x["ts"].startswith(prefix)], key=lambda x: x["index"])

# --- keys (theater) by batch order
E_N = ["e1-agent-mcp","e2-seed","e3-diffusion","e4-plausible","e5-context","e6-rag","n1-consistency","n2-video-cost","n3-english-prompt","n4-reasoning","n5-vibecoding","n6-ai-label"]
b = [x for x in batch("2026-09-25T13:24") if "New outfit" in x["prompt"]]
for slug, x in zip(E_N, b): put(f"assets/samples/{slug}.webp", x, "극장 의상 키비주얼")
S3_4 = ["s3-voice","s3-avatar","s3-music","s3-subtitle","s3-vision","s3-role","s4-grading","s4-sycophancy","s4-privacy","s4-calc","s4-search","s4-choose"]
for slug, x in zip(S3_4, batch("2026-09-25T13:56:52")): put(f"assets/samples/{slug}.webp", x, "극장 의상 키비주얼")
s5keys = json.load(open(os.path.join(TH, "assets/gen/s5/keys.json"), encoding="utf-8"))
keyjob2slug = {}
for slug, jid in s5keys.items():
    put(f"assets/samples/{slug}.webp", byjob.get(jid), "극장 의상 키비주얼"); keyjob2slug[jid] = slug
W = ["w1-santa","w2-reindeer","w3-snow","w4-elf","w5-baker","w6-skater"]; W2 = ["w7-librarian","w8-overcoat","w9-lineman","w10-ski"]
KW = {"w1-santa":"santa","w2-reindeer":"reindeer","w3-snow":"snow","w4-elf":"elf","w5-baker":"gingerbread","w6-skater":"skat","w7-librarian":"librar","w8-overcoat":"overcoat","w9-lineman":"line","w10-ski":"ski"}
for slugs, pre in ((W, "2026-09-26T06:46"), (W2, "2026-10-02T08:05")):
    for slug, x in zip(slugs, batch(pre)):
        if KW[slug] not in x["prompt"].lower(): print("WARN keyword mismatch", slug)
        put(f"assets/samples/{slug}.webp", x, "극장 의상 키비주얼"); keyjob2slug[x["job_id"]] = slug
# --- poses (theater): batch tsv -> job id
for tsv in ("batch2.tsv", "batch3.tsv"):
    for line in open(os.path.join(TH, "assets/gen", tsv), encoding="utf-8"):
        parts = line.strip().split("\t")
        if len(parts) < 3: continue
        slug, pose, fn = parts[:3]; jid = fn.split("_", 3)[-1].replace(".png", "")
        put(f"assets/char/{slug}_{pose}.webp", byjob.get(jid), "극장 의상 포즈")
POSE_KW = [("point", "pointing"), ("think", "chin"), ("oops", "surprised"), ("wave", "waving")]
def pose_of(p):
    for k, kw in POSE_KW:
        if kw in p: return k
    return None
for pre in ("2026-09-26T06:32", "2026-09-26T06:33", "2026-09-26T06:49", "2026-10-02T08:07"):
    for x in batch(pre):
        ref = (x.get("refs") or [None])[0]; slug = keyjob2slug.get(ref); pose = pose_of(x["prompt"])
        if slug and pose: put(f"assets/char/{slug}_{pose}.webp", x, "극장 의상 포즈")
# --- paris, sheets, new year, sebae by index order
paris = sorted(glob.glob(A("assets/paris", "*.webp")))
for x, f in zip(batch("2026-10-03T15:39"), paris): put("assets/paris/" + os.path.basename(f), x, "파리지앵 키비주얼")
SHEET = ["01_turnaround", "02_expressions", "03_poses", "04_colors"]
for x, n in zip(batch("2026-10-03T15:47"), SHEET): put(f"assets/sheets/{n}.webp", x, "캐릭터 시트")
for x, n in zip(batch("2026-10-03T16:24"), SHEET): put(f"assets/sheets/v2_눈썹_보관/{n}.webp", x, "캐릭터 시트(눈썹 버전)")
NY1 = ["양01_한옥마당_인사","양02_동해_일출","양03_세배","양04_연날리기","양05_불꽃놀이","한복01_색동저고리_복주머니","한복02_파스텔_당의풍","한복03_두루마기_호건","한복04_생활한복_카페","한복05_금박_궁중"]
for x, n in zip(batch("2026-10-03T15:48"), NY1): put(f"assets/newyear_v1/{n}.webp", x, "2027 새해 1차")
NY2 = ["양01_한옥마당_세배","양02_동해_일출_솟대","양03_안방_세배_떡국","양04_방패연_날리기","양05_궁궐문_청사초롱_불꽃","한복01_색동저고리_복주머니","한복02_파스텔_민트저고리","한복03_남아_배자_호건","한복04_생활한복_떡국","한복05_당의_노리개"]
for x, n in zip(batch("2026-10-03T16:01"), NY2): put(f"assets/newyear/{n}.webp", x, "2027 새해 릴스")
SB = ["01_마주서서_손모으기","02_무릎꿇기","03_엎드려절","04_일어나며_웃기","05_복주머니_환호"]
for x, n in zip(batch("2026-10-03T16:10"), SB): put(f"assets/sebae/{n}.webp", x, "세배 시퀀스")
# --- infographics
for d in sorted(glob.glob(os.path.join(BLOG, "E*"))):
    code = os.path.basename(d).split("_")[0]
    try: ps = json.load(open(os.path.join(d, "_prompts.json"), encoding="utf-8"))
    except Exception: continue
    for it in ps:
        OUT[f"assets/info/{code}_{it['n']}.webp"] = {"prompt": it["prompt"], "model": "gpt_image_2_5", "quality": "high", "ar": "16:9", "bg": None, "refs": [], "note": "블로그 인포그래픽"}
json.dump(OUT, open(A("assets", "prompts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# coverage report against samples.json
sm = json.load(open(A("assets", "samples.json"), encoding="utf-8"))
files = [k["file"] for k in sm["keys"] if not k.get("dup")] + [p["file"] for k in sm["keys"] if not k.get("dup") for p in k.get("poses", [])]
for g in ("paris", "sebae", "newyear_v1", "sheets_v2", "common", "info"): files += [x["file"] for x in sm.get(g, [])]
files += [f"assets/sheets/{n}.webp" for n in SHEET] + [f"assets/newyear/{n}.webp" for n in NY2]
miss = [f for f in files if f not in OUT]
print("prompts", len(OUT), "covered", len(files) - len(miss), "/", len(files))
print("missing:", miss[:40])
