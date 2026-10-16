# -*- coding: utf-8 -*-
"""第三轮精准重搜：偏组修正 + 新增编译原理视频组。"""
import json, time, re, urllib.parse, hashlib, sys
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

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,
         12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,
         57,62,11,36,20,34,44,52]

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

# 第三轮：更精准的关键词
ROUND3 = {
    # 偏组终极修正
    "软件工程-内聚耦合": ["软件设计师 内聚类型 耦合类型 真题", "模块独立性 高内聚低耦合 软考"],
    "计组-可靠性": ["系统可靠性 串联 并联 计算 真题", "可靠性框图 软考 计算机"],
    "软件工程-CMMI": ["CMMI 五个等级 初始级 已管理级", "软件能力成熟度模型 CMMI3"],
    # 新增编译原理组
    "编译原理-编译过程": ["编译原理 词法分析 语法分析 语义分析", "编译器六个阶段 期末速成"],
    "编译原理-自动机正规式": ["有限自动机 DFA NFA 正规式", "编译原理 正规表达式 期末"],
    "编译原理-后缀式": ["中缀转后缀 逆波兰式 栈", "编译原理 后缀表达式 计算"],
    # 新增多媒体/图像容量
    "多媒体-图像容量": ["图像存储容量计算 像素 位深", "音频视频容量计算 计算机"],
}

data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
seen_bv = set()
for vids in data.values():
    for v in vids:
        seen_bv.add(v["bvid"])

for topic, kws in ROUND3.items():
    vids = []
    for kw in kws:
        try:
            res = search(kw)
            time.sleep(1.5)
            for v in res[:15]:
                bv = v.get("bvid")
                if not bv or bv in seen_bv: continue
                title = re.sub(r'<[^>]+>', '', v.get("title",""))
                vids.append({
                    "bvid": bv, "title": title, "author": v.get("author",""),
                    "play": v.get("play",0), "duration": v.get("duration",""),
                    "url": f"https://www.bilibili.com/video/{bv}", "keyword": kw,
                })
                seen_bv.add(bv)
        except Exception as e:
            print(f"  失败 [{kw}]: {e}")
            time.sleep(3)
    vids.sort(key=lambda x: -x["play"])
    data[topic] = vids[:10]
    print(f"[{topic}] {len(vids[:10])} 个视频")

JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n完成。总知识点组: {len(data)}")
