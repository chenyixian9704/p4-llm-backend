# -*- coding: utf-8 -*-
"""C1 Step 2：语料向量化——11 节语料逐块调 embedding，存成 resume_vectors.json"""
import requests, re, json

key = None
for line in open(r'C:\Users\xt\.secrets\api-keys.md', encoding='utf-8'):
    if '73b5' in line:
        m = re.search(r'[A-Za-z0-9.\-_]{28,}', line)
        if m: key = m.group(0)

text = open("resume_kb.txt", encoding="utf-8").read()
chunks = text.split("## ")[1:]              # 切块（chunk_test 的三连复用）

out = []
for i, c in enumerate(chunks):
    title = c.split("\n")[0].strip()
    r = requests.post('https://open.bigmodel.cn/api/paas/v4/embeddings',
                      headers={'Authorization': 'Bearer ' + key},
                      json={'model': 'embedding-3', 'input': c}, timeout=30)
    if r.status_code != 200:
        print(f"[{i}] {title} 失败:", r.text[:100]); break
    vec = r.json()['data'][0]['embedding']
    out.append({"id": i, "title": title, "text": c, "vector": vec})
    print(f"[{i}] {title} -> {len(vec)} 维 ✓")

json.dump(out, open("resume_vectors.json", "w", encoding="utf-8"), ensure_ascii=False)
print(f"\n向量库已保存: resume_vectors.json（{len(out)} 块 × 2048 维）")
