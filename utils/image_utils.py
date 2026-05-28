import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext


class ImageCopyTool:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("🖼️ 图片提取工具")
        self.window.geometry("700x550")
        self.window.configure(bg="#f8f9fa")
        self.window.minsize(650, 500)
        
        self.source_dir = tk.StringVar()
        self.setup_ui()
        
    def setup_ui(self):
        # 标题栏
        header = tk.Frame(self.window, bg="#3b82f6", height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        
        tk.Label(header, text="🖼️ 图片提取工具", font=("Microsoft YaHei UI", 16, "bold"), 
                bg="#3b82f6", fg="#ffffff").pack(pady=15)
        
        # 内容区域
        content = tk.Frame(self.window, bg="#f8f9fa", padx=30, pady=30)
        content.pack(fill=tk.BOTH, expand=True)
        
        # 源文件夹选择
        dir_frame = tk.Frame(content, bg="#f8f9fa")
        dir_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(dir_frame, text="选择包含图片的文件夹:", font=("Microsoft YaHei UI", 11), 
                bg="#f8f9fa", fg="#1e293b").pack(anchor=tk.W, pady=(0, 8))
        
        path_frame = tk.Frame(dir_frame, bg="#f8f9fa")
        path_frame.pack(fill=tk.X)
        
        path_entry = tk.Entry(path_frame, textvariable=self.source_dir, 
                             font=("Microsoft YaHei UI", 10), bg="#ffffff", 
                             fg="#1e293b", relief=tk.SOLID, bd=1)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = tk.Button(path_frame, text="浏览...", bg="#3b82f6", fg="#ffffff",
                              font=("Microsoft YaHei UI", 10), padx=15, pady=6, 
                              relief=tk.FLAT, cursor="hand2", command=self.browse_dir)
        browse_btn.pack(side=tk.RIGHT)
        
        # 操作按钮
        btn_frame = tk.Frame(content, bg="#f8f9fa")
        btn_frame.pack(fill=tk.X, pady=(0, 20))
        
        start_btn = tk.Button(btn_frame, text="🚀 开始提取", bg="#10b981", fg="#ffffff",
                             font=("Microsoft YaHei UI", 11, "bold"), padx=25, pady=10, 
                             relief=tk.FLAT, cursor="hand2", command=self.start_copy)
        start_btn.pack(side=tk.LEFT)
        
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
        
        self.log("准备就绪，请选择包含图片的文件夹...")
        
    def browse_dir(self):
        dir_path = filedialog.askdirectory(title="选择包含图片的文件夹")
        if dir_path:
            self.source_dir.set(dir_path)
            self.log(f"已选择文件夹: {dir_path}")
            
    def start_copy(self):
        source_dir = self.source_dir.get()
        if not source_dir:
            messagebox.showwarning("警告", "请先选择源文件夹！")
            return
            
        assets_dir = os.path.join(os.getcwd(), "assets")
        if not os.path.exists(assets_dir):
            os.makedirs(assets_dir)
            self.log(f"📂 创建Assets目录: {assets_dir}")
            
        self.log("\n🚀 开始查找并提取图片...")
        
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
        copied_count = 0
        skipped_count = 0
        
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.lower().endswith(image_extensions):
                    source_file = os.path.join(root, file)
                    target_file = os.path.join(assets_dir, file)
                    
                    if os.path.exists(target_file):
                        skipped_count += 1
                        self.log(f"⚠️  跳过已存在: {file}")
                    else:
                        shutil.copy2(source_file, target_file)
                        copied_count += 1
                        self.log(f"✅ 提取成功: {file}")
                        
        self.log(f"\n📊 操作完成！")
        self.log(f"   成功复制: {copied_count} 个文件")
        self.log(f"   跳过重复: {skipped_count} 个文件")
        
        if copied_count > 0:
            messagebox.showinfo("成功", f"成功提取 {copied_count} 张图片到Assets目录！")
            
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        self.log("日志已清空...")
