import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess

# 工具模块导入
from utils.image_utils import ImageCopyTool
from utils.pdf_utils import PDFExtractTool
from utils.md_utils import MarkdownExtractor
from utils.pptx_utils import PPTX2MDConverter


class ImageBedToolsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图床工具箱 - ImageBed Tools v1.0")
        self.root.geometry("1100x750")
        self.root.resizable(True, True)
        self.root.minsize(1000, 650)
        
        # 配置颜色主题
        self.colors = {
            'bg': '#f8f9fa',
            'bg_dark': '#2d3748',
            'primary': '#4f46e5',
            'primary_hover': '#4338ca',
            'secondary': '#64748b',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'text': '#1e293b',
            'text_light': '#64748b',
            'white': '#ffffff',
            'border': '#e2e8f0',
            'card_border': '#cbd5e1'
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # 创建主框架
        self.main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建顶部导航栏
        self.create_header()
        
        # 创建内容区域
        self.create_content()
        
        # 创建底部状态栏
        self.create_footer()
        
    def create_header(self):
        header = tk.Frame(self.main_frame, bg=self.colors['bg_dark'])
        header.pack(fill=tk.X, side=tk.TOP)
        
        # Logo区域 - 居中对齐
        header_container = tk.Frame(header, bg=self.colors['bg_dark'])
        header_container.pack(fill=tk.BOTH, expand=True, padx=35, pady=22)
        
        # 左侧Logo和标题
        logo_frame = tk.Frame(header_container, bg=self.colors['bg_dark'])
        logo_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        logo_label = tk.Label(logo_frame, text="🖼️", font=("Arial", 34), bg=self.colors['bg_dark'], fg=self.colors['white'])
        logo_label.pack(side=tk.LEFT)
        
        title_frame = tk.Frame(logo_frame, bg=self.colors['bg_dark'])
        title_frame.pack(side=tk.LEFT, padx=18)
        
        title_label = tk.Label(title_frame, text="图床工具箱", font=("Microsoft YaHei UI", 22, "bold"), 
                               bg=self.colors['bg_dark'], fg=self.colors['white'])
        title_label.pack(anchor=tk.W)
        
        subtitle_label = tk.Label(title_frame, text="图片资源管理与文档转换工具", 
                                  font=("Microsoft YaHei UI", 11), bg=self.colors['bg_dark'], 
                                  fg='#94a3b8')
        subtitle_label.pack(anchor=tk.W, pady=(3, 0))
        
        # 右侧操作按钮 - 垂直居中
        actions_frame = tk.Frame(header_container, bg=self.colors['bg_dark'])
        actions_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 使用垂直居中的容器
        buttons_wrapper = tk.Frame(actions_frame, bg=self.colors['bg_dark'])
        buttons_wrapper.pack(anchor=tk.E, expand=True)
        
        help_btn = tk.Button(buttons_wrapper, text="❓ 帮助", 
                            bg=self.colors['secondary'], fg=self.colors['white'],
                            font=("Microsoft YaHei UI", 10, "bold"), padx=18, pady=9,
                            relief=tk.FLAT, cursor="hand2", command=self.show_help)
        help_btn.pack(side=tk.LEFT, padx=7)
        help_btn.bind("<Enter>", lambda e: help_btn.configure(bg='#475569'))
        help_btn.bind("<Leave>", lambda e: help_btn.configure(bg=self.colors['secondary']))
        
        open_assets_btn = tk.Button(buttons_wrapper, text="📂 打开Assets", 
                                   bg=self.colors['primary'], fg=self.colors['white'],
                                   font=("Microsoft YaHei UI", 10, "bold"), padx=18, pady=9,
                                   relief=tk.FLAT, cursor="hand2", command=self.open_assets)
        open_assets_btn.pack(side=tk.LEFT, padx=7)
        open_assets_btn.bind("<Enter>", lambda e: open_assets_btn.configure(bg=self.colors['primary_hover']))
        open_assets_btn.bind("<Leave>", lambda e: open_assets_btn.configure(bg=self.colors['primary']))
        
    def create_content(self):
        content = tk.Frame(self.main_frame, bg=self.colors['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=22)
        
        # 欢迎区域
        welcome_frame = tk.Frame(content, bg=self.colors['bg'])
        welcome_frame.pack(fill=tk.X, pady=(0, 20))
        
        welcome_label = tk.Label(welcome_frame, text="选择工具开始使用", 
                               font=("Microsoft YaHei UI", 16, "bold"), 
                               bg=self.colors['bg'], fg=self.colors['text'])
        welcome_label.pack(anchor=tk.W)
        
        desc_label = tk.Label(welcome_frame, text="以下是所有可用的功能工具，点击卡片即可使用", 
                             font=("Microsoft YaHei UI", 10), 
                             bg=self.colors['bg'], fg=self.colors['text_light'])
        desc_label.pack(anchor=tk.W, pady=(4, 0))
        
        # 工具网格容器
        grid_container = tk.Frame(content, bg=self.colors['bg'])
        grid_container.pack(fill=tk.BOTH, expand=True)
        
        # 定义所有工具
        tools = [
            {
                'icon': '🖼️',
                'title': '图片提取工具',
                'desc': '将图片批量提取到Assets目录',
                'color': '#3b82f6',
                'command': self.open_image_tool
            },
            {
                'icon': '📄',
                'title': 'PDF提取工具',
                'desc': '从文件夹中提取所有PDF文件到新目录',
                'color': '#ef4444',
                'command': self.open_pdf_tool
            },
            {
                'icon': '📝',
                'title': 'Markdown提取工具',
                'desc': '从文件夹中提取所有Markdown文件',
                'color': '#10b981',
                'command': self.open_md_extract_tool
            },
            {
                'icon': '📊',
                'title': 'PPTX转Markdown',
                'desc': '将PowerPoint演示文稿转换为Markdown',
                'color': '#f59e0b',
                'command': self.open_pptx_tool
            },
            {
                'icon': '🏷️',
                'title': 'Markdown属性工具',
                'desc': '为Markdown文件添加YAML属性',
                'color': '#8b5cf6',
                'command': self.open_md_attr_tool
            }
        ]
        
        # 创建工具网格 - 3列布局
        for i, tool in enumerate(tools):
            row = i // 3
            col = i % 3
            self.create_tool_card(grid_container, tool, row, col)
        
        # 配置网格权重
        for col in range(3):
            grid_container.grid_columnconfigure(col, weight=1, uniform="equal")
        
    def create_tool_card(self, parent, tool, row, col):
        # 创建带阴影效果的卡片容器
        card_container = tk.Frame(parent, bg=self.colors['border'], padx=1, pady=1)
        card_container.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # 主卡片
        card = tk.Frame(card_container, bg=self.colors['white'], bd=0, relief=tk.FLAT, padx=18, pady=18)
        card.pack(fill=tk.BOTH, expand=True)
        
        # 统一的最小高度
        card.config(height=210)
        card.pack_propagate(False)
        
        # 绑定点击事件
        card.bind("<Button-1>", lambda e: tool['command']())
        card.configure(cursor="hand2")
        
        # 内部容器，确保垂直居中
        inner_frame = tk.Frame(card, bg=self.colors['white'])
        inner_frame.pack(expand=True)
        
        # 所有元素居中对齐
        icon_label = tk.Label(inner_frame, text=tool['icon'], font=("Arial", 32), bg=self.colors['white'])
        icon_label.pack(pady=(0, 10))
        icon_label.bind("<Button-1>", lambda e: tool['command']())
        icon_label.configure(cursor="hand2")
        
        title_label = tk.Label(inner_frame, text=tool['title'], font=("Microsoft YaHei UI", 12, "bold"), 
                              bg=self.colors['white'], fg=self.colors['text'])
        title_label.pack(pady=(0, 6))
        title_label.bind("<Button-1>", lambda e: tool['command']())
        title_label.configure(cursor="hand2")
        
        desc_label = tk.Label(inner_frame, text=tool['desc'], font=("Microsoft YaHei UI", 9), 
                             bg=self.colors['white'], fg=self.colors['text_light'], 
                             wraplength=230, justify=tk.CENTER)
        desc_label.pack(pady=(0, 14))
        desc_label.bind("<Button-1>", lambda e: tool['command']())
        desc_label.configure(cursor="hand2")
        
        # 使用按钮 - 固定内边距确保高度一致
        use_btn = tk.Button(inner_frame, text="开始使用", bg=tool['color'], fg=self.colors['white'],
                          font=("Microsoft YaHei UI", 9, "bold"), padx=28, pady=7,
                          relief=tk.FLAT, cursor="hand2", command=tool['command'])
        use_btn.pack()
        
        # 按钮悬停效果
        use_btn.bind("<Enter>", lambda e: use_btn.configure(bg=self.adjust_color(tool['color'], -20)))
        use_btn.bind("<Leave>", lambda e: use_btn.configure(bg=tool['color']))
        
    def create_footer(self):
        footer = tk.Frame(self.main_frame, bg=self.colors['border'], height=38)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        footer_label = tk.Label(footer, text="ImageBed Tools v1.0  |  简化您的图片资源管理流程", 
                               font=("Microsoft YaHei UI", 9), bg=self.colors['border'], 
                               fg=self.colors['text_light'])
        footer_label.pack(pady=10)
        
    def open_image_tool(self):
        ImageCopyTool(self.root)
        
    def open_pdf_tool(self):
        PDFExtractTool(self.root)
        
    def open_md_extract_tool(self):
        MarkdownExtractor(self.root)
        
    def open_pptx_tool(self):
        PPTX2MDConverter(self.root)
        
    def open_md_attr_tool(self):
        # 使用subprocess启动独立的PyQt应用
        script_path = os.path.join(os.path.dirname(__file__), 'utils', 'md_attr_standalone.py')
        if os.path.exists(script_path):
            subprocess.Popen([sys.executable, script_path])
        else:
            messagebox.showerror("错误", "Markdown属性工具脚本不存在！")
        
    def open_assets(self):
        assets_path = os.path.join(os.getcwd(), "assets")
        if os.path.exists(assets_path):
            os.startfile(assets_path)
        else:
            if messagebox.askyesno("提示", "Assets目录不存在，是否创建？"):
                os.makedirs(assets_path)
                os.startfile(assets_path)
                
    def show_help(self):
        help_window = tk.Toplevel(self.root)
        help_window.title("帮助文档")
        help_window.geometry("700x580")
        help_window.configure(bg=self.colors['bg'])
        
        content = scrolledtext.ScrolledText(help_window, font=("Microsoft YaHei UI", 10), 
                                           bg=self.colors['white'], fg=self.colors['text'], 
                                           wrap=tk.WORD, padx=25, pady=25)
        content.pack(fill=tk.BOTH, expand=True)
        
        help_text = """
# 图床工具箱使用指南

## 图片复制工具
- 选择包含图片的文件夹
- 工具会自动查找并复制所有图片到assets目录
- 支持格式：jpg, jpeg, png, gif, bmp, webp
- 重复文件会自动跳过

## PDF提取工具
- 选择包含PDF文件的文件夹
- 所有PDF文件会被移动到新目录（原目录名_PDF）
- 保持原有文件夹结构

## Markdown提取工具
- 选择源文件夹和目标文件夹
- 提取所有.md文件到目标位置
- 保持原有的目录结构

## PPTX转Markdown
- 选择要转换的.pptx文件
- 选择图片存储路径
- 自动将演示文稿转换为Markdown格式

## Markdown属性工具
- 为Markdown文件添加YAML frontmatter属性
- 支持标题、日期、标签、分类等多种属性
- 支持批量处理多个文件

## 图床URL格式
上传到assets目录的图片可通过以下URL访问：
https://image.201068.xyz/assets/文件名
        """
        content.insert(tk.END, help_text)
        content.config(state=tk.DISABLED)
        
    def adjust_color(self, color_hex, amount):
        # 简单的颜色调整函数
        color_hex = color_hex.lstrip('#')
        r = max(0, min(255, int(color_hex[0:2], 16) + amount))
        g = max(0, min(255, int(color_hex[2:4], 16) + amount))
        b = max(0, min(255, int(color_hex[4:6], 16) + amount))
        return f'#{r:02x}{g:02x}{b:02x}'


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageBedToolsApp(root)
    root.mainloop()
