# -*- coding: utf-8 -*-
"""给知识地图所有考点追加状态字段：状态(掌握度) + 素材出现次数"""
import json, re
from pathlib import Path

BASE = Path(r"D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\提不起精神-调研\衍生-学理解读\双轨策略-工作区\软考特攻")
MAP = BASE / "01-知识地图-L3.md"

stats = json.loads((BASE / "素材清单" / "考点出现次数统计.json").read_text(encoding="utf-8"))
stat_map = {r["name"]: r for r in stats}
print(f"统计条目: {len(stat_map)}")

lines = MAP.read_text(encoding="utf-8").splitlines()
new_lines = []
added = 0
i = 0
while i < len(lines):
    line = lines[i]
    m = re.match(r'^- \*\*(.+?)\*\*：', line.strip())
    if m and not line.strip().startswith('- ['):
        name = m.group(1).strip()
        stat = stat_map.get(name)
        if stat:
            count = stat.get("count", 0)
            docs = stat.get("docs", 0)
            suffix = f"｜ 状态：⚪未掌握 ｜ 素材：{count}次/{docs}篇"
            if i + 1 < len(lines) and lines[i+1].strip().startswith('- 考频'):
                meta = lines[i+1]
                if '状态：' not in meta:
                    new_lines.append(line)
                    new_lines.append(meta + suffix)
                    added += 1
                    i += 2
                    continue
                else:
                    new_lines.append(line)
                    new_lines.append(meta)
                    added += 1
                    i += 2
                    continue
            else:
                new_lines.append(line)
                new_lines.append(f"  - 状态：⚪未掌握 ｜ 素材：{count}次/{docs}篇")
                added += 1
                i += 1
                continue
    new_lines.append(line)
    i += 1

MAP.write_text("\n".join(new_lines), encoding="utf-8")
print(f"已更新 {added} 条考点状态字段")
