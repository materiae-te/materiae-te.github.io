# import os
# import fitz  # PyMuPDF

# # 获取所有 mp- 开头的文件夹
# folders = [f for f in os.listdir('.') if os.path.isdir(f) and f.startswith('mp-')]

# success_count = 0
# fail_count = 0

# for folder in folders:
#     pdf_path = os.path.join(folder, 'band.pdf')
#     if os.path.exists(pdf_path):
#         try:
#             doc = fitz.open(pdf_path)
#             page = doc[0]
#             pix = page.get_pixmap(dpi=150)
#             output_path = os.path.join(folder, 'band.png')
#             pix.save(output_path)
#             doc.close()
#             print(f'✅ 已转换: {folder}/band.pdf -> band.png')
#             success_count += 1
#         except Exception as e:
#             print(f'❌ 转换失败: {folder}, 错误: {e}')
#             fail_count += 1
#     else:
#         print(f'⚠️ 未找到: {folder}/band.pdf')
#         fail_count += 1

# print(f'\n🎉 完成！成功: {success_count}, 失败: {fail_count}')

import os
import fitz  # PyMuPDF

# ====== 可调参数 ======
DPI = 85              # 建议 72~120，根据需要调整（值越小图片越小）
# =====================

folders = [f for f in os.listdir('.') if os.path.isdir(f) and f.startswith('mp-')]
success_count = fail_count = 0

for folder in folders:
    pdf_path = os.path.join(folder, 'band.pdf')
    if not os.path.exists(pdf_path):
        print(f'⚠️ 未找到: {folder}/band.pdf')
        fail_count += 1
        continue

    try:
        doc = fitz.open(pdf_path)
        page = doc[0]
        pix = page.get_pixmap(dpi=DPI)
        out_path = os.path.join(folder, 'band.png')
        pix.save(out_path)          # 默认已启用PNG压缩（通常相当于compress=6）
        doc.close()
        print(f'✅ 已转换: {folder}/band.pdf -> band.png (DPI={DPI})')
        success_count += 1
    except Exception as e:
        print(f'❌ 转换失败: {folder}, 错误: {e}')
        fail_count += 1

print(f'\n🎉 完成！成功: {success_count}, 失败: {fail_count}')