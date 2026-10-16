# -*- coding: utf-8 -*-
"""批量ASR转写：44个无AI字幕的视频，用FunASR paraformer-zh + GPU。"""
import json, os, sys, subprocess, pathlib, time

# 用现有Python环境
PY = r"D:\6_code\13_python\1_python3.11.0\python.exe"
FFMPEG = r"D:\6_code\36_ffmpeg\ffmpeg-8.1-full_build\bin\ffmpeg.exe"

BASE = pathlib.Path(r"D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\提不起精神-调研\衍生-学理解读\双轨策略-工作区\软考特攻")
OUT = BASE / "字幕"
TMP = BASE / "tmp_audio"
TMP.mkdir(exist_ok=True)

# 读取无字幕清单
no_sub = json.loads((BASE / "素材清单" / "无字幕视频清单.json").read_text(encoding="utf-8"))

# 只处理1P短视频（先处理快的）
short_videos = [v for v in no_sub if v.get("pages", 1) == 1]
long_videos = [v for v in no_sub if v.get("pages", 1) > 1]

print(f"1P短视频: {len(short_videos)}个（先处理这些）")
print(f"长视频(多P): {len(long_videos)}个（后面再说）")

# 写一个内部脚本给funasr用
inner_script = BASE / "_asr_inner.py"
inner_script.write_text(f'''
import sys, pathlib, json
import yt_dlp
from funasr import AutoModel

ffmpeg = r"{FFMPEG}"
tmp_dir = pathlib.Path(r"{TMP}")
out_dir = pathlib.Path(r"{OUT}")

model = AutoModel(model="paraformer-zh", vad_model="fsmn-vad", punc_model="ct-punc",
                  disable_update=True, device="cuda:0")

def download_audio(bvid):
    out = tmp_dir / f"{{bvid}}.wav"
    if out.exists() and out.stat().st_size > 10000:
        return str(out)
    ydl_opts = {{
        "format": "bestaudio/best",
        "outtmpl": str(tmp_dir / f"{{bvid}}.%(ext)s"),
        "quiet": True,
        "postprocessors": [{{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
            "preferredquality": "192",
        }}],
        "ffmpeg_location": ffmpeg,
    }}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"https://www.bilibili.com/video/{{bvid}}"])
    return str(out)

def asr_transcribe(wav_path, bvid, topic):
    res = model.generate(input=wav_path, batch_size_s=300)
    text = "".join(r["text"] for r in res)
    safe_topic = "".join(c if c not in r'\\\\/:*?"<>|' else "_" for c in topic)
    out_file = out_dir / f"{{safe_topic}}_{{bvid}}.md"
    out_file.write_text(f"# {{topic}}\\n\\n> 来源：https://www.bilibili.com/video/{{bvid}}\\n> 转写：FunASR paraformer-zh GPU\\n\\n{{text}}", encoding="utf-8")
    return len(text)

if __name__ == "__main__":
    bvid = sys.argv[1]
    topic = sys.argv[2]
    try:
        wav = download_audio(bvid)
        chars = asr_transcribe(wav, bvid, topic)
        print(f"OK: {{bvid}} {{chars}}字")
        # 删音频省空间
        os.remove(wav)
    except Exception as e:
        print(f"ERR: {{bvid}} {{e}}")
''', encoding="utf-8")

# 批量跑
results = []
for i, v in enumerate(short_videos):
    bvid = v["bvid"]
    topic = v["topic"]
    print(f"\\n[{i+1}/{len(short_videos)}] {{bvid}} {{topic[:30]}}")
    try:
        r = subprocess.run([PY, str(inner_script), bvid, topic],
                         capture_output=True, text=True, timeout=600, encoding="utf-8")
        print(r.stdout.strip())
        if r.returncode != 0:
            print("  stderr:", r.stderr[-200:] if r.stderr else "")
    except subprocess.TimeoutExpired:
        print("  超时")
    time.sleep(1)

print("\\n=== 完成 ===")
