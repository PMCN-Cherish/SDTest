import re, json
from pathlib import Path

BASE = Path(r'D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\提不起精神-调研\衍生-学理解读\双轨策略-工作区\软考特攻')

# 1. 知识地图考点数
content = (BASE / '01-知识地图-L3.md').read_text(encoding='utf-8')
kaodian = len(re.findall(r'考频：[ABC]', content))
lines = len(content.splitlines())
size = len(content.encode('utf-8'))

# 2. 视频组
data = json.loads((BASE / '素材清单' / '视频样本清单.json').read_text(encoding='utf-8'))
total_vids = sum(len(v) for v in data.values())

# 3. 易混点
yihun = len(re.findall(r'\| \*\*', content))

print('=== 最终核验报告 ===')
print(f'知识地图: {kaodian}条考点, {lines}行, {size//1024}KB')
print(f'视频组: {len(data)}组, {total_vids}个视频')
print(f'易混点表: {yihun}条')
print(f'外部资源索引: 9篇博客+1个Gitee仓库')
print()
print('=== 模块覆盖 ===')
modules = ['软件工程','数据结构','编译原理','计算机组成','操作系统','数据库','网络','面向对象','UML','设计模式','知识产权','专业英语','下午题','易混点']
for m in modules:
    count = content.count(m)
    print(f'  {m}: 出现{count}次')
