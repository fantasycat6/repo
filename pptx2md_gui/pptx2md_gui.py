import os
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess

def select_pptx_file():
    file_path = filedialog.askopenfilename(
        title="选择PPTX文件",
        filetypes=[("PPTX文件", "*.pptx")]
    )
    if file_path:
        pptx_path_var.set(file_path)

        # 设置默认输出文件路径为与选择的 .pptx 文件相同的目录
        md_output_path = os.path.splitext(file_path)[0] + ".md"
        output_filename_var.set(md_output_path)


def select_image_dir():
    dir_path = filedialog.askdirectory(
        title="选择图片存储路径"
    )
    if dir_path:
        image_dir_var.set(dir_path)


def convert_to_md():
    pptx_path = pptx_path_var.get()
    image_dir = image_dir_var.get().replace("\\", "/")  # 使用正斜杠统一路径
    output_file = output_filename_var.get()

    if not pptx_path:
        messagebox.showwarning("警告", "请选择PPTX文件")
        return
    if not image_dir:
        messagebox.showwarning("警告", "请选择图片存储路径")
        return
    if not output_file.endswith(".md"):
        output_file += ".md"

    # 生成命令
    command = [
        "pptx2md.exe",
        "-i", image_dir,
        "-o", output_file,
        pptx_path
    ]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        messagebox.showinfo("成功", "转换完成！")


    except subprocess.CalledProcessError as e:
        messagebox.showerror("错误", f"转换失败！\n{e.output}")
    except UnicodeDecodeError as e:
        messagebox.showerror("错误", f"编码错误：{e}")


# 初始化Tkinter窗口
root = tk.Tk()
root.title("PPTX转Markdown工具")
root.geometry("500x400")

# 字体设置
font = ("宋体", 18)

# PPTX文件选择
pptx_path_var = tk.StringVar()
tk.Label(root, text="选择PPTX文件:", font=font).pack(pady=5)
tk.Entry(root, textvariable=pptx_path_var, font=font, width=40).pack()
tk.Button(root, text="选择文件", command=select_pptx_file, font=font).pack(pady=5)

# 图片存储路径选择
image_dir_var = tk.StringVar(value="E:/learn/repo/assets")
tk.Label(root, text="图片存储路径:", font=font).pack(pady=5)
tk.Entry(root, textvariable=image_dir_var, font=font, width=40).pack()
tk.Button(root, text="选择路径", command=select_image_dir, font=font).pack(pady=5)

# 输出文件名设置（生成路径与pptx路径相同）
output_filename_var = tk.StringVar()
tk.Label(root, text="输出文件名:", font=font).pack(pady=5)
tk.Entry(root, textvariable=output_filename_var, font=font, width=40).pack()

# 转换按钮
tk.Button(root, text="开始转换", command=convert_to_md, font=font).pack(pady=20)

# 运行主循环
root.mainloop()
