# -*- coding: utf-8 -*-
"""批量ASR转写44个无字幕视频。"""
import sys, os, json, pathlib, time

# ffmpeg加到PATH
os.environ["PATH"] = r"D:\6_code\36_ffmpeg\ffmpeg-8.1-full_build\bin;" + os.environ["PATH"]

import yt_dlp
from funasr import AutoModel

BASE = pathlib.Path(r"D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\提不起精神-调研\衍生-学理解读\双轨策略-工作区\软考特攻")
TMP = BASE / "tmp_audio"
TMP.mkdir(exist_ok=True)
OUT = BASE / "字幕"

# 加载无字幕清单
no_sub = json.loads((BASE / "素材清单" / "无字幕视频清单.json").read_text(encoding="utf-8"))

# 加载模型（只加载一次）
print("加载模型...")
model = AutoModel(model="paraformer-zh", vad_model="fsmn-vad", punc_model="ct-punc",
                  disable_update=True, device="cuda:0")
print("模型加载完成")

results = []
for i, v in enumerate(no_sub):
    bvid = v["bvid"]
    topic = v["topic"]
    pages = v.get("pages", 1)
    
    # 跳过已存在的
    safe_topic = "".join(c if c not in '\\/:*?"<>|' else "_" for c in topic)
    out_file = OUT / f"{safe_topic}_{bvid}.md"
    if out_file.exists() and out_file.stat().st_size > 1000:
        print(f"[{i+1}/{len(no_sub)}] {bvid} - 已存在，跳过")
        results.append({"bvid":bvid,"topic":topic,"status":"already"})
        continue
    
    print(f"[{i+1}/{len(no_sub)}] {bvid} {topic[:20]} ({pages}P)")
    
    try:
        # 下载音频
        wav_path = TMP / f"{bvid}.wav"
        if not wav_path.exists():
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": str(TMP / f"{bvid}.%(ext)s"),
                "quiet": True,
                "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "wav", "preferredquality": "192"}],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"https://www.bilibili.com/video/{bvid}"])
        
        # ASR转写
        res = model.generate(input=str(wav_path), batch_size_s=300)
        text = "".join(r["text"] for r in res)
        
        out_file.write_text(f"# {topic}\n\n> 来源：https://www.bilibili.com/video/{bvid}\n> 转写：FunASR paraformer-zh GPU\n\n{text}", encoding="utf-8")
        
        print(f"  ✅ {len(text)}字")
        results.append({"bvid":bvid,"topic":topic,"status":"ok","chars":len(text)})
        
        # 删音频
        os.remove(wav_path)
        
    except Exception as e:
        print(f"  ❌ {str(e)[:80]}")
        results.append({"bvid":bvid,"topic":topic,"status":"error","err":str(e)[:100]})
    
    time.sleep(1)

# 保存结果
(BASE / "素材清单" / "ASR转写结果.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

ok = sum(1 for r in results if r["status"]=="ok")
already = sum(1 for r in results if r["status"]=="already")
err = sum(1 for r in results if r["status"]=="error")
print(f"\n=== 完成 ===")
print(f"成功: {ok} | 已存在: {already} | 失败: {err}")
