import os
import fitz

DPI = 75

folders = [f for f in os.listdir('.') if os.path.isdir(f) and f.startswith('mp-')]

for folder in folders:
    pdf_files = [f for f in os.listdir(folder) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f'⚠️ 未找到 PDF 文件: {folder}')
        continue

    for pdf_name in pdf_files:
        pdf_path = os.path.join(folder, pdf_name)
        try:
            doc = fitz.open(pdf_path)
            page = doc[0]
            pix = page.get_pixmap(dpi=DPI)
            # 输出文件名：去掉 .pdf 后缀，加上 .png
            out_name = os.path.splitext(pdf_name)[0] + '.png'
            out_path = os.path.join(folder, out_name)
            pix.save(out_path)
            doc.close()
            print(f'✅ 已转换: {folder}/{pdf_name} -> {out_name}')
        except Exception as e:
            print(f'❌ 转换失败: {folder}/{pdf_name}, 错误: {e}')