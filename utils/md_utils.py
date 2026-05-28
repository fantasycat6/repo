import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class MarkdownExtractor:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("📝 Markdown提取工具")
        self.window.geometry("700x500")
        self.window.configure(bg="#f8f9fa")
        self.window.minsize(650, 450)
        
        self.source_dir = tk.StringVar()
        self.target_dir = tk.StringVar()
        self.setup_ui()
        
    def setup_ui(self):
        # 标题栏
        header = tk.Frame(self.window, bg="#10b981", height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        
        tk.Label(header, text="📝 Markdown提取工具", font=("Microsoft YaHei UI", 16, "bold"), 
                bg="#10b981", fg="#ffffff").pack(pady=15)
        
        # 内容区域
        content = tk.Frame(self.window, bg="#f8f9fa", padx=30, pady=30)
        content.pack(fill=tk.BOTH, expand=True)
        
        # 源文件夹选择
        src_frame = tk.Frame(content, bg="#f8f9fa")
        src_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(src_frame, text="源文件夹:", font=("Microsoft YaHei UI", 11), 
                bg="#f8f9fa", fg="#1e293b").pack(anchor=tk.W, pady=(0, 8))
        
        src_path_frame = tk.Frame(src_frame, bg="#f8f9fa")
        src_path_frame.pack(fill=tk.X)
        
        src_entry = tk.Entry(src_path_frame, textvariable=self.source_dir, 
                            font=("Microsoft YaHei UI", 10), bg="#ffffff", 
                            fg="#1e293b", relief=tk.SOLID, bd=1)
        src_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        src_browse_btn = tk.Button(src_path_frame, text="浏览...", bg="#10b981", fg="#ffffff",
                                  font=("Microsoft YaHei UI", 10), padx=15, pady=6, 
                                  relief=tk.FLAT, cursor="hand2", 
                                  command=lambda: self.browse_dir(self.source_dir))
        src_browse_btn.pack(side=tk.RIGHT)
        
        # 目标文件夹选择
        target_frame = tk.Frame(content, bg="#f8f9fa")
        target_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(target_frame, text="目标文件夹:", font=("Microsoft YaHei UI", 11), 
                bg="#f8f9fa", fg="#1e293b").pack(anchor=tk.W, pady=(0, 8))
        
        target_path_frame = tk.Frame(target_frame, bg="#f8f9fa")
        target_path_frame.pack(fill=tk.X)
        
        target_entry = tk.Entry(target_path_frame, textvariable=self.target_dir, 
                              font=("Microsoft YaHei UI", 10), bg="#ffffff", 
                              fg="#1e293b", relief=tk.SOLID, bd=1)
        target_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        target_browse_btn = tk.Button(target_path_frame, text="浏览...", bg="#10b981", fg="#ffffff",
                                     font=("Microsoft YaHei UI", 10), padx=15, pady=6, 
                                     relief=tk.FLAT, cursor="hand2", 
                                     command=lambda: self.browse_dir(self.target_dir))
        target_browse_btn.pack(side=tk.RIGHT)
        
        # 进度条
        progress_frame = tk.Frame(content, bg="#f8f9fa")
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100, length=300)
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        self.status_label = tk.Label(progress_frame, text="准备就绪", font=("Microsoft YaHei UI", 9), 
                                   bg="#f8f9fa", fg="#64748b")
        self.status_label.pack(anchor=tk.W)
        
        # 操作按钮
        btn_frame = tk.Frame(content, bg="#f8f9fa")
        btn_frame.pack(fill=tk.X)
        
        start_btn = tk.Button(btn_frame, text="🚀 开始提取", bg="#10b981", fg="#ffffff",
                             font=("Microsoft YaHei UI", 11, "bold"), padx=25, pady=10, 
                             relief=tk.FLAT, cursor="hand2", command=self.start_extract)
        start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = tk.Button(btn_frame, text="清空", bg="#64748b", fg="#ffffff",
                             font=("Microsoft YaHei UI", 10), padx=20, pady=8, 
                             relief=tk.FLAT, cursor="hand2", command=self.clear_fields)
        clear_btn.pack(side=tk.LEFT)
        
    def browse_dir(self, var):
        dir_path = filedialog.askdirectory(title="选择文件夹")
        if dir_path:
            var.set(dir_path)
            
    def start_extract(self):
        source_dir = self.source_dir.get()
        target_dir = self.target_dir.get()
        
        if not source_dir:
            messagebox.showwarning("警告", "请选择源文件夹！")
            return
        if not target_dir:
            messagebox.showwarning("警告", "请选择目标文件夹！")
            return
            
        if not os.path.isdir(source_dir):
            messagebox.showerror("错误", "源文件夹不存在！")
            return
            
        # 查找所有Markdown文件
        md_files = []
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.md'):
                    md_files.append((root, file))
                    
        if not md_files:
            messagebox.showinfo("提示", "未找到任何Markdown文件！")
            return
            
        total = len(md_files)
        self.progress_var.set(0)
        self.status_label.config(text=f"正在提取... 0/{total}")
        
        count = 0
        for i, (root, file) in enumerate(md_files):
            rel_path = os.path.relpath(root, source_dir)
            target_subdir = os.path.join(target_dir, rel_path)
            
            if not os.path.exists(target_subdir):
                os.makedirs(target_subdir)
                
            src_file = os.path.join(root, file)
            dst_file = os.path.join(target_subdir, file)
            
            shutil.copy2(src_file, dst_file)
            count += 1
            
            progress = (i + 1) / total * 100
            self.progress_var.set(progress)
            self.status_label.config(text=f"正在提取... {i+1}/{total}")
            self.window.update_idletasks()
            
        self.status_label.config(text=f"完成！提取了 {count} 个Markdown文件")
        messagebox.showinfo("成功", f"成功提取 {count} 个Markdown文件！")
        
    def clear_fields(self):
        self.source_dir.set("")
        self.target_dir.set("")
        self.progress_var.set(0)
        self.status_label.config(text="准备就绪")
