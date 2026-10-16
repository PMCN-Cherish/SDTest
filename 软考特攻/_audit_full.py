import json
data = json.loads(open(r'D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\提不起精神-调研\衍生-学理解读\双轨策略-工作区\软考特攻\素材清单\视频样本清单.json',encoding='utf-8').read())
# 打印每组全部3个视频，人工判断对应度
for topic, vids in data.items():
    print(f'\n### {topic}')
    for i, v in enumerate(vids[:3], 1):
        t = v['title'][:50]
        print(f'  {i}. {t} | {v["author"]} | {v["play"]}')
