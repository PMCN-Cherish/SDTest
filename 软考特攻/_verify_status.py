import re
from pathlib import Path
MAP = Path(r"D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\提不起精神-调研\衍生-学理解读\双轨策略-工作区\软考特攻\01-知识地图-L3.md")
text = MAP.read_text(encoding="utf-8")
lines = text.splitlines()

# 统计
status_lines = [l for l in lines if '状态：' in l]
ok_style = [l for l in status_lines if '｜ 状态：⚪未掌握 ｜ 素材：' in l or '> 状态：⚪未掌握 ｜ 素材：' in l]
total_kd = len(re.findall(r'^- \*\*.+?\*\*：', text, re.M))
print(f"文件大小: {len(text.encode('utf-8'))//1024}KB")
print(f"考点行: {total_kd}条")
print(f"状态字段行: {len(status_lines)}条")
print(f"格式正常: {len(ok_style)}条")
no_zero = [l for l in status_lines if '素材：0次' in l]
print(f"素材0次(覆盖缺口): {len(no_zero)}条")
for l in no_zero[:10]:
    m = re.search(r'\*\*(.+?)\*\*', l)
    print(f"  {m.group(1) if m else l[:40]}")
print("\n--- 头部说明 ---")
print("\n".join(lines[1:8]))
print("\n--- 下午题状态 ---")
for l in lines:
    if re.match(r'^## 题', l) or (l.startswith('> 状态：') and '素材：' in l):
        print(l)
