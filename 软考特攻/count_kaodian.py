# -*- coding: utf-8 -*-
"""v2: 用主干关键词统计考点在字幕库的出现次数与覆盖篇数"""
import re, json
from pathlib import Path

BASE = Path(r"D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\提不起精神-调研\衍生-学理解读\双轨策略-工作区\软考特攻")
MAP = BASE / "01-知识地图-L3.md"
SUB_DIR = BASE / "字幕"

# 考点名 → 搜索关键词（手工映射，覆盖特殊命名）
KEYWORD_MAP = {
    "需求分类": ["功能需求", "非功能需求"],
    "需求工程6步": ["需求获取", "需求分析", "需求验证"],
    "内聚7级（从低到高）": ["内聚"],
    "耦合7级（从低到高/从好到坏）": ["耦合"],
    "结构化分析SA工具": ["结构化分析", "数据流图"],
    "数据字典4类条目": ["数据字典"],
    "结构化设计SD": ["变换流", "事务流"],
    "V模型对应": ["验收测试", "系统测试", "集成测试", "单元测试"],
    "白盒覆盖强度（弱→强）": ["语句覆盖", "判定覆盖", "条件覆盖", "路径覆盖"],
    "黑盒方法": ["等价类", "边界值", "因果图", "错误推测"],
    "Alpha测试 vs Beta测试": ["Alpha测试", "Beta测试", "α测试", "β测试"],
    "调试 vs 测试": ["调试"],
    "McCabe环路复杂度": ["环路复杂度", "McCabe", "McCabe环路"],
    "4种维护": ["改正性", "适应性维护", "完善性", "预防性"],
    "关键路径法CPM/PERT": ["关键路径", "CPM", "PERT"],
    "CMMI 5级（从低到高）": ["CMMI"],
    "COCOMO模型": ["COCOMO"],
    "功能点FP": ["功能点"],
    "二叉树性质": ["二叉树"],
    "B树/B+树": ["B+树", "B树"],
    "哈夫曼编码": ["哈夫曼"],
    "排序算法比较": ["排序"],
    "查找算法": ["二分查找", "折半查找", "哈希查找"],
    "进程三态": ["进程状态", "就绪", "运行", "阻塞"],
    "进程五态": ["进程状态", "挂起"],
    "进程同步互斥": ["信号量", "PV操作", "PV"],
    "死锁条件": ["死锁"],
    "死锁避免": ["银行家算法"],
    "死锁检测": ["死锁检测", "资源分配图"],
    "三级调度": ["作业调度", "进程调度", "低级调度"],
    "时间片轮转RR": ["时间片轮转", "RR"],
    "页式存储": ["页式", "分页"],
    "段式存储": ["段式"],
    "段页式存储": ["段页式"],
    "局部性原理": ["局部性"],
    "页面置换算法": ["页面置换", "LRU", "FIFO", "OPT"],
    "文件索引结构": ["索引节点", "i节点", "文件分配"],
    "磁盘调度": ["磁盘调度", "先来先服务", "最短寻道", "SCAN"],
    "虚设备SPOOLing": ["SPOOLing", "Spooling"],
    "SQL基础": ["SQL"],
    "SQL注入攻击": ["SQL注入"],
    "三级模式结构": ["三级模式", "外模式", "概念模式", "内模式"],
    "关系代数": ["关系代数", "选择", "投影", "连接"],
    "关系模式规范化": ["范式", "NF", "函数依赖"],
    "事务ACID": ["ACID", "原子性", "一致性", "隔离性", "持久性"],
    "并发控制": ["并发控制", "锁", "封锁"],
    "ER图": ["ER图", "E-R"],
    "OSI七层": ["OSI"],
    "TCP/IP协议族": ["TCP/IP", "TCP", "IP协议"],
    "IP地址分类": ["IP地址", "A类", "B类", "C类"],
    "子网划分": ["子网"],
    "CIDR": ["CIDR", "无类"],
    "ARP协议": ["ARP"],
    "ICMP协议": ["ICMP"],
    "TCP三次握手": ["三次握手", "TCP"],
    "UDP": ["UDP"],
    "DNS": ["DNS"],
    "DHCP": ["DHCP"],
    "HTTP": ["HTTP"],
    "HTTPS": ["HTTPS", "SSL", "TLS"],
    "FTP": ["FTP"],
    "SMTP": ["SMTP", "邮件"],
    "POP3": ["POP3", "IMAP"],
    "加密算法": ["DES", "AES", "RSA", "加密"],
    "数字签名": ["数字签名"],
    "数字证书": ["数字证书", "CA证书"],
    "防火墙": ["防火墙"],
    "入侵检测IDS": ["入侵检测", "IDS"],
    "VPN": ["VPN"],
    "面向对象基本概念": ["对象", "类", "封装", "继承", "多态"],
    "UML类图": ["类图"],
    "UML用例图": ["用例图"],
    "UML序列图": ["序列图", "时序图"],
    "UML活动图": ["活动图"],
    "UML状态图": ["状态图"],
    "UML协作图": ["协作图", "通信图"],
    "用例间关系": ["包含", "扩展"],
    "类图关系": ["关联", "聚合", "组合", "依赖", "泛化"],
    "设计模式-创建型": ["工厂", "单例", "建造者", "原型"],
    "设计模式-结构型": ["适配器", "装饰", "代理", "外观", "组合"],
    "设计模式-行为型": ["观察者", "策略", "模板方法", "命令", "状态"],
    "著作权": ["著作权", "版权"],
    "专利权": ["专利"],
    "商标权": ["商标"],
    "商业秘密": ["商业秘密"],
    "标准化": ["标准化", "ISO", "GB"],
    "软件保护期限": ["保护期", "著作权法"],
    # ===== v2补全：0次考点映射 =====
    "二叉排序树BST": ["二叉排序树", "BST"],
    "平衡二叉树AVL": ["平衡二叉树", "AVL"],
    "最短路径Dijkstra": ["Dijkstra", "迪杰斯特拉"],
    "要背的话": ["快速排序", "快排", "堆排序", "归并排序"],
    "哈希冲突": ["哈希", "散列"],
    "ASL平均查找长度": ["平均查找长度", "ASL"],
    "编译过程6阶段": ["词法分析", "语法分析", "语义分析", "中间代码", "目标代码"],
    "Chomsky文法4型": ["Chomsky", "乔姆斯基"],
    "中间代码形式": ["后缀式", "四元式", "三元式", "中间代码"],
    "Cache映射": ["直接映射", "全相联", "组相联", "Cache映射"],
    "寻址方式速度排序": ["寻址方式", "立即寻址", "寄存器寻址", "间接寻址"],
    "流水线相关": ["流水线"],
    "进程vs线程": ["线程"],
    "FCFS先来先服务": ["先来先服务", "FCFS"],
    "SJF短作业优先": ["短作业优先", "SJF"],
    "死锁四必要条件": ["互斥", "循环等待", "不可剥夺", "死锁"],
    "死锁资源计算公式": ["死锁", "资源数"],
    "TLB快表": ["TLB", "快表"],
    "树形目录路径": ["目录"],
    "SPOOLing": ["SPOOLing", "Spooling"],
    "虚设备SPOOLing": ["SPOOLing", "Spooling"],
    "数据库设计4阶段": ["需求分析", "概念设计", "逻辑设计", "物理设计"],
    "三类完整性约束": ["实体完整性", "参照完整性", "用户定义完整性"],
    "ER图元素": ["ER图", "E-R图", "实体"],
    "ER转关系模式规则": ["关系模式", "ER图"],
    "SQL核心": ["SELECT", "GROUP BY", "HAVING", "JOIN"],
    "规范化范式逐级消除": ["范式", "1NF", "2NF", "3NF", "BCNF"],
    "TCP/IP四层": ["网络接口层", "网际层", "传输层", "应用层"],
    "各层代表协议": ["HTTP", "TCP", "UDP", "IP协议"],
    "数字证书+CA": ["数字证书", "CA"],
    "网络设备分层": ["路由器", "交换机", "网桥", "集线器"],
    "VLAN虚拟局域网": ["VLAN"],
    "Hash哈希函数": ["哈希函数", "散列函数"],
    "常见网络攻击": ["SQL注入", "XSS", "CSRF", "DoS", "攻击"],
    "多媒体图像容量计算": ["位图", "分辨率", "图像容量"],
    "面向对象三特性": ["封装", "继承", "多态"],
    "重载vs重写": ["重载", "重写", "覆盖"],
    "SRP单一职责": ["单一职责"],
    "OCP开闭原则": ["开闭原则"],
    "LSP里氏替换": ["里氏替换"],
    "DIP依赖倒置": ["依赖倒置"],
    "ISP接口隔离": ["接口隔离"],
    "抽象类vs接口": ["抽象类"],
    "UML 9图分类": ["用例图", "类图", "序列图", "活动图", "状态图"],
    "用例图关系": ["包含", "扩展", "泛化"],
}

