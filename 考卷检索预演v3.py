# -*- coding: utf-8 -*-
"""A计划简历考卷 · 检索预演 v3（向量档取证）

背景：agent.py 的检索开关拨在向量 v3 档（search_resume_vector），
而老预演 考卷检索预演.py 只测字面 v2——预演与实战不是同一条检索线。
本脚本给 v3 拍 X 光片：每题打印 top-2 块标题 + 余弦相似度。

判卷三步不变：定标（这题需要哪几块）→ 对照（来了没）→ 定因（谁把谁挤下去了）
用法：D:/conda/python.exe 考卷检索预演v3.py
"""
import json
from search_test import search_resume_vector, VEC_FILE

# K卷知识题原题——取证必须用实战考卷原文：措辞差一个词，向量排名就可能变
QUESTIONS = [
    ("K1", "简历主人叫什么名字？毕业于哪所学校、什么专业？"),
    ("K2", "他掌握哪些与 AI 相关的技能？"),
    ("K3", "他在云服务器上部署过什么平台？独立解决过哪类故障？"),
    ("K4", "他的 RAG 项目叫什么名字？评测结果如何？"),
    ("K5", "他手搓的 Agent 有哪些核心组件？"),
    ("K6", "他给 Agent 设计的评测考卷覆盖哪几类题？分数是怎么变化的？"),
    ("K7", "他实习过的公司是哪家？担任什么岗位？"),
]

print("=" * 62)
print("书架全图（向量库全部块，定标用）")
print("=" * 62)
kb = json.load(open(VEC_FILE, encoding="utf-8"))
for it in kb:
    print(f"  [{it['id']}] {it['title']}")

for k, q in QUESTIONS:
    print(f"\n{'—' * 50}")
    print(f"=== {k}：{q}")
    for sim, text in search_resume_vector(q):
        title = text.splitlines()[0]          # 块标题 = text 第一行
        print(f"  [{sim:.3f}] 《{title}》")
