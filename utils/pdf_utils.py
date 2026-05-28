import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext


class PDFExtractTool:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("📄 PDF提取工具")
        self.window.geometry("700x550")
        self.window.configure(bg="#f8f9fa")
        self.window.minsize(650, 500)
        
        self.source_dir = tk.StringVar()
        self.output_dir = None
        self.setup_ui()
        
    def setup_ui(self):
        # 标题栏
        header = tk.Frame(self.window, bg="#ef4444", height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        
        tk.Label(header, text="📄 PDF提取工具", font=("Microsoft YaHei UI", 16, "bold"), 
                bg="#ef4444", fg="#ffffff").pack(pady=15)
        
        # 内容区域
        content = tk.Frame(self.window, bg="#f8f9fa", padx=30, pady=30)
        content.pack(fill=tk.BOTH, expand=True)
        
        # 源文件夹选择
        dir_frame = tk.Frame(content, bg="#f8f9fa")
        dir_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(dir_frame, text="选择包含PDF文件的文件夹:", font=("Microsoft YaHei UI", 11), 
                bg="#f8f9fa", fg="#1e293b").pack(anchor=tk.W, pady=(0, 8))
        
        path_frame = tk.Frame(dir_frame, bg="#f8f9fa")
        path_frame.pack(fill=tk.X)
        
        path_entry = tk.Entry(path_frame, textvariable=self.source_dir, 
                             font=("Microsoft YaHei UI", 10), bg="#ffffff", 
                             fg="#1e293b", relief=tk.SOLID, bd=1, state="readonly")
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = tk.Button(path_frame, text="浏览...", bg="#ef4444", fg="#ffffff",
                              font=("Microsoft YaHei UI", 10), padx=15, pady=6, 
                              relief=tk.FLAT, cursor="hand2", command=self.browse_dir)
        browse_btn.pack(side=tk.RIGHT)
        
        # 操作按钮
        btn_frame = tk.Frame(content, bg="#f8f9fa")
        btn_frame.pack(fill=tk.X, pady=(0, 20))
        
        start_btn = tk.Button(btn_frame, text="🚀 开始提取", bg="#ef4444", fg="#ffffff",
                             font=("Microsoft YaHei UI", 11, "bold"), padx=25, pady=10, 
                             relief=tk.FLAT, cursor="hand2", command=self.start_extract, 
                             state=tk.DISABLED)
        self.start_btn = start_btn
        start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        open_output_btn = tk.Button(btn_frame, text="📂 打开输出目录", bg="#64748b", fg="#ffffff",
                                  font=("Microsoft YaHei UI", 10), padx=20, pady=8, 
                                  relief=tk.FLAT, cursor="hand2", command=self.open_output, 
                                  state=tk.DISABLED)
        self.open_output_btn = open_output_btn
        open_output_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = tk.Button(btn_frame, text="清空", bg="#64748b", fg="#ffffff",
                             font=("Microsoft YaHei UI", 10), padx=20, pady=8, 
                             relief=tk.FLAT, cursor="hand2", command=self.clear_log)
        clear_btn.pack(side=tk.RIGHT)
        
        # 日志区域
        log_frame = tk.LabelFrame(content, text="操作日志", font=("Microsoft YaHei UI", 10, "bold"), 
                                 bg="#ffffff", fg="#1e293b", padx=15, pady=15)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, font=("Consolas", 9), 
                                                 bg="#f8f9fa", fg="#1e293b", 
                                                 wrap=tk.WORD, relief=tk.FLAT)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log("准备就绪，请选择包含PDF文件的文件夹...")
        
    def browse_dir(self):
        dir_path = filedialog.askdirectory(title="选择包含PDF文件的文件夹")
        if dir_path:
            self.source_dir.set(dir_path)
            self.output_dir = dir_path + "_PDF"
            self.start_btn.config(state=tk.NORMAL)
            self.log(f"已选择文件夹: {dir_path}")
            self.log(f"输出目录: {self.output_dir}")
            
    def start_extract(self):
        source_dir = self.source_dir.get()
        if not source_dir or not self.output_dir:
            messagebox.showwarning("警告", "请先选择源文件夹！")
            return
            
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            self.log(f"📂 创建输出目录: {self.output_dir}")
            
        self.log("\n🚀 开始提取PDF文件...")
        
        extracted_count = 0
        
        for root, dirs, files in os.walk(source_dir):
            rel_path = os.path.relpath(root, source_dir)
            target_dir = os.path.join(self.output_dir, rel_path)
            
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
                
            for file in files:
                if file.lower().endswith('.pdf'):
                    source_file = os.path.join(root, file)
                    target_file = os.path.join(target_dir, file)
                    shutil.move(source_file, target_file)
                    extracted_count += 1
                    self.log(f"✅ 提取: {file}")
                        
        self.log(f"\n📊 操作完成！")
        self.log(f"   成功提取: {extracted_count} 个PDF文件")
        
        self.open_output_btn.config(state=tk.NORMAL)
        
        if extracted_count > 0:
            messagebox.showinfo("成功", f"成功提取 {extracted_count} 个PDF文件！")
            
    def open_output(self):
        if self.output_dir and os.path.exists(self.output_dir):
            os.startfile(self.output_dir)
        else:
            messagebox.showerror("错误", "输出目录不存在！")
            
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        self.log("日志已清空...")
