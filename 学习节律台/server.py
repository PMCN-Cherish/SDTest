# -*- coding: utf-8 -*-
"""学习节律台 · 信号服务（仅标准库，无需安装依赖，纯本地不出网）

数据源
  1. WorkBuddy 会话记录  ~/.workbuddy/projects/<工作区名>/*.jsonl
     - message(role=user)        → 你的参与节律（主信号）
     - message(role=assistant)   → 对话往返
     - function_call             → 助手正在干活
  2. 工作区文件产出  被修改文件的 mtime → 学习产出信号

输出
  GET /            index.html
  GET /api/state   活动状态 JSON（BPM / 强度 / 空闲 / 今日统计 / 时间线）
  GET /api/assets  assets/ 下的音频文件列表
  GET /assets/xx   音频文件
"""
import glob
import json
import os
import time
from datetime import datetime
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(HERE)
WS_NAME = os.path.basename(WORKSPACE)
ASSETS = os.path.join(HERE, "assets")
PROJECTS = os.path.join(os.path.expanduser("~"), ".workbuddy", "projects")

PORT = 8790
WINDOW_MIN = 10.0
IDLE_GRACE_MIN = 3.0
IDLE_FULL_MIN = 20.0
FADE_FLOOR = 0.3
TARGET_SCORE = 25.0
BPM_MIN, BPM_MAX = 50, 140
W_USER, W_ASSIST, W_TOOL, W_FILE = 3.0, 1.0, 0.8, 2.0
PING_FILE = os.path.join(HERE, "manual-pings.jsonl")
SKIP_DIRS = {".git", ".workbuddy", ".vscode", "__pycache__", "学习节律台", "assets"}
AUDIO_EXT = {".mp3", ".m4a", ".ogg", ".wav", ".flac", ".aac"}


def session_files():
    if not os.path.isdir(PROJECTS):
        return []
    hits = []
    for d in os.listdir(PROJECTS):
        p = os.path.join(PROJECTS, d)
        if os.path.isdir(p) and d.endswith(WS_NAME):
            hits.extend(glob.glob(os.path.join(p, "*.jsonl")))
    return hits


