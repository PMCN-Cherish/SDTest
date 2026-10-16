import requests, time, urllib.parse, hashlib
from pathlib import Path
COOKIE_DIR = Path(r"D:\11.project\iwen-codex\bilibili-cookies")
c = None
for f in sorted(COOKIE_DIR.glob("account*.txt")):
    if ".bak" in f.name: continue
    c = f.read_text(encoding="utf-8-sig").strip()
    if c: break
s = requests.Session()
s.headers.update({"User-Agent":"Mozilla/5.0","Cookie":c,"Referer":"https://www.bilibili.com/"})
nav = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=15).json()
wbi = nav["data"]["wbi_img"]
MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,34,44,52]
img = wbi["img_url"].rsplit("/",1)[-1].split(".")[0]
sub = wbi["sub_url"].rsplit("/",1)[-1].split(".")[0]
mixin = "".join((img+sub)[i] for i in MIXIN)[:32]

for kw in ["CMMI", "Cache命中率", "系统可靠性", "编译原理", "软件设计师冲刺"]:
    p = {"search_type":"video","keyword":kw,"page":1,"page_size":5}
    p["wts"] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(p.items()))
    p["w_rid"] = hashlib.md5((q+mixin).encode()).hexdigest()
    r = s.get("https://api.bilibili.com/x/web-interface/wbi/search/type", params=p, timeout=20).json()
    res = (r.get("data") or {}).get("result") or []
    print(f"\n[{kw}] {len(res)}个结果")
    for v in res[:3]:
        t = v.get("title","")[:40]
        a = v.get("author","")
        print(f"  - {t} | {a}")
    time.sleep(2)
