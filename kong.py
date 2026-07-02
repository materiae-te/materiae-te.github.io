import os

# 查找所有以'mp-'开头的文件夹
mp_folders = [f for f in os.listdir() if f.startswith('mp-') and os.path.isdir(f)]

print("空'mp-'文件夹:")
for folder in mp_folders:
    if not os.listdir(folder):  # 如果文件夹为空
        print(folder)