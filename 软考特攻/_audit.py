import json, re
from pathlib import Path

BASE = Path(r'D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\提不起精神-调研\衍生-学理解读\双轨策略-工作区\软考特攻')

# 统计考点数
content = (BASE / '01-知识地图-L3.md').read_text(encoding='utf-8')
kaodian = len(re.findall(r'考频：[ABC]', content))
print(f'考点条数: {kaodian}')
print(f'文件大小: {(BASE / "01-知识地图-L3.md").stat().st_size} bytes')
print(f'总行数: {len(content.splitlines())}')

# 统计视频组
data = json.loads((BASE / '素材清单' / '视频样本清单.json').read_text(encoding='utf-8'))
total_vids = sum(len(v) for v in data.values())
print(f'\n视频知识点组: {len(data)}')
print(f'视频总数: {total_vids}')

# 列出每组top1标题，人工快速判断偏不偏
print('\n=== 各组top1核查 ===')
for topic, vids in data.items():
    if vids:
        t = vids[0]['title'][:40]
        print(f'  {topic}: {t}')
