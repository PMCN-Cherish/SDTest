# -*- coding: utf-8 -*-
"""全量抓取：遍历415个视频，每个获取分P，逐P抓AI字幕。"""
import requests, time, re, json, urllib.parse, hashlib
from pathlib import Path

COOKIE_DIR = Path(r"D:\11.project\iwen-codex\bilibili-cookies")
BASE = Path(r"D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\提不起精神-调研\衍生-学理解读\双轨策略-工作区\软考特攻")
OUT = BASE / "字幕"
OUT.mkdir(exist_ok=True)

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

def get_video_info(bvid):
    """获取视频分P列表和每个P的cid"""
    try:
        r = s.get(f"https://www.bilibili.com/video/{bvid}/", timeout=20)
        # 提取分P列表
        pages = []
        # 尝试从INITIAL_STATE提取
        m = re.search(r'"pages":(\[.*?\])', r.text)
        if m:
            try:
                pages = json.loads(m.group(1))
            except:
                pass
        # 如果没拿到，至少拿第一P的cid
        if not pages:
            cid_m = re.search(r'"cid":(\d+)', r.text)
            aid_m = re.search(r'"aid":(\d+)', r.text)
            title_m = re.search(r'"title":"([^"]+)"', r.text)
            if cid_m:
                pages = [{"cid": int(cid_m.group(1)), "part": title_m.group(1) if title_m else "P1", "page": 1}]
        return pages
    except Exception as e:
        return []

def get_subtitle(bvid, cid):
    try:
        p = sign({"bvid":bvid,"cid":str(cid),"web_location":"333.1007"})
        r = s.get("https://api.bilibili.com/x/player/wbi/v2", params=p, timeout=15).json()
        subs = (r.get("data") or {}).get("subtitle") or {}
        list_ = subs.get("subtitles") or []
        if not list_: return None
        for item in list_:
            if "zh" in item.get("lan",""):
                return "https:" + item["subtitle_url"]
        return "https:" + list_[0]["subtitle_url"]
    except:
        return None

def download_sub(url):
    try:
        r = s.get(url, timeout=15).json()
        body = r.get("body") or []
        return "\n".join(item.get("content","") for item in body)
    except:
        return ""

# 读取视频清单
data = json.loads((BASE / "素材清单" / "视频样本清单.json").read_text(encoding="utf-8"))

# 收集所有bvid
all_videos = []
for topic, vids in data.items():
    for v in vids:
        all_videos.append({"bvid": v["bvid"], "title": v["title"], "topic": topic})

print(f"共{len(all_videos)}个视频待处理")

results = []
for i, v in enumerate(all_videos):
    bvid = v["bvid"]
    topic = v["topic"]
    title = v["title"][:30]
    
    # 跳过已抓的
    safe_topic = re.sub(r'[\\/:*?"<>|]', '_', topic)
    out_file = OUT / f"{safe_topic}_{bvid}.md"
    if out_file.exists() and out_file.stat().st_size > 500:
        results.append({"bvid":bvid,"topic":topic,"status":"already"})
        continue
    
    try:
        pages = get_video_info(bvid)
        if not pages:
            results.append({"bvid":bvid,"topic":topic,"status":"no_pages"})
            print(f"[{i+1}/{len(all_videos)}] {topic[:20]} - 无分P")
            time.sleep(0.5)
            continue
        
        all_text = []
        has_sub = False
        for p in pages:
            cid = p["cid"]
            sub_url = get_subtitle(bvid, cid)
            time.sleep(0.3)
            if sub_url:
                text = download_sub(sub_url)
                time.sleep(0.3)
                if text:
                    all_text.append(f"## {p.get('part','P'+str(p.get('page',1)))}\n\n{text}")
                    has_sub = True
        
        if has_sub:
            content = f"# {title}\n\n> 来源：https://www.bilibili.com/video/{bvid}\n> 模块：{topic}\n\n" + "\n\n".join(all_text)
            out_file.write_text(content, encoding="utf-8")
            total_chars = sum(len(t) for t in all_text)
            results.append({"bvid":bvid,"topic":topic,"status":"ok","chars":total_chars,"pages":len(pages)})
            print(f"[{i+1}/{len(all_videos)}] {topic[:20]} - ✅ {total_chars}字/{len(pages)}P")
        else:
            results.append({"bvid":bvid,"topic":topic,"status":"no_sub","pages":len(pages)})
            print(f"[{i+1}/{len(all_videos)}] {topic[:20]} - ❌ 无AI字幕/{len(pages)}P")
        
        time.sleep(0.8)
    except Exception as e:
        results.append({"bvid":bvid,"topic":topic,"status":"error","err":str(e)[:50]})
        print(f"[{i+1}/{len(all_videos)}] {topic[:20]} - ❌ {str(e)[:40]}")
        time.sleep(1)

# 保存结果
(BASE / "素材清单" / "全量字幕抓取结果.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

ok = sum(1 for r in results if r["status"]=="ok")
no_sub = sum(1 for r in results if r["status"]=="no_sub")
already = sum(1 for r in results if r["status"]=="already")
err = sum(1 for r in results if r["status"]=="error")
print(f"\n=== 完成 ===")
print(f"有字幕: {ok} | 无字幕: {no_sub} | 已存在: {already} | 错误: {err}")
print(f"总视频: {len(results)}")
