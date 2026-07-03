import os

# 获取当前目录
current_directory = os.getcwd()

# 初始化计数器
mp_folder_count = 0

# 遍历当前目录下的所有文件和文件夹
for item in os.listdir(current_directory):
    # 检查是否是文件夹并且以 'mp-' 开头
    if item.startswith('mp-') and os.path.isdir(os.path.join(current_directory, item)):
        mp_folder_count += 1

# 输出结果
print(f"当前目录下以 'mp-' 开头的文件夹数量: {mp_folder_count}")