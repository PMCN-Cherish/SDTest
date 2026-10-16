# -*- coding: utf-8 -*-
"""给下午题5大题模板加状态行 + 更新文件头说明"""
import re
from pathlib import Path

BASE = Path(r"D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\提不起精神-调研\衍生-学理解读\双轨策略-工作区\软考特攻")
MAP = BASE / "01-知识地图-L3.md"

# 题1-5 素材关键词
TOPIC_STATS = {
    "题1": ("数据流图", "DFD"),
    "题2": ("ER图", "关系模式", "E-R"),
    "题3": ("UML", "用例图", "类图"),
    "题4": ("分治", "贪心", "动态规划", "回溯"),
    "题5": ("设计模式", "单例", "工厂", "观察者"),
}

SUB_DIR = BASE / "字幕"
sub_texts = {}
for f in SUB_DIR.glob("*.md"):
    try:
        sub_texts[f.name] = f.read_text(encoding="utf-8", errors="ignore")
    except:
        pass

def count_kws(kws):
    total = 0; docs = 0
    for fname, text in sub_texts.items():
        c = sum(text.count(kw) for kw in kws)
        if c > 0:
            total += c; docs += 1
    return total, docs

lines = MAP.read_text(encoding="utf-8").splitlines()
new_lines = []
added = 0
i = 0
while i < len(lines):
    line = lines[i]
    m = re.match(r'^## 题([1-5]) ·', line)
    if m:
        num = m.group(1)
        kws = TOPIC_STATS[f"题{num}"]
        cnt, docs = count_kws(kws)
        new_lines.append(line)
        # 检查下一行是否已有状态行
        if not (i + 1 < len(lines) and '状态：' in lines[i+1]):
            new_lines.append(f"> 状态：⚪未掌握 ｜ 素材：{cnt}次/{docs}篇")
            added += 1
        i += 1
        continue
    new_lines.append(line)
    i += 1

# 更新文件头说明
text = "\n".join(new_lines)
text = text.replace(
    "> 颗粒度：每个考点到\"要背的那一句话\"，6字段齐全",
    "> 颗粒度：每个考点到\"要背的那一句话\"，8字段齐全\n> 状态字段：⚪未掌握(默认)/◐学习中/✅已掌握，自己改 ｜ 素材=该考点在445篇字幕中的出现次数/覆盖篇数"
)
MAP.write_text(text, encoding="utf-8")
print(f"下午题已加状态: {added} 题")
