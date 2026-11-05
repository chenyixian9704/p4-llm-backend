# -*- coding: utf-8 -*-
"""Step 5 索引实验：造 300 行 → EXPLAIN 前后对比（SCAN vs SEARCH）"""
import sqlite3

conn = sqlite3.connect("chats.db")
cur = conn.cursor()

# ① 造 300 行测试数据（数据少了，加不加索引都看不出来）
cur.execute("BEGIN")
for i in range(300):
    cur.execute("INSERT INTO chats (question, answer, created_at) VALUES (?, ?, ?)",
                (f"测试问题{i}", f"测试回答{i}", f"2026-11-{(i % 28) + 1:02d} 12:00:00"))
conn.commit()
print("已造 300 行测试数据，总行数变为", list(cur.execute("SELECT COUNT(*) FROM chats"))[0][0])

# ② 加索引前：让 SQLite 汇报它打算怎么查
print("\n=== 加索引前（EXPLAIN QUERY PLAN）===")
for row in cur.execute("EXPLAIN QUERY PLAN SELECT * FROM chats WHERE created_at = '2026-11-15 12:00:00'"):
    print(row)

# ③ 建索引：给 created_at 这一列配"书的目录"
cur.execute("CREATE INDEX IF NOT EXISTS idx_chats_created_at ON chats(created_at)")
conn.commit()
print("\n索引 idx_chats_created_at 已建")

# ④ 加索引后：同样的查询，再看计划
print("\n=== 加索引后（EXPLAIN QUERY PLAN）===")
for row in cur.execute("EXPLAIN QUERY PLAN SELECT * FROM chats WHERE created_at = '2026-11-15 12:00:00'"):
    print(row)

conn.close()
