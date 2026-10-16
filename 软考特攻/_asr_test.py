# -*- coding: utf-8 -*-
"""单视频ASR测试"""
import sys, os, pathlib

# 把ffmpeg加到PATH
os.environ["PATH"] = r"D:\6_code\36_ffmpeg\ffmpeg-8.1-full_build\bin;" + os.environ["PATH"]

import yt_dlp
from funasr import AutoModel

FFMPEG = r"D:\6_code\36_ffmpeg\ffmpeg-8.1-full_build\bin\ffmpeg.exe"
BASE = pathlib.Path(r"D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\提不起精神-调研\衍生-学理解读\双轨策略-工作区\软考特攻")
TMP = BASE / "tmp_audio"
TMP.mkdir(exist_ok=True)
OUT = BASE / "字幕"

bvid = sys.argv[1] if len(sys.argv) > 1 else "BV1iY3y6UEsa"
topic = sys.argv[2] if len(sys.argv) > 2 else "软件工程-内聚耦合"

print(f"加载模型...")
model = AutoModel(model="paraformer-zh", vad_model="fsmn-vad", punc_model="ct-punc",
                  disable_update=True, device="cuda:0")
print("模型加载完成")

# 下载音频
wav_path = TMP / f"{bvid}.wav"
if not wav_path.exists():
    print(f"下载音频 {bvid}...")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(TMP / f"{bvid}.%(ext)s"),
        "quiet": True,
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "wav", "preferredquality": "192"}],
        "ffmpeg_location": FFMPEG,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"https://www.bilibili.com/video/{bvid}"])

print(f"ASR转写...")
res = model.generate(input=str(wav_path), batch_size_s=300)
text = "".join(r["text"] for r in res)

safe_topic = "".join(c if c not in '\\/:*?"<>|' else "_" for c in topic)
out_file = OUT / f"{safe_topic}_{bvid}.md"
out_file.write_text(f"# {topic}\n\n> 来源：https://www.bilibili.com/video/{bvid}\n> 转写：FunASR paraformer-zh GPU\n\n{text}", encoding="utf-8")

print(f"完成: {len(text)}字 -> {out_file.name}")
os.remove(wav_path)
