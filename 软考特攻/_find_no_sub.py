import json
from pathlib import Path

BASE = Path(r"D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\提不起精神-调研\衍生-学理解读\双轨策略-工作区\软考特攻")

# 读取抓取结果
results = json.loads((BASE / "素材清单" / "全量字幕抓取结果.json").read_text(encoding="utf-8"))

# 找出无字幕的
no_sub = [r for r in results if r["status"] == "no_sub"]
print(f"无字幕视频: {len(no_sub)}个")
for r in no_sub:
    print(f"  {r['bvid']} | {r['topic']} | {r.get('pages','?')}P")

# 保存清单
(BASE / "素材清单" / "无字幕视频清单.json").write_text(json.dumps(no_sub, ensure_ascii=False, indent=2), encoding="utf-8")
