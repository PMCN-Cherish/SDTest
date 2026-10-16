import re
content = open(r'D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\提不起精神-调研\衍生-学理解读\双轨策略-工作区\软考特攻\01-知识地图-L3.md', encoding='utf-8').read()
kaodian = len(re.findall(r'考频：[ABC]', content))
lines = len(content.splitlines())
size = len(content.encode('utf-8'))
print(f'考点条数: {kaodian}')
print(f'总行数: {lines}')
print(f'文件大小: {size} bytes ({size//1024}KB)')
