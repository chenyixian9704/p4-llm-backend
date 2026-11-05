# -*- coding: utf-8 -*-
"""Step 2：四件套实战——INSERT / SELECT / UPDATE / DELETE"""
import sqlite3

conn = sqlite3.connect("chats.db")
cur = conn.cursor()

# ① INSERT 三条真实对话（就用今天测试 Agent 的真实问答）
# ? 占位符 = 参数化查询：用户输入只当数据、不当代码（防SQL注入，面试考点）
cur.execute("INSERT INTO chats (question, answer) VALUES (?, ?)",
            ("什么是 FDE", "FDE 是前沿部署工程师，深入客户业务现场落地大模型能力"))
cur.execute("INSERT INTO chats (question, answer) VALUES (?, ?)",
            ("他会 Docker 吗", "会，部署过 20 容器 Dify 平台"))
cur.execute("INSERT INTO chats (question, answer) VALUES (?, ?)",
            ("什么是幻觉", "编造事实——假在内容，区别于表演式服从的假在过程"))
conn.commit()                                # 三条攒一起，一次落盘

# ② SELECT 全部读出来
print("--- 插入后 ---")
for row in cur.execute("SELECT id, question, answer FROM chats"):
    print(row)

# ③ UPDATE 改一条（注意 WHERE！）
cur.execute("UPDATE chats SET answer = ? WHERE id = 1",
            ("FDE = Forward Deployed Engineer 前沿部署工程师",))
conn.commit()

# ④ DELETE 删一条
cur.execute("DELETE FROM chats WHERE id = 3")
conn.commit()

# ⑤ 再 SELECT 看最终变化
print("--- 改删后 ---")
for row in cur.execute("SELECT id, question, answer FROM chats"):
    print(row)

conn.close()