# -*- coding: utf-8 -*-
"""统计02知识点分解各模块考点数，生成模块进度总览表"""
import re
from pathlib import Path

BASE = Path(r"D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\提不起精神-调研\衍生-学理解读\双轨策略-工作区")
F02 = BASE / "考试备考系统" / "02-知识点分解.md"

lines = F02.read_text(encoding="utf-8").splitlines()

modules = []  # [(module_name, sub_count_dict)]
cur_mod = None
cur_sub = None

for line in lines:
    s = line.strip()
    m2 = re.match(r'^## (.+)', s)
    m3 = re.match(r'^### (.+)', s)
    # ⚠️ 为双码位(U+26A0 U+FE0F)，须整串匹配，否则漏统计
    mk = re.match(r'^- (⚠️|⬜|🔵|✅)\s+(.+)', s)
    if m2 and not s.startswith('## 掌握率'):
        cur_mod = m2.group(1)
        modules.append({"name": cur_mod, "subs": {}, "total": 0, "states": {"⬜":0,"🔵":0,"✅":0,"⚠️":0}})
        cur_sub = None
    elif m3 and modules:
        cur_sub = m3.group(1)
        modules[-1]["subs"][cur_sub] = 0
    elif mk and modules:
        state = mk.group(1)
        modules[-1]["total"] += 1
        modules[-1]["states"][state] += 1
        if cur_sub:
            modules[-1]["subs"][cur_sub] += 1

# 输出
print("=== 各模块格数统计 ===")
grand_total = 0
for m in modules:
    grand_total += m["total"]
    print(f"\n{m['name']}：{m['total']}格")
    for sub, cnt in m["subs"].items():
        if cnt > 0:
            print(f"  {sub}: {cnt}格")

print(f"\n=== 总计：{grand_total}格 ===")

# 生成进度总览表
print("\n=== 模块进度总览表（模板）===")
print("| 模块 | 总格数 | ✅已掌握 | 🔵学习中 | ⚠️待攻克 | ⬜未开始 | 掌握率 |")
print("|---|---|---|---|---|---|---|")
for m in modules:
    print(f"| {m['name']} | {m['total']} | 0 | 0 | 0 | {m['total']} | 0% |")
print(f"| **合计** | **{grand_total}** | 0 | 0 | 0 | {grand_total} | 0% |")
