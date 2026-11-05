# -*- coding: utf-8 -*-
"""Step 3 弹药：插入 10 行测试数据（日期跨多天，供排序/分组练习）"""
import sqlite3

rows = [
    ("怎么学 RAG", "从检索三步开始", "2026-11-01 09:00:00"),
    ("token 怎么算钱", "按输入+输出 token 数", "2026-11-01 10:30:00"),
    ("Docker 报错怎么办", "先看 logs", "2026-11-01 21:15:00"),
    ("什么是 MCP", "模型上下文协议", "2026-11-02 09:20:00"),
    ("eval 怎么设计", "先定黄金考卷", "2026-11-02 14:00:00"),
    ("MySQL 和 SQLite 区别", "单文件 vs 服务端", "2026-11-03 10:00:00"),
    ("他会 Docker 吗", "会，部署过 20 容器", "2026-11-03 11:20:00"),
    ("什么是幻觉", "编造事实", "2026-11-04 09:10:00"),
    ("FDE 是什么岗位", "前沿部署工程师", "2026-11-04 15:30:00"),
    ("怎么转行 AI", "做中学+作品集", "2026-11-04 20:45:00"),
]
conn = sqlite3.connect("chats.db")
cur = conn.cursor()
for q, a, t in rows:
    cur.execute("INSERT INTO chats (question, answer, created_at) VALUES (?, ?, ?)", (q, a, t))
conn.commit()
print("已插入", len(rows), "行测试数据")
for row in conn.execute("SELECT COUNT(*) FROM chats"):
    print("表内总行数:", row[0])
conn.close()