def extract_keywords(name):
    """默认关键词提取：去括号、去数字级数、去vs"""
    if name in KEYWORD_MAP:
        return KEYWORD_MAP[name]
    # 去括号内容
    base = re.sub(r'[（(].*?[）)]', '', name)
    # 去数字+级数词
    base = re.sub(r'\d+[级类步大条层]', '', base)
    # 去 vs 后半
    base = base.split(' vs ')[0].split(' vs ')[0]
    # 去空格
    base = base.strip()
    if not base:
        return [name]
    return [base]

lines = MAP.read_text(encoding="utf-8").splitlines()
kaodian = []
for i, line in enumerate(lines):
    m = re.match(r'^- \*\*(.+?)\*\*：', line.strip())
    if m and not line.strip().startswith('- ['):
        name = m.group(1).strip()
        has_meta = False
        if i + 1 < len(lines) and lines[i+1].strip().startswith('- 考频'):
            has_meta = True
        kws = extract_keywords(name)
        kaodian.append({"line": i, "name": name, "has_meta": has_meta, "keywords": kws})

print(f"考点: {len(kaodian)}条")

sub_files = list(SUB_DIR.glob("*.md"))
sub_texts = {}
for f in sub_files:
    try:
        sub_texts[f.name] = f.read_text(encoding="utf-8", errors="ignore")
    except:
        pass
print(f"字幕: {len(sub_texts)}篇")

results = []
for kd in kaodian:
    total_count = 0
    doc_count = 0
    for fname, text in sub_texts.items():
        c = 0
        for kw in kd["keywords"]:
            c += text.count(kw)
        if c > 0:
            total_count += c
            doc_count += 1
    kd["count"] = total_count
    kd["docs"] = doc_count
    results.append(kd)

no_hit = [r for r in results if r["count"] == 0]
print(f"\n0次出现: {len(no_hit)}条")
for r in no_hit:
    print(f"  {r['name']} (kw={r['keywords']})")

(BASE / "素材清单" / "考点出现次数统计.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n统计已保存")
