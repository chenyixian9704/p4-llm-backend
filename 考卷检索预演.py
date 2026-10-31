# -*- coding: utf-8 -*-
"""A计划简历考卷 · 检索预演 v2：先看书架全图，再看每题递来的书（全文）。
判卷三步：定标（这题需要哪几块）→ 对照（来了没）→ 定因（字面失配 or 噪音竞争）"""

import io
import contextlib

with contextlib.redirect_stdout(io.StringIO()):  # 屏蔽 import 时的自带三连
    from search_test import search_resume

text = open("resume_kb.txt", encoding="utf-8").read()
chunks = text.split("## ")[1:]

print("=" * 62)
print("第一步：书架全图——语料里一共有这些块（这是你定标的依据）")
print("=" * 62)
for c in chunks:
    body = "\n".join(c.splitlines()[1:]).strip()
    print(f"\n【{c.splitlines()[0]}】")
    print(body if body else "（无正文）")

QUESTIONS = [
    ("Q2", "他有哪些与 AI 产品/实施/测试岗位匹配的能力？"),
    ("Q3", "他是什么专业背景？这对转行是优势还是劣势？"),
    ("Q4", "描述一个他亲手做过的项目"),
    ("Q5", "他系统学过哪些技术和工具？"),
    ("Q6", "他目前的学习进度到了哪一步？"),
    ("T1", "他会写 Python 吗？水平怎么样？"),
    ("T3", "他做过多少人的团队管理？"),
]

print("\n" + "=" * 62)
print("第二步：逐题看图书管理员递来什么（全文，附得分）")
print("=" * 62)
for k, q in QUESTIONS:
    print(f"\n{'—' * 50}")
    print(f"=== {k}：{q}")
    for score, c in search_resume(q):
        print(f"\n  ▼ [{score}% 命中] 《{c.splitlines()[0]}》")
        print("  " + "\n  ".join(c.splitlines()[1:]).strip())

print("\n—— 预演结束。逐题走三步：定标 → 对照 → 定因，给我判决表。")
