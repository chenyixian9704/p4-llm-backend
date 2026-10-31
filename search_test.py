# -*- coding: utf-8 -*-
"""检索实验 v2：按"命中单元"打分（长度归一），返回最相关的 4 块——自建 RAG 的心脏

v2 迭代记录（2026-10-31，检索预演考卷驱动，共 5 处）：
  ① 语料去重并版：resume_kb.txt 里工作经历/交付文档原有两份拷贝；工作经历取两版合并
     （补回「在……公司担任」措辞，否则"哪个公司实习"检索不到工作经历）
  ② 长度归一：命中率 = 命中单元数 ÷ 块长度 × 100，治"长块处处沾光"
     （术语表 190+ 字全场最长，曾在 Q2/Q3/Q6 三题靠字多抢位）
  ③ 剔除非文字单元：空格/标点不参与计分（"他会 Docker 吗"的两个空格曾给全场白送 2 分）
  ④ 英文按词匹配：Python 整词算一个命中单元，不再逐字母
     （治"github.com 里的 y/t/o/h 冒充命中 Python"——HANDOFF 已知弱点的正式修法）
  ⑤ 同义词改写换时序：先剥停用词、再改写"技术→技能"。
     顺序反了的话，改写进来的"能"会被停用词剥掉，改写等于白做
"""
import re

STOPWORDS = "的了是在有和与就也都啊吧吗呢把对从被让向往哪些什么怎么多少这那他她它我你您会能可以很过要请帮"
SYNONYMS = {"技术": "技能"}          # 查询改写：题目用词 → 语料用词


def search_resume(question):
    text = open("resume_kb.txt", encoding="utf-8").read()   # ① 读语料
    chunks = text.split("## ")[1:]                          # ② 切块

    # ⓪ 拆检索单元：英文单词=1 个单元、汉字=1 个单元；空格/标点直接丢弃
    words = re.findall(r"[A-Za-z]+", question)
    hanzi = [h for h in re.findall(r"[\u4e00-\u9fff]", question) if h not in STOPWORDS]
    clean = "".join(hanzi)
    for old, new in SYNONYMS.items():                       # ③ 同义词改写（在停用词之后！）
        clean = clean.replace(old, new)
    units = words + list(clean)                             # 英文按词、中文按字

    hits = []                                               # ④ 记分板：(命中率, 块)
    for c in chunks:
        c_low = c.lower()
        score = sum(1 for u in units if (u.lower() in c_low if len(u) > 1 else u in c))
        rate = round(100 * score / len(c), 1)               # 长度归一：长块不再占便宜
        hits.append((rate, c))

    hits.sort(key=lambda x: x[0], reverse=True)             # ⑤ 按命中率从高到低
    return hits[:4]                                         # ⑥ 前 4 名（综合题需要多块材料，2 块不够）


if __name__ == "__main__":          # 只有直接运行本文件才跑验收三连；被 import 时保持安静
    for q in ["他会 Docker 吗", "他在哪个公司实习过", "他的评测考卷有几道题"]:
        print("问：", q)
        for rate, c in search_resume(q):
            print(f"  [{rate}% 命中] {c.splitlines()[0]}")   # 元组解包 + 只打印标题行
        print()
