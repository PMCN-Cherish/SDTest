import json
from pathlib import Path
BASE = Path(r"D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\提不起精神-调研\衍生-学理解读\双轨策略-工作区\软考特攻")
results = json.loads((BASE / "素材清单" / "ASR转写结果.json").read_text(encoding="utf-8"))
ok = sum(1 for r in results if r["status"]=="ok")
already = sum(1 for r in results if r["status"]=="already")
err = sum(1 for r in results if r["status"]=="error")
print(f"总数: {len(results)}")
print(f"成功: {ok}")
print(f"已存在: {already}")
print(f"失败: {err}")
print("\n失败的:")
for r in results:
    if r["status"]=="error":
        print(f"  {r['bvid']} {r['topic'][:20]} - {r.get('err','')[:50]}")
