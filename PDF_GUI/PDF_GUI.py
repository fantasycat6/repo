import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, font


class PDFExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF文件提取器")
        self.root.geometry("800x500")
        self.root.resizable(False, False)

        # 设置字体
        self.custom_font = font.Font(family="宋体", size=18)

        # 创建文件夹选择框和显示路径的文本框
        self.folder_path = tk.StringVar()
        self.output_folder_path = None

        tk.Label(root, text="选择包含PDF文件的文件夹：", font=self.custom_font).pack(pady=10)

        path_frame = tk.Frame(root)
        path_frame.pack(pady=10)

        tk.Entry(path_frame, textvariable=self.folder_path, width=40, font=self.custom_font, state="readonly").pack(
            side="left", padx=5)
        tk.Button(path_frame, text="选择文件夹", font=self.custom_font, command=self.select_folder).pack(side="left")

        # 提取PDF文件按钮
        self.extract_button = tk.Button(root, text="提取PDF文件", font=self.custom_font, state="disabled",
                                        command=self.extract_pdfs)
        self.extract_button.pack(pady=10)

        # 打开生成文件夹按钮
        self.open_button = tk.Button(root, text="打开生成的文件夹", font=self.custom_font, state="disabled",
                                     command=self.open_output_folder)
        self.open_button.pack(pady=10)

        # 日志信息文本框
        self.log_text = tk.Text(root, font=self.custom_font, height=8, width=50)
        self.log_text.pack(pady=10)

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.output_folder_path = os.path.join(folder_selected + "_PDF")
            self.extract_button.config(state="normal")
            self.log("已选择文件夹: " + folder_selected)

    def extract_pdfs(self):
        input_folder = self.folder_path.get()
        if not input_folder:
            messagebox.showwarning("警告", "请先选择文件夹！")
            return

        if not os.path.exists(self.output_folder_path):
            os.makedirs(self.output_folder_path)

        for root_dir, dirs, files in os.walk(input_folder):
            rel_path = os.path.relpath(root_dir, input_folder)
            target_dir = os.path.join(self.output_folder_path, rel_path)
            os.makedirs(target_dir, exist_ok=True)

            for file_name in files:
                if file_name.lower().endswith('.pdf'):
                    src_file = os.path.join(root_dir, file_name)
                    dst_file = os.path.join(target_dir, file_name)
                    shutil.move(src_file, dst_file)
                    self.log(f"提取PDF: {src_file} -> {dst_file}")

        self.open_button.config(state="normal")
        messagebox.showinfo("完成", "PDF文件提取完成！")

    def open_output_folder(self):
        if self.output_folder_path and os.path.exists(self.output_folder_path):
            os.startfile(self.output_folder_path)
        else:
            messagebox.showerror("错误", "输出文件夹不存在！")

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)


# 创建主窗口
root = tk.Tk()
app = PDFExtractorApp(root)
root.mainloop()
