# -*- coding: utf-8 -*-
"""C1 Step 3：向量检索——余弦相似度取最相关的 2 块"""
import requests, json, re

key = None
for line in open(r'C:\Users\xt\.secrets\api-keys.md', encoding='utf-8'):
    if '73b5' in line:
        m = re.search(r'[A-Za-z0-9.\-_]{28,}', line)
        if m: key = m.group(0)

def embed(text):
    r = requests.post('https://open.bigmodel.cn/api/paas/v4/embeddings',
                      headers={'Authorization': 'Bearer ' + key},
                      json={'model': 'embedding-3', 'input': text}, timeout=30)
    return r.json()['data'][0]['embedding']

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))       # 点积：对应位置相乘再求和
    na = sum(x * x for x in a) ** 0.5            # a 的长度
    nb = sum(x * x for x in b) ** 0.5            # b 的长度
    return dot / (na * nb)

def search_resume_v3(question):
    kb = json.load(open("resume_vectors.json", encoding="utf-8"))
    qv = embed(question)
    scored = []
    for item in kb:
        sim = cosine(qv, item["vector"])
        scored.append((sim, item))
    scored.sort(reverse=True)
    return scored[:2]

for q in ["他在哪个学校读书", "他会用容器技术吗", "他的求职意向是什么"]:
    print("问：", q)
    for sim, item in search_resume_v3(q):
        print(f"  [{sim:.3f}] {item['title']}")
    print()
