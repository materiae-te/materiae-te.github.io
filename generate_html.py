import os

# 获取所有包含 band.png 的 mp- 文件夹
folders = []
for f in os.listdir('.'):
    if os.path.isdir(f) and f.startswith('mp-'):
        if os.path.exists(os.path.join(f, 'band.png')):
            folders.append(f)

# 生成图片卡片
cards = []
for folder in folders:
    card = f'''        <div class="card">
            <img src="{folder}/band.png" alt="{folder}">
            <p>{folder}</p>
        </div>'''
    cards.append(card)

# 生成完整的 HTML
html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>能带图展示</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 20px auto;
            padding: 0 20px;
            background-color: #f4f4f4;
        }}
        h1 {{
            color: #333;
            text-align: center;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        .card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .card img {{
            max-width: 100%;
            height: auto;
            border-radius: 5px;
        }}
        .card p {{
            color: #555;
            margin: 10px 0 0;
            font-size: 14px;
            word-break: break-all;
        }}
    </style>
</head>
<body>
    <h1>📊 能带图展示</h1>
    <p style="text-align:center; color:#666;">共 {len(cards)} 张图片</p>

    <div class="gallery">
{chr(10).join(cards)}
    </div>

</body>
</html>'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f'✅ 已生成 index.html，共 {len(cards)} 张图片')