# -*- coding: utf-8 -*-
"""重搜偏组+新增考点组的视频，结果追加到JSON。"""
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

# 偏组重搜 + 新增考点组
RESEARCH = {
    # 偏组重搜（换精准关键词）
    "软件工程-内聚耦合": ["软件设计师 内聚 耦合 类型", "软考 模块独立性 耦合度"],
    "计组-IO中断DMA": ["计算机组成原理 中断方式 DMA方式", "IO控制方式 程序查询 中断 DMA"],
    "计组-可靠性": ["系统可靠性计算 串联并联 软考", "可靠性MTBF MTTF 计算机"],
    "操作系统-文件索引": ["操作系统 文件管理 索引节点 位示图", "文件系统 磁盘空间管理 操作系统"],
    # 新增考点组
    "软件工程-CMMI": ["CMMI 软件成熟度等级", "软考 软件过程改进"],
    "软件工程-数据字典": ["数据字典 数据流图 软件工程", "结构化分析 数据字典 四类条目"],
    "操作系统-进程调度": ["进程调度算法 FCFS SJF 时间片轮转", "短作业优先 多级反馈队列"],
    "数据库-三级模式": ["数据库三级模式两级映像", "数据库系统 外模式 模式 内模式"],
    "网络-加密防火墙": ["对称加密 非对称加密 RSA 数字签名", "防火墙 包过滤 应用网关"],
    "OOP-SOLID": ["SOLID设计原则 开闭原则", "里氏替换 依赖倒置 设计原则"],
}

# 加载现有JSON
data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
seen_bv = set()
for vids in data.values():
    for v in vids:
        seen_bv.add(v["bvid"])

for topic, kws in RESEARCH.items():
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
