import json
data = json.loads(open(r'D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\提不起精神-调研\衍生-学理解读\双轨策略-工作区\软考特攻\素材清单\视频样本清单.json',encoding='utf-8').read())
for topic in ['软件工程-内聚耦合','计组-IO中断DMA','计组-可靠性','操作系统-文件索引','软件工程-CMMI','操作系统-进程调度','数据库-三级模式','网络-加密防火墙','OOP-SOLID']:
    vids = data.get(topic,[])[:3]
    print(f'\n=== {topic} ===')
    for v in vids:
        t = v['title'][:45]
        print(f'  {t} | {v["author"]} | play={v["play"]}')
