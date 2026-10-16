# -*- coding: utf-8 -*-
"""
按知识点批量搜索B站视频，输出按知识点分组的清单JSON。
不转写，只收集bvid/标题/UP主/播放量/时长/URL。
"""
import json, time, re, urllib.parse, hashlib, sys
from pathlib import Path
import requests

COOKIE_DIR = Path(r"D:\11.project\iwen-codex\bilibili-cookies")
OUT_DIR = Path(r"D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\提不起精神-调研\衍生-学理解读\双轨策略-工作区\软考特攻\素材清单")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 加载cookie
def load_cookie():
    for f in sorted(COOKIE_DIR.glob("account*.txt")):
        if f.name.endswith(".bak.20261011"): continue
        c = f.read_text(encoding="utf-8-sig").strip()
        if c:
            return c
    raise RuntimeError("no cookie")

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,
         12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,
         57,62,11,36,20,34,44,52]

s = requests.Session()
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Cookie": load_cookie(),
    "Referer": "https://www.bilibili.com/",
})

# 验证登录
nav = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=15).json()
print("登录状态:", nav.get("data",{}).get("isLogin"), "|", nav.get("data",{}).get("uname"))
if not nav.get("data",{}).get("isLogin"):
    print("Cookie失效，退出")
    sys.exit(1)

wbi = nav["data"]["wbi_img"]
img = wbi["img_url"].rsplit("/",1)[-1].split(".")[0]
sub = wbi["sub_url"].rsplit("/",1)[-1].split(".")[0]
mixin = "".join((img+sub)[i] for i in MIXIN)[:32]

def sign(p):
    p = dict(p); p["wts"] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(p.items()))
    p["w_rid"] = hashlib.md5((q+mixin).encode()).hexdigest()
    return p

def search(kw, page=1):
    p = sign({"search_type":"video","keyword":kw,"page":page,"page_size":30})
    r = s.get("https://api.bilibili.com/x/web-interface/wbi/search/type", params=p, timeout=20).json()
    return (r.get("data") or {}).get("result") or []

