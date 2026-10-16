# -*- coding: utf-8 -*-
"""把视频样本JSON转成Markdown附录，追加到L3知识地图末尾。"""
import json
from pathlib import Path

BASE = Path(r"D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\提不起精神-调研\衍生-学理解读\双轨策略-工作区\软考特攻")
data = json.loads((BASE / "素材清单" / "视频样本清单.json").read_text(encoding="utf-8"))
md_path = BASE / "01-知识地图-L3.md"

# 模块映射：知识地图章节标题 -> JSON里的知识点组
MODULE_MAP = [
    ("一、上午题 9 模块", "## ① 软件工程 ~15分", [
        "软件工程-开发模型", "软件工程-内聚耦合", "软件工程-测试",
        "软件工程-项目管理CPM", "软件工程-维护", "软件工程-CMMI", "软件工程-数据字典",
    ]),
    ("## ② 数据结构与算法 ~7分", None, [
        "数据结构-二叉树遍历", "数据结构-排序算法", "数据结构-图", "数据结构-算法策略",
        "编译原理-编译过程", "编译原理-自动机正规式",
    ]),
    ("## ③ 计算机组成与体系结构 ~6分", None, [
        "计组-码制浮点数", "计组-校验码", "计组-Cache存储",
        "计组-IO中断DMA", "计组-流水线", "计组-可靠性",
    ]),
    ("## ④ 操作系统 ~7分", None, [
        "操作系统-PV操作", "操作系统-死锁", "操作系统-页式存储", "操作系统-文件索引",
        "操作系统-进程调度",
    ]),
    ("## ⑤ 数据库系统 ~7分", None, [
        "数据库-ER关系模式", "数据库-SQL范式", "数据库-事务", "数据库-三级模式",
    ]),
    ("## ⑥ 计算机网络 ~5分", None, [
        "网络-OSI协议栈", "网络-IP子网", "网络-TCP", "网络-加密防火墙",
    ]),
    ("## ⑦ 面向对象技术（UML+设计模式）~7分", None, [
        "UML-用例图类图", "UML-序列图",
        "设计模式-23个", "设计模式-单例工厂", "设计模式-观察者策略", "OOP-SOLID",
    ]),
    ("## ⑧ 标准化与知识产权 ~3分", None, [
        "知识产权-保护期限",
    ]),
    ("二、下午题 5 大题模板", None, [
        "下午题-DFD", "下午题-ER数据库", "下午题-UML",
        "下午题-算法C", "下午题-设计模式代码",
    ]),
]

lines = ["\n\n---\n\n# 附录：视频资源索引（每知识点 top3）\n",
         "> 从640个去重视频中按播放量排序，每个知识点挑3个最相关的。\n",
         "> 用法：哪个考点不熟，直接点链接看视频，不用自己搜。\n"]

for header, _, topics in MODULE_MAP:
    lines.append(f"\n## {header.replace('## ','')}\n")
    for topic in topics:
        vids = data.get(topic, [])[:3]
        if not vids: continue
        lines.append(f"\n### {topic}\n")
        for i, v in enumerate(vids, 1):
            lines.append(f"{i}. [{v['title'][:50]}]({v['url']}) — {v['author']} | ▶{v['play']} | {v['duration']}")

# 整体串讲
lines.append("\n## 整体串讲/经验（全局）\n")
for topic in ["整体-串讲", "整体-经验"]:
    for i, v in enumerate(data.get(topic, [])[:3], 1):
        lines.append(f"- [{v['title'][:50]}]({v['url']}) — {v['author']} | ▶{v['play']} | {v['duration']}")

appendix = "\n".join(lines)

# 追加到文件末尾
old = md_path.read_text(encoding="utf-8")
if "附录：视频资源索引" in old:
    # 替换旧附录
    idx = old.find("\n\n---\n\n# 附录：视频资源索引")
    old = old[:idx]
md_path.write_text(old + appendix, encoding="utf-8")
print(f"已追加视频索引。文件大小: {md_path.stat().st_size} bytes")
print(f"附录行数: {len(lines)}")
