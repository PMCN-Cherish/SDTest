# -*- coding: utf-8 -*-
"""批量抓取核心视频的B站AI字幕，存到本地。"""
import requests, time, re, json, urllib.parse, hashlib
from pathlib import Path

COOKIE_DIR = Path(r"D:\11.project\iwen-codex\bilibili-cookies")
BASE = Path(r"D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\提不起精神-调研\衍生-学理解读\双轨策略-工作区\软考特攻")
OUT = BASE / "字幕"
OUT.mkdir(exist_ok=True)

# 核心视频清单（优先转写这些）
CORE_BVIDS = [
    # zst_2001 模块真题系列
    ("BV1ym4y1D7RW", "zst上午题#1-计算机系统"),
    ("BV1Qr4y167cX", "zst上午题#5-知识产权"),
    ("BV1LZ4y1k7ma", "zst上午题#6-数据库"),
    ("BV1a44y1K7HH", "zst上午题#8-UML"),
    ("BV18L4y1M7Bd", "zst上午题#9-设计模式"),
    ("BV1AY411E7GC", "zst上午题#10-操作系统"),
    ("BV1gU4y1U72k", "zst上午题#15-计算机网络"),
    ("BV1ai4y1f7ot", "zst下午题#1-DFD"),
    ("BV1x34y1k7ZE", "zst下午题#2-试题二"),
    ("BV11Z4y1z7Uc", "zst下午题#3-UML"),
    ("BV1XT4y1v7ih", "zst下午题#4-设计模式代码"),
    # 高价值长视频
    ("BV1rc411t71D", "学以致知-系统精讲807min"),
    ("BV13iDvBVENd", "软考小灵通-保姆级5011min"),
    ("BV15WkVBYEG8", "半岛阳光-完整版4025min"),
    # 精品短视频
    ("BV1Wu4y1Y7ya", "肥猫简图-UML类图6min"),
    ("BV1qN41177fw", "肥猫简图-UML用例图6min"),
    ("BV1YM411f7dr", "肥猫简图-UML时序图5min"),
    ("BV1af421z7Hk", "圆酱-PV秒杀12min"),
    ("BV1rJ411p7au", "山大小佛爷-银行家算法12min"),
    ("BV1Tx4y1a7zm", "Beokayy-流水线52min"),
    ("BV1hd4y1m7yC", "Beokayy-分页存储16min"),
    ("BV1cd4y1o7op", "土豆-CRC校验6min"),
    ("BV1zL4y1A785", "甜甜的酒儿-白盒测试17min"),
    ("BV1zz4y1m7Nq", "从0开始数-Dijkstra5min"),
    ("BV1wG411z79G", "蓝不过海-PrimKruskal16min"),
    ("BV1Ub4y147Zv", "阿琛-二叉树遍历3min"),
    ("BV1be4y1i78u", "Please907-子网划分39min"),
    ("BV1af4y1y7sS", "子烁-单例模式5min"),
    ("BV1vg4y1v7V4", "子烁-观察者模式4min"),
    ("BV1vT4y1E7g6", "子烁-策略模式5min"),
]

def load_cookie():
    for f in sorted(COOKIE_DIR.glob("account*.txt")):
        if ".bak" in f.name: continue
        c = f.read_text(encoding="utf-8-sig").strip()
        if c: return c
    raise RuntimeError("no cookie")

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,34,44,52]

s = requests.Session()
s.headers.update({"User-Agent":"Mozilla/5.0","Cookie":load_cookie(),"Referer":"https://www.bilibili.com/"})

# 获取wbi签名用的img/sub
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

def get_cid(bvid):
    """从网页HTML提取cid和aid"""
    r = s.get(f"https://www.bilibili.com/video/{bvid}/", timeout=20)
    m = re.search(r'"cid":(\d+)', r.text)
    aid_m = re.search(r'"aid":(\d+)', r.text)
    cid = m.group(1) if m else None
    aid = aid_m.group(1) if aid_m else None
    return cid, aid

def get_subtitle(bvid, cid):
    """获取AI字幕URL"""
    p = sign({"bvid":bvid,"cid":str(cid),"web_location":"333.1007"})
    r = s.get("https://api.bilibili.com/x/player/wbi/v2", params=p, timeout=20).json()
    subs = (r.get("data") or {}).get("subtitle") or {}
    list_ = subs.get("subtitles") or []
    if not list_: return None
    # 优先中文
    for item in list_:
        if "zh" in item.get("lan",""):
            return "https:" + item["subtitle_url"]
    return "https:" + list_[0]["subtitle_url"]

def download_sub(url):
    """下载字幕JSON并提取纯文本"""
    r = s.get(url, timeout=20).json()
    body = r.get("body") or []
    lines = []
    for item in body:
        lines.append(item.get("content",""))
    return "\n".join(lines)

results = []
for bvid, name in CORE_BVIDS:
    try:
        cid, aid = get_cid(bvid)
        if not cid:
            print(f"[{name}] 无cid")
            results.append({"bvid":bvid,"name":name,"status":"no_cid"})
            continue
        time.sleep(0.5)
        sub_url = get_subtitle(bvid, cid)
        if not sub_url:
            print(f"[{name}] 无AI字幕")
            results.append({"bvid":bvid,"name":name,"status":"no_subtitle"})
            continue
        time.sleep(0.5)
        text = download_sub(sub_url)
        # 保存
        safe_name = re.sub(r'[\\/:*?"<>|]', '_', name)
        (OUT / f"{safe_name}.md").write_text(f"# {name}\n\n> 来源：https://www.bilibili.com/video/{bvid}\n\n{text}", encoding="utf-8")
        print(f"[{name}] ✅ {len(text)}字")
        results.append({"bvid":bvid,"name":name,"status":"ok","chars":len(text)})
        time.sleep(1)
    except Exception as e:
        print(f"[{name}] ❌ {e}")
        results.append({"bvid":bvid,"name":name,"status":"error","err":str(e)})
        time.sleep(2)

# 保存结果
(BASE / "素材清单" / "字幕抓取结果.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
ok = sum(1 for r in results if r["status"]=="ok")
print(f"\n完成: {ok}/{len(CORE_BVIDS)} 个视频字幕已抓取到 {OUT}")