# 知识点→搜索关键词（多组同义词）
TOPICS = {
    # 上午-软件工程
    "软件工程-开发模型": ["软考 软件设计师 开发模型 瀑布 螺旋", "软考 软件工程 V模型 敏捷"],
    "软件工程-内聚耦合": ["软考 内聚 耦合", "软件设计师 模块独立"],
    "软件工程-测试": ["软考 白盒测试 覆盖", "软件设计师 黑盒测试 等价类"],
    "软件工程-项目管理CPM": ["软考 关键路径 PERT", "软件设计师 甘特图 项目管理"],
    "软件工程-维护": ["软考 软件维护 改正性 完善性"],

    # 上午-数据结构
    "数据结构-二叉树遍历": ["软考 二叉树 遍历", "软件设计师 二叉树 中序前序"],
    "数据结构-排序算法": ["软考 排序算法 复杂度", "软件设计师 快排 堆排 归并"],
    "数据结构-图": ["软考 最小生成树 Dijkstra", "软件设计师 拓扑排序 关键路径"],
    "数据结构-算法策略": ["软考 分治 贪心 动态规划", "软件设计师 回溯法"],

    # 上午-计组
    "计组-码制浮点数": ["软考 原码反码补码", "软件设计师 浮点数 IEEE754"],
    "计组-校验码": ["软考 海明码 CRC", "软件设计师 奇偶校验"],
    "计组-Cache存储": ["软考 Cache 命中率 映射", "软件设计师 存储系统 层次"],
    "计组-IO中断DMA": ["软考 中断 DMA", "软件设计师 IO控制方式"],
    "计组-流水线": ["软考 流水线 吞吐率", "软件设计师 指令流水线"],
    "计组-可靠性": ["软考 可靠性 串联并联", "软件设计师 MTTF MTTR"],

    # 上午-操作系统
    "操作系统-PV操作": ["软考 PV操作 前驱图", "软件设计师 信号量 生产者消费者"],
    "操作系统-死锁": ["软考 死锁 银行家", "软件设计师 死锁必要条件"],
    "操作系统-页式存储": ["软考 页式存储 逻辑地址", "软件设计师 页面置换 LRU"],
    "操作系统-文件索引": ["软考 索引文件 位示图", "软件设计师 文件管理 磁盘"],

    # 上午-数据库
    "数据库-ER关系模式": ["软考 ER图 关系模式", "软件设计师 数据库下午题"],
    "数据库-SQL范式": ["软考 SQL 范式 1NF 3NF", "软件设计师 关系代数"],
    "数据库-事务": ["软考 事务 ACID 封锁"],

    # 上午-网络
    "网络-OSI协议栈": ["软考 OSI七层 TCP IP", "软件设计师 网络协议分层"],
    "网络-IP子网": ["软考 子网划分 CIDR", "软件设计师 IP地址 计算"],
    "网络-TCP": ["软考 TCP 三次握手", "软件设计师 TCP拥塞控制"],

    # 上午-OOP/UML
    "UML-用例图类图": ["软考 UML 用例图 include extend", "软件设计师 类图 聚合组合"],
    "UML-序列图": ["软考 UML 序列图 状态图"],

    # 设计模式（已抓过BV1xhLP6aEdU，补其他源）
    "设计模式-23个": ["软考 设计模式 口诀", "软件设计师 创建型 结构型 行为型"],
    "设计模式-单例工厂": ["软考 单例模式 工厂模式", "软件设计师 抽象工厂"],
    "设计模式-观察者策略": ["软考 观察者模式 策略模式", "软件设计师 装饰器 适配器"],

    # 知识产权
    "知识产权-保护期限": ["软考 知识产权 保护期限", "软件设计师 著作权 专利 商标"],

    # 下午题
    "下午题-DFD": ["软考 数据流图 DFD 下午题", "软件设计师 DFD 真题"],
    "下午题-ER数据库": ["软考 下午题 数据库 ER", "软件设计师 下午题 关系模式 SQL"],
    "下午题-UML": ["软考 下午题 UML 建模", "软件设计师 UML 案例题"],
    "下午题-算法C": ["软考 下午题 算法 C语言", "软件设计师 算法填空 动态规划"],
    "下午题-设计模式代码": ["软考 下午题 设计模式 Java", "软件设计师 设计模式 代码填空"],

    # 串讲/整体
    "整体-串讲": ["软考 软件设计师 串讲 冲刺", "软件设计师 考前急救 45分"],
    "整体-经验": ["软件设计师 备考经验 两周", "软考 不报班 上岸"],
}

all_results = {}
seen_bv = set()

for topic, kws in TOPICS.items():
    vids = []
    for kw in kws:
        try:
            res = search(kw)
            time.sleep(1.5)
            for v in res[:15]:
                bv = v.get("bvid")
                if not bv or bv in seen_bv: continue
                title = re.sub(r'<[^>]+>', '', v.get("title",""))
                dur = v.get("duration","")
                play = v.get("play",0)
                author = v.get("author","")
                vids.append({
                    "bvid": bv,
                    "title": title,
                    "author": author,
                    "play": play,
                    "duration": dur,
                    "url": f"https://www.bilibili.com/video/{bv}",
                    "keyword": kw,
                })
                seen_bv.add(bv)
        except Exception as e:
            print(f"  搜索失败 [{kw}]: {e}")
            time.sleep(3)
    # 按播放量排序取top10
    vids.sort(key=lambda x: -x["play"])
    all_results[topic] = vids[:10]
    print(f"[{topic}] {len(vids[:10])} 个视频")

# 保存
out_json = OUT_DIR / "视频样本清单.json"
out_json.write_text(json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")

# 生成MD
md_lines = ["# 软考视频样本清单（按知识点分组）\n", f"> 共 {len(all_results)} 个知识点组，{len(seen_bv)} 个去重视频\n"]
for topic, vids in all_results.items():
    md_lines.append(f"\n## {topic}\n")
    md_lines.append("| # | 标题 | UP主 | 播放 | 时长 | 链接 |")
    md_lines.append("|---|---|---|---|---|---|")
    for i, v in enumerate(vids, 1):
        md_lines.append(f"| {i} | {v['title'][:40]} | {v['author']} | {v['play']} | {v['duration']} | {v['url']} |")
(OUT_DIR / "视频样本清单.md").write_text("\n".join(md_lines), encoding="utf-8")

print(f"\n完成。总视频数: {len(seen_bv)}")
print(f"JSON: {out_json}")
print(f"MD: {OUT_DIR / '视频样本清单.md'}")
