# -*- coding: utf-8 -*-
"""Step 6 关联表 + JOIN：feedback 表（评分）× chats 表（对话）按单号对上"""
import sqlite3

conn = sqlite3.connect("chats.db")
cur = conn.cursor()

# ① 建 feedback 表：chat_id 指回 chats 表的 id（外键=表之间的快递单号）
cur.execute("""CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,                        -- 这条评分评的是哪条对话
    rating INTEGER                          -- 评分 1-5
)""")

# ② 塞 5 条评分（拿表里真实存在的前 5 条对话的 id，故意有低分）
ids = [r[0] for r in cur.execute("SELECT id FROM chats ORDER BY id LIMIT 5")]
ratings = [3, 1, 5, 2, 4]
for cid, r in zip(ids, ratings):
    cur.execute("INSERT INTO feedback (chat_id, rating) VALUES (?, ?)", (cid, r))
conn.commit()
print("已插入 5 条评分，对应的对话 id：", ids)

# ③ JOIN：按 chat_id = id 把两张表对上，查评分最低的 5 条对话
print("\n=== 评分最低的 5 条对话（JOIN 结果，升序）===")
for row in cur.execute("""
    SELECT f.rating, c.id, c.question
    FROM feedback f
    JOIN chats c ON f.chat_id = c.id
    ORDER BY f.rating ASC
    LIMIT 5
"""):
    print(row)

conn.close()
