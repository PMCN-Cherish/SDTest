# -*- coding: utf-8 -*-
"""从知识地图提取考点结构，生成02-知识点分解.md"""
import re
from pathlib import Path

BASE = Path(r"D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\提不起精神-调研\衍生-学理解读\双轨策略-工作区")
MAP = BASE / "软考特攻" / "01-知识地图-L3.md"
OUT = BASE / "考试备考系统" / "02-知识点分解.md"

lines = MAP.read_text(encoding="utf-8").splitlines()

# 结构：## 模块（上午题9模块/下午题5题）→ ### 子模块 → - **考点**
sections = {}  # section_title -> {sub_title -> [kaodian]}
cur_sec = None
cur_sub = None
kaodian_count = 0

for line in lines:
    s = line.strip()
    m2 = re.match(r'^## (.+)', s)
    m3 = re.match(r'^### (.+)', s)
    mk = re.match(r'^- \*\*(.+?)\*\*：', s)
    if m2 and not s.startswith('## 目录'):
        cur_sec = m2.group(1)
        sections.setdefault(cur_sec, {})
        cur_sub = None
    elif m3:
        cur_sub = m3.group(1)
        if cur_sec:
            sections[cur_sec].setdefault(cur_sub, [])
    elif mk and cur_sec and not s.startswith('- ['):
        name = mk.group(1)
        if cur_sub:
            sections[cur_sec][cur_sub].append(name)
        else:
            sections[cur_sec].setdefault("(直属)", []).append(name)
        kaodian_count += 1

# 只保留上午题9模块和下午题部分（跳过易混点/冲突表）
keep_prefixes = ["①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "题1", "题2", "题3", "题4", "题5"]

out_lines = []
out_lines.append("# 知识点分解\n")
out_lines.append("> 来源：`软考特攻\\01-知识地图-L3.md`（173 条考点，L3 颗粒度）")
out_lines.append("> 状态：⬜ 未开始 / 🔵 学习中 / ✅ 已掌握（能独立解题）/ ⚠️ 待攻克（反复出错）")
out_lines.append("> 初始全部 ⬜，随每日学习按「能否独立提取」更新\n")

count = 0
for sec, subs in sections.items():
    if not any(sec.startswith(p) for p in keep_prefixes):
        continue
    out_lines.append(f"## {sec}")
    for sub, kds in subs.items():
        out_lines.append(f"### {sub}")
        for kd in kds:
            out_lines.append(f"- ⬜ {kd}")
            count += 1
    out_lines.append("")

out_lines.append("---\n")
out_lines.append("## 掌握率统计（每周日更新）\n")
out_lines.append("| 周次 | 总知识点 | 已掌握 | 掌握率 | 待攻克 |")
out_lines.append("|---|---|---|---|---|")
out_lines.append("| W42（10/12-10/18） | | | | |")
out_lines.append("| W43（10/19-10/25） | | | | |")

OUT.write_text("\n".join(out_lines), encoding="utf-8")
print(f"02 已生成：{count} 条考点")
