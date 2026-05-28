import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

def copy_images_to_assets(source_dir, text_widget):
    current_dir = os.getcwd()
    assets_dir = os.path.join(current_dir, 'assets')
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)

    copied_files_count = 0
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                source_file = os.path.join(root, file)
                target_file = os.path.join(assets_dir, file)
                shutil.copy2(source_file, target_file)
                # text_widget.insert(tk.END, f'已复制: {source_file} 到 {target_file}\n')
                copied_files_count += 1

    if copied_files_count > 0:
        text_widget.insert(tk.END, f'\n复制完成！共复制了 {copied_files_count} 张图片。\n')
    else:
        text_widget.insert(tk.END, '没有找到任何图片文件。\n')

def select_directory():
    global selected_directory
    selected_directory = filedialog.askdirectory()
    if selected_directory:
        path_entry.delete(0, tk.END)  # 清空文本框
        path_entry.insert(0, selected_directory)  # 显示选择的文件夹路径
        text_widget.delete(1.0, tk.END)  # 清空结果文本框
        text_widget.insert(tk.END, f'选择的文件夹是: {selected_directory}\n')
    else:
        messagebox.showwarning("未选择文件夹", "请先选择一个文件夹！")

def start_copying():
    if selected_directory:
        text_widget.delete(1.0, tk.END)  # 清空结果文本框
        text_widget.insert(tk.END, f'开始复制来自: {selected_directory}\n\n')
        copy_images_to_assets(selected_directory, text_widget)
    else:
        messagebox.showwarning("未选择文件夹", "请先选择一个文件夹！")

# 初始化全局变量
selected_directory = ""

# 创建主窗口
root = tk.Tk()
root.title("图片复制程序")

# 设置字体
font_settings = ("宋体", 18)

# 创建上方框架
top_frame = tk.Frame(root)
top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

# 创建路径文本框
path_entry = tk.Entry(top_frame, width=50, font=font_settings)
path_entry.pack(side=tk.LEFT, padx=10)

# 创建选择文件夹按钮
select_button = tk.Button(top_frame, text="选择文件夹", command=select_directory, height=1, font=font_settings)
select_button.pack(side=tk.LEFT, padx=5)

# 创建开始按钮
start_button = tk.Button(top_frame, text="开始", command=start_copying, height=1, font=font_settings)
start_button.pack(side=tk.LEFT, padx=5)

# 创建滚动文本框以显示结果
text_widget = scrolledtext.ScrolledText(root, width=80, height=20, font=font_settings)
text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# 运行主循环
root.mainloop()
