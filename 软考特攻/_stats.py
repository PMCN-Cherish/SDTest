import os
from pathlib import Path
dir = Path(r"D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\提不起精神-调研\衍生-学理解读\双轨策略-工作区\软考特攻\字幕")
files = list(dir.glob("*.md"))
total = sum(f.stat().st_size for f in files)
print(f"字幕文件总数: {len(files)}")
print(f"总大小: {total/1024/1024:.1f}MB")
print("\n前10个大文件:")
for f in sorted(files, key=lambda x: -x.stat().st_size)[:10]:
    print(f"  {f.stat().st_size/1024/1024:.1f}MB - {f.name[:50]}")