def message_events():
    evs, seen = [], set()
    for f in session_files():
        try:
            with open(f, "r", encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        d = json.loads(line)
                    except Exception:
                        continue
                    eid = d.get("id")
                    if eid in seen:
                        continue
                    seen.add(eid)
                    ts = d.get("timestamp")
                    if not isinstance(ts, (int, float)):
                        continue
                    t = d.get("type")
                    if t == "message":
                        user = d.get("role") == "user"
                        evs.append({"ts": ts / 1000.0, "w": W_USER if user else W_ASSIST,
                                    "kind": "user" if user else "assistant"})
                    elif t == "function_call":
                        evs.append({"ts": ts / 1000.0, "w": W_TOOL, "kind": "tool"})
        except Exception:
            continue
    evs.sort(key=lambda e: e["ts"])
    return evs


def file_events(since):
    out, n = [], 0
    for root, dirs, files in os.walk(WORKSPACE):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            n += 1
            fp = os.path.join(root, name)
            try:
                mt = os.path.getmtime(fp)
            except OSError:
                continue
            if mt >= since:
                out.append({"ts": mt, "w": W_FILE, "kind": "file", "name": name})
    return out, n


def manual_events():
    if not os.path.isfile(PING_FILE):
        return []
    out = []
    try:
        with open(PING_FILE, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                ts = d.get("ts")
                if isinstance(ts, (int, float)):
                    out.append({"ts": ts, "w": W_USER, "kind": "ping"})
    except Exception:
        pass
    return out


def add_ping():
    with open(PING_FILE, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts": time.time(), "src": "manual"}, ensure_ascii=False) + "\n")


def midnight():
    d = datetime.now()
    return time.mktime(d.replace(hour=0, minute=0, second=0, microsecond=0).timetuple())


def compute_state():
    now = time.time()
    t0 = midnight()
    msg = message_events()
    files, ws_count = file_events(t0)
    ping = manual_events()
    all_ev = msg + files + ping
    today = [e for e in all_ev if e["ts"] >= t0]
    recent = [e for e in all_ev if e["ts"] >= now - 3600]

    score = sum(e["w"] for e in recent if e["ts"] >= now - WINDOW_MIN * 60)
    intensity = min(1.0, score / TARGET_SCORE)

    last_ts = max([e["ts"] for e in all_ev], default=0.0)
    idle_min = (now - last_ts) / 60.0 if last_ts else 999.0
    if idle_min <= IDLE_GRACE_MIN:
        ramp = 1.0
    elif idle_min >= IDLE_FULL_MIN:
        ramp = 0.0
    else:
        ramp = 1.0 - (idle_min - IDLE_GRACE_MIN) / (IDLE_FULL_MIN - IDLE_GRACE_MIN)
    fade = round(FADE_FLOOR + (1.0 - FADE_FLOOR) * ramp, 3)

    bpm = int(round(BPM_MIN + (BPM_MAX - BPM_MIN) * intensity * fade))
    volume = round((0.22 + 0.78 * intensity) * fade, 3)

    if ramp <= 0.001:
        status, hint = "降至最缓", "空闲 %.0f 分钟，音乐停在最低档" % idle_min
    elif ramp < 1.0:
        status, hint = "慢下来了", "距上次活动 %.0f 分钟" % idle_min
    elif intensity >= 0.75:
        status, hint = "全速推进", "近 10 分钟高强度"
    elif intensity >= 0.35:
        status, hint = "进行中", "节奏稳定"
    else:
        status, hint = "刚起步", "近 10 分钟活动较少"

    buckets = [0.0] * 60
    for e in recent:
        i = int((now - e["ts"]) // 60)
        if 0 <= i < 60:
            buckets[59 - i] += e["w"]
    peak = max(buckets) or 1.0
    timeline = [round(min(1.0, v / peak), 3) for v in buckets]

    streak = 0
    for v in reversed(buckets):
        if v <= 0:
            break
        streak += 1

    def minutes_of(evs):
        return len({int(e["ts"] // 60) for e in evs})

    def count(evs, kind):
        return sum(1 for e in evs if e["kind"] == kind)

    return {
        "now": now,
        "bpm": bpm,
        "intensity": round(intensity, 3),
        "volume": volume,
        "fade": round(fade, 3),
        "status": status,
        "hint": hint,
        "ramp": round(ramp, 3),
        "idle_min": round(idle_min, 1) if last_ts else None,
        "window_score": round(score, 2),
        "streak_min": streak,
        "timeline": timeline,
        "today": {
            "user_msgs": count(today, "user"),
            "assist_msgs": count(today, "assistant"),
            "tool_calls": count(today, "tool"),
            "pings": count(today, "ping"),
            "files": len({e.get("name") for e in today if e["kind"] == "file"}),
            "active_min": minutes_of(today),
        },
        "sources": {"sessions": len(session_files()), "events": len(msg), "workspace_files": ws_count},
    }


def list_assets():
    if not os.path.isdir(ASSETS):
        return []
    return sorted(f for f in os.listdir(ASSETS) if os.path.splitext(f)[1].lower() in AUDIO_EXT)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        b = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(b)
        except Exception:
            pass

    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if path in ("/", "/index.html"):
            p = os.path.join(HERE, "index.html")
            if os.path.isfile(p):
                with open(p, "rb") as fh:
                    self._send(200, fh.read(), "text/html; charset=utf-8")
            else:
                self._send(404, "index.html 缺失")
        elif path == "/api/state":
            self._send(200, json.dumps(compute_state(), ensure_ascii=False))
        elif path == "/api/assets":
            self._send(200, json.dumps(list_assets(), ensure_ascii=False))
        elif path == "/api/ping":
            try:
                add_ping()
                self._send(200, json.dumps({"ok": True}))
            except Exception as e:
                self._send(500, json.dumps({"ok": False, "err": str(e)}, ensure_ascii=False))
        elif path.startswith("/assets/"):
            name = os.path.basename(path)
            fp = os.path.join(ASSETS, name)
            if os.path.isfile(fp):
                ctype = "audio/mpeg" if name.lower().endswith(".mp3") else "application/octet-stream"
                with open(fp, "rb") as fh:
                    self._send(200, fh.read(), ctype)
            else:
                self._send(404, b"")
        elif path == "/favicon.ico":
            self._send(204, b"")
        else:
            self._send(404, json.dumps({"error": "not found"}))


def main():
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print("学习节律台已启动： http://127.0.0.1:%d" % PORT)
    print("工作区: %s" % WORKSPACE)
    print("会话文件: %d 个" % len(session_files()))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
