# -*- coding: utf-8 -*-
"""检索实验：按字符重合度打分，返回最相关的 2 块——自建 RAG 的心脏"""
STOPWORDS = "的了是在有和与就也都啊吧吗呢把对从被让向往哪些什么怎么多少这那他她它我你您会能可以很过要请帮"
def search_resume(question):
    text = open("resume_kb.txt", encoding="utf-8").read()   # ① 读语料
    chunks = text.split("## ")[1:]                          # ② 切块（chunk_test 三连）

    scores = []                                             # ③ 记分板
    for c in chunks:
        score = 0
        clean = "".join(ch for ch in question if ch not in STOPWORDS)   # ← 新增：剥掉停用字
        for ch in clean:                                                 # ← question 改成 clean
            if ch in c:
                score += 1                         #    得一分
        scores.append((score, c))                           #    打包上记分板

    scores.sort(reverse=True)                               # ④ 按得分从高到低
    return scores[:2]                                       # ⑤ 前 2 名

# —— 验收三连 ——
for q in ["他会 Docker 吗", "他在哪个公司实习过", "他的评测考卷有几道题"]:
    print("问：", q)
    for score, c in search_resume(q):
        print(f"  [{score}分] {c.splitlines()[0]}")         # 元组解包 + 只打印标题行
    print()
