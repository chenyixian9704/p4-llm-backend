# -*- coding: utf-8 -*-
"""C1 Step 1：embedding 开眼——看文字怎么变成数字向量"""
import requests, re

# 从密钥索引读 73b5 按量 key（打码，不打印）
key = None
for line in open(r'C:\Users\xt\.secrets\api-keys.md', encoding='utf-8'):
    if '73b5' in line:
        m = re.search(r'[A-Za-z0-9.\-_]{28,}', line)
        if m: key = m.group(0)
print("key:", key[:8] + "****" if key else "❌ 没找到")

words = ["张力波动", "牵伸不稳定", "营业执照"]
for w in words:
    r = requests.post('https://open.bigmodel.cn/api/paas/v4/embeddings',
                      headers={'Authorization': 'Bearer ' + key},
                      json={'model': 'embedding-3', 'input': w}, timeout=30)
    print(f"\n[{w}] -> {r.status_code}")
    if r.status_code == 200:
        vec = r.json()['data'][0]['embedding']
        print(f"  向量维度: {len(vec)}")
        print(f"  前 6 个数: {[round(x, 4) for x in vec[:6]]}")
    else:
        print("  ", r.text[:150])
