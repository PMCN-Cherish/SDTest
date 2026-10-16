# -*- coding: utf-8 -*-
"""自动统计02知识点分解各模块状态，更新顶部进度总览表"""
import re
from pathlib import Path

BASE = Path(r"D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\提不起精神-调研\衍生-学理解读\双轨策略-工作区")
F02 = BASE / "考试备考系统" / "02-知识点分解.md"

lines = F02.read_text(encoding="utf-8").splitlines()

modules = []
cur_mod = None

for line in lines:
    s = line.strip()
    m2 = re.match(r'^## (.+)', s)
    # 注意：⚠️ 由 U+26A0 + U+FE0F 两个码位组成，不能用单字符类 [⬜🔵✅⚠️]（会漏匹配），必须整串匹配
    mk = re.match(r'^- (⚠️|⬜|🔵|✅)\s+(.+)', s)
    if m2 and not s.startswith('## 掌握率') and not s.startswith('## 模块进度'):
        cur_mod = m2.group(1)
        modules.append({"name": cur_mod, "total": 0, "states": {"⬜":0,"🔵":0,"✅":0,"⚠️":0}})
    elif mk and modules:
        state = mk.group(1)
        modules[-1]["total"] += 1
        modules[-1]["states"][state] += 1

# 生成新的进度表
table_lines = []
table_lines.append("| 模块 | 总格数 | ✅已掌握 | 🔵学习中 | ⚠️待攻克 | ⬜未开始 | 掌握率 |")
table_lines.append("|---|---|---|---|---|---|---|")
grand = {"total":0,"✅":0,"🔵":0,"⚠️":0,"⬜":0}
for m in modules:
    rate = f"{m['states']['✅']}/{m['total']}" if m['total'] > 0 else "0%"
    pct = f"{m['states']['✅']*100//m['total']}%" if m['total'] > 0 else "0%"
    table_lines.append(f"| {m['name']} | {m['total']} | {m['states']['✅']} | {m['states']['🔵']} | {m['states']['⚠️']} | {m['states']['⬜']} | {pct} |")
    for k in grand: grand[k] += m["states"].get(k, 0) if k != "total" else 0
    grand["total"] += m["total"]
grand_pct = f"{grand['✅']*100//grand['total']}%" if grand['total'] > 0 else "0%"
table_lines.append(f"| **合计** | **{grand['total']}** | {grand['✅']} | {grand['🔵']} | {grand['⚠️']} | {grand['⬜']} | {grand_pct} |")

# 替换文件中的进度表
new_lines = []
in_table = False
table_done = False
for line in lines:
    if line.startswith("## 模块进度总览"):
        in_table = True
        new_lines.append(line)
        new_lines.append("")
        new_lines.extend(table_lines)
        table_done = True
        continue
    if in_table:
        if line.startswith("---") or line.startswith("## "):
            in_table = False
            new_lines.append("")
            new_lines.append(line)
        continue
    new_lines.append(line)

F02.write_text("\n".join(new_lines), encoding="utf-8")

print(f"进度表已更新。总计 {grand['total']} 格")
print(f"✅已掌握: {grand['✅']}  🔵学习中: {grand['🔵']}  ⚠️待攻克: {grand['⚠️']}  ⬜未开始: {grand['⬜']}")
print(f"掌握率: {grand_pct}")
