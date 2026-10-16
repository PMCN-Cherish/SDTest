import json
data = json.loads(open(r'D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\提不起精神-调研\衍生-学理解读\双轨策略-工作区\软考特攻\素材清单\视频样本清单.json',encoding='utf-8').read())
for topic in ['软件工程-内聚耦合','计组-可靠性','软件工程-CMMI','编译原理-编译过程','编译原理-自动机正规式','编译原理-后缀式','多媒体-图像容量']:
    vids = data.get(topic,[])[:3]
    print(f'\n=== {topic} ({len(data.get(topic,[]))}个) ===')
    for v in vids:
        t = v['title'][:45]
        print(f'  {t} | {v["author"]} | play={v["play"]}')
