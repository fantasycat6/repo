import os
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess


class PPTX2MDConverter:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("📊 PPTX转Markdown")
        self.window.geometry("650x480")
        self.window.configure(bg="#f8f9fa")
        self.window.minsize(600, 430)
        
        self.pptx_path = tk.StringVar()
        self.image_dir = tk.StringVar()
        self.output_file = tk.StringVar()
        self.setup_ui()
        
    def setup_ui(self):
        # 标题栏
        header = tk.Frame(self.window, bg="#f59e0b", height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        
        tk.Label(header, text="📊 PPTX转Markdown", font=("Microsoft YaHei UI", 16, "bold"), 
                bg="#f59e0b", fg="#ffffff").pack(pady=15)
        
        # 内容区域
        content = tk.Frame(self.window, bg="#f8f9fa", padx=30, pady=30)
        content.pack(fill=tk.BOTH, expand=True)
        
        # PPTX文件选择
        pptx_frame = tk.Frame(content, bg="#f8f9fa")
        pptx_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(pptx_frame, text="选择PPTX文件:", font=("Microsoft YaHei UI", 11), 
                bg="#f8f9fa", fg="#1e293b").pack(anchor=tk.W, pady=(0, 8))
        
        pptx_path_frame = tk.Frame(pptx_frame, bg="#f8f9fa")
        pptx_path_frame.pack(fill=tk.X)
        
        pptx_entry = tk.Entry(pptx_path_frame, textvariable=self.pptx_path, 
                             font=("Microsoft YaHei UI", 10), bg="#ffffff", 
                             fg="#1e293b", relief=tk.SOLID, bd=1)
        pptx_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        pptx_browse_btn = tk.Button(pptx_path_frame, text="浏览...", bg="#f59e0b", fg="#ffffff",
                                   font=("Microsoft YaHei UI", 10), padx=15, pady=6, 
                                   relief=tk.FLAT, cursor="hand2", 
                                   command=self.browse_pptx)
        pptx_browse_btn.pack(side=tk.RIGHT)
        
        # 图片目录选择
        image_frame = tk.Frame(content, bg="#f8f9fa")
        image_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(image_frame, text="图片存储路径:", font=("Microsoft YaHei UI", 11), 
                bg="#f8f9fa", fg="#1e293b").pack(anchor=tk.W, pady=(0, 8))
        
        image_path_frame = tk.Frame(image_frame, bg="#f8f9fa")
        image_path_frame.pack(fill=tk.X)
        
        default_assets = os.path.join(os.getcwd(), "assets")
        self.image_dir.set(default_assets.replace("\\", "/"))
        
        image_entry = tk.Entry(image_path_frame, textvariable=self.image_dir, 
                              font=("Microsoft YaHei UI", 10), bg="#ffffff", 
                              fg="#1e293b", relief=tk.SOLID, bd=1)
        image_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        image_browse_btn = tk.Button(image_path_frame, text="浏览...", bg="#f59e0b", fg="#ffffff",
                                    font=("Microsoft YaHei UI", 10), padx=15, pady=6, 
                                    relief=tk.FLAT, cursor="hand2", 
                                    command=self.browse_image_dir)
        image_browse_btn.pack(side=tk.RIGHT)
        
        # 输出文件选择
        output_frame = tk.Frame(content, bg="#f8f9fa")
        output_frame.pack(fill=tk.X, pady=(0, 25))
        
        tk.Label(output_frame, text="输出Markdown文件:", font=("Microsoft YaHei UI", 11), 
                bg="#f8f9fa", fg="#1e293b").pack(anchor=tk.W, pady=(0, 8))
        
        output_path_frame = tk.Frame(output_frame, bg="#f8f9fa")
        output_path_frame.pack(fill=tk.X)
        
        output_entry = tk.Entry(output_path_frame, textvariable=self.output_file, 
                               font=("Microsoft YaHei UI", 10), bg="#ffffff", 
                               fg="#1e293b", relief=tk.SOLID, bd=1)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        output_browse_btn = tk.Button(output_path_frame, text="浏览...", bg="#f59e0b", fg="#ffffff",
                                     font=("Microsoft YaHei UI", 10), padx=15, pady=6, 
                                     relief=tk.FLAT, cursor="hand2", 
                                     command=self.browse_output)
        output_browse_btn.pack(side=tk.RIGHT)
        
        # 说明文本
        info_label = tk.Label(content, text="注意: 转换需要pptx2md工具，请确保已正确安装。", 
                             font=("Microsoft YaHei UI", 9), bg="#f8f9fa", 
                             fg="#64748b")
        info_label.pack(anchor=tk.W, pady=(0, 20))
        
        # 操作按钮
        btn_frame = tk.Frame(content, bg="#f8f9fa")
        btn_frame.pack(fill=tk.X)
        
        convert_btn = tk.Button(btn_frame, text="🚀 开始转换", bg="#f59e0b", fg="#ffffff",
                               font=("Microsoft YaHei UI", 11, "bold"), padx=25, pady=10, 
                               relief=tk.FLAT, cursor="hand2", command=self.start_convert)
        convert_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = tk.Button(btn_frame, text="清空", bg="#64748b", fg="#ffffff",
                             font=("Microsoft YaHei UI", 10), padx=20, pady=8, 
                             relief=tk.FLAT, cursor="hand2", command=self.clear_fields)
        clear_btn.pack(side=tk.LEFT)
        
    def browse_pptx(self):
        file_path = filedialog.askopenfilename(
            title="选择PPTX文件",
            filetypes=[("PPTX Files", "*.pptx")]
        )
        if file_path:
            self.pptx_path.set(file_path)
            # 默认输出文件与PPTX同目录同名
            base_path = os.path.splitext(file_path)[0]
            self.output_file.set(base_path + ".md")
            
    def browse_image_dir(self):
        dir_path = filedialog.askdirectory(title="选择图片存储路径")
        if dir_path:
            self.image_dir.set(dir_path.replace("\\", "/"))
            
    def browse_output(self):
        file_path = filedialog.asksaveasfilename(
            title="选择输出文件",
            defaultextension=".md",
            filetypes=[("Markdown Files", "*.md")]
        )
        if file_path:
            self.output_file.set(file_path)
            
    def start_convert(self):
        pptx_path = self.pptx_path.get()
        image_dir = self.image_dir.get()
        output_file = self.output_file.get()
        
        if not pptx_path:
            messagebox.showwarning("警告", "请选择要转换的PPTX文件！")
            return
        if not image_dir:
            messagebox.showwarning("警告", "请选择图片存储路径！")
            return
        if not output_file:
            messagebox.showwarning("警告", "请指定输出文件！")
            return
            
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
            
        try:
            cmd = [
                "pptx2md",
                "-i", image_dir,
                "-o", output_file,
                pptx_path
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, 
                                  text=True, encoding='utf-8')
            
            messagebox.showinfo("成功", "PPTX转Markdown转换完成！")
            
        except subprocess.CalledProcessError as e:
            messagebox.showerror("错误", f"转换失败！\n{e.output}")
        except Exception as e:
            messagebox.showerror("错误", f"发生错误: {str(e)}")
            
    def clear_fields(self):
        self.pptx_path.set("")
        self.output_file.set("")
