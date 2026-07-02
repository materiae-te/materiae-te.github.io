# import os
# import pandas as pd

# # 设置文件夹路径和CSV文件路径
# folder_path = './'  # 替换为你的文件夹路径
# csv_path = 'ZT-300t.csv'    # 替换为你的CSV文件路径

# # 读取CSV文件
# df = pd.read_csv(csv_path)

# # 获取CSV中file列的数字
# csv_numbers = set(df['id'].astype(str))

# # 获取文件夹中所有mp-数字文件夹的数字
# folder_numbers = set()
# for item in os.listdir(folder_path):
#     if os.path.isdir(os.path.join(folder_path, item)) and item.startswith('mp-'):
#         folder_numbers.add(item.split('-')[1])

# # 找出文件夹中不存在的CSV数字
# missing_in_folders = csv_numbers - folder_numbers
# if missing_in_folders:
#     print("以下数字在文件夹中不存在:")
#     for number in missing_in_folders:
#         print(f"mp-{number}")

# # 找出CSV中不存在的文件夹数字
# missing_in_csv = folder_numbers - csv_numbers
# if missing_in_csv:
#     print("以下数字在CSV中不存在:")
#     for number in missing_in_csv:
#         print(f"mp-{number}")
import os
import pandas as pd

# 设置文件夹路径和CSV文件路径
folder_path = './'  # 替换为你的文件夹路径
csv_path = 'ZT-300t.csv'    # 替换为你的CSV文件路径

# 读取CSV文件
df = pd.read_csv(csv_path)

# 获取CSV中id列的数字
csv_numbers = set(df['id'].astype(str))

# 获取文件夹中所有mp-数字文件夹的数字
folder_numbers = set()
for item in os.listdir(folder_path):
    if os.path.isdir(os.path.join(folder_path, item)) and item.startswith('mp-'):
        folder_numbers.add(item.split('-')[1])

# 打印 CSV 和文件夹中的数字
print("CSV 中的数字：", csv_numbers)
print("文件夹中的数字：", folder_numbers)

# 找出差异
only_in_csv = csv_numbers - folder_numbers  # 在CSV中但不在文件夹中的数字
only_in_folder = folder_numbers - csv_numbers  # 在文件夹中但不在CSV中的数字

# 打印结果
print("\n仅在CSV中的数字（不在文件夹中）：")
print(only_in_csv)

print("\n仅在文件夹中的数字（不在CSV中）：")
print(only_in_folder)