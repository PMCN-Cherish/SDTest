# -*- coding: utf-8 -*-
"""最终修正：用简单关键词重搜偏组，直接替换。"""
import json, time, re, urllib.parse, hashlib
from pathlib import Path
import requests

COOKIE_DIR = Path(r"D:\11.project\iwen-codex\bilibili-cookies")
BASE = Path(r"D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\提不起精神-调研\衍生-学理解读\双轨策略-工作区\软考特攻")
JSON_PATH = BASE / "素材清单" / "视频样本清单.json"

def load_cookie():
    for f in sorted(COOKIE_DIR.glob("account*.txt")):
        if ".bak" in f.name: continue
        c = f.read_text(encoding="utf-8-sig").strip()
        if c: return c
    raise RuntimeError("no cookie")

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,34,44,52]

s = requests.Session()
s.headers.update({"User-Agent":"Mozilla/5.0","Cookie":load_cookie(),"Referer":"https://www.bilibili.com/"})
nav = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=15).json()
wbi = nav["data"]["wbi_img"]
img = wbi["img_url"].rsplit("/",1)[-1].split(".")[0]
sub = wbi["sub_url"].rsplit("/",1)[-1].split(".")[0]
mixin = "".join((img+sub)[i] for i in MIXIN)[:32]

def sign(p):
    p=dict(p); p["wts"]=str(int(time.time()))
    q=urllib.parse.urlencode(sorted(p.items()))
    p["w_rid"]=hashlib.md5((q+mixin).encode()).hexdigest()
    return p

def search(kw, page=1):
    p=sign({"search_type":"video","keyword":kw,"page":page,"page_size":30})
    r=s.get("https://api.bilibili.com/x/web-interface/wbi/search/type",params=p,timeout=20).json()
    return (r.get("data") or {}).get("result") or []

# 简单关键词
FIX = {
    "软件工程-CMMI": ["CMMI", "软件能力成熟度"],
    "软件工程-测试": ["白盒测试 覆盖", "黑盒测试 等价类"],
    "软件工程-维护": ["软件维护 类型", "软件工程 维护"],
    "计组-Cache存储": ["Cache命中率", "高速缓存 映射"],
    "计组-可靠性": ["系统可靠性 串联并联", "可靠性计算"],
    "编译原理-编译过程": ["编译原理 期末速成", "编译器 阶段"],
    "整体-串讲": ["软件设计师冲刺", "软考软件设计师 押题"],
    "整体-经验": ["软件设计师 上岸", "软考中级 经验分享"],
}

data = json.loads(JSON_PATH.read_text(encoding="utf-8"))

for topic, kws in FIX.items():
    vids = []
    for kw in kws:
        try:
            res = search(kw)
            time.sleep(2)
            for v in res[:15]:
                bv = v.get("bvid")
                if not bv: continue
                title = re.sub(r'<[^>]+>', '', v.get("title",""))
                vids.append({
                    "bvid": bv, "title": title, "author": v.get("author",""),
                    "play": v.get("play",0), "duration": v.get("duration",""),
                    "url": f"https://www.bilibili.com/video/{bv}", "keyword": kw,
                })
        except Exception as e:
            print(f"  失败 [{kw}]: {e}")
            time.sleep(3)
    seen = set()
    uniq = []
    for v in vids:
        if v["bvid"] not in seen:
            seen.add(v["bvid"])
            uniq.append(v)
    uniq.sort(key=lambda x: -x["play"])
    data[topic] = uniq[:10]
    print(f"[{topic}] {len(uniq[:10])} 个")
    for v in uniq[:3]:
        print(f"  {v['title'][:40]} | {v['author']}")

JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n完成。总组: {len(data)}")
