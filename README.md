# 🖼️ 图床工具箱

**ImageBed Tools** - 一个集图片资源管理和文档转换于一体的工具集合，采用现代化的Tkinter界面设计。

---

## 📋 功能特性

### 1. 🖼️ 图片复制工具
- 批量将图片从源文件夹复制到Assets目录
- 支持多种图片格式：JPG、JPEG、PNG、GIF、BMP、WebP
- 自动检测并跳过已存在的图片
- 实时日志显示操作进度

### 2. 📄 PDF提取工具
- 从文件夹中提取所有PDF文件
- 保持原有的目录结构
- 将PDF移动到新目录（原文件夹名_PDF）

### 3. 📝 Markdown提取工具
- 从文件夹中提取所有Markdown文件
- 保持原有的目录结构
- 支持自定义目标目录
- 显示提取进度条

### 4. 📊 PPTX转Markdown工具
- 将PowerPoint演示文稿转换为Markdown格式
- 支持自定义图片存储路径
- 自动设置默认输出路径

### 5. 🏷️ Markdown属性工具
- 为Markdown文件添加YAML Frontmatter属性
- 支持多种属性：标题、发布日期、标签、分类、作者等
- 支持批量处理多个文件
- 可选择是否替换已有属性
- 采用PyQt5界面，支持主题切换

---

## 🚀 快速开始

### 运行程序

**Windows用户（推荐）：**
```cmd
双击 Start.cmd 即可启动
```

**Python用户：**
```bash
python main.py
```

### 安装依赖

```bash
pip install -r requirements.txt
```

### 系统要求

- Python 3.6+
- Tkinter（通常随Python一起安装）
- PyQt5（用于Markdown属性工具）
- pptx2md（可选，用于PPTX转换功能）

---

## 📁 项目结构

```
ImageBed-Tools/
├── main.py                 # 主程序入口
├── Start.cmd              # Windows快捷启动脚本
├── requirements.txt        # Python依赖包列表
├── README.md              # 项目说明文档
├── assets/                # 默认图片资源目录
└── utils/                 # 工具模块
    ├── __init__.py
    ├── image_utils.py     # 图片复制工具
    ├── pdf_utils.py       # PDF提取工具
    ├── md_utils.py        # Markdown提取工具
    ├── pptx_utils.py      # PPTX转Markdown工具
    ├── md_attr_utils.py   # Markdown属性工具（模块）
    └── md_attr_standalone.py  # Markdown属性工具（独立运行）
```

---

## 💡 使用说明

### 图床URL格式

上传到assets目录的图片可以通过以下URL访问：

```
https://image.201068.xyz/assets/文件名
```

### 各个工具的详细使用

#### 图片复制工具
1. 点击"🖼️ 图片复制工具"卡片
2. 点击"浏览..."选择包含图片的文件夹
3. 点击"🚀 开始复制"按钮
4. 查看日志确认操作结果

#### PDF提取工具
1. 点击"📄 PDF提取工具"卡片
2. 点击"浏览..."选择包含PDF文件的文件夹
3. 点击"🚀 开始提取"按钮
4. 提取完成后可直接打开输出目录

#### Markdown提取工具
1. 点击"📝 Markdown提取工具"卡片
2. 选择源文件夹和目标文件夹
3. 点击"🚀 开始提取"按钮

#### PPTX转Markdown工具
1. 点击"📊 PPTX转Markdown"卡片
2. 选择要转换的PPTX文件
3. 设置图片存储路径（默认为assets目录）
4. 选择输出文件路径
5. 点击"🚀 开始转换"

#### Markdown属性工具
1. 点击"🏷️ Markdown属性工具"卡片
2. 点击"📁 添加文件"或"📂 添加文件夹"添加Markdown文件
3. 设置所需的属性（描述、图片、标签、分类、作者等）
4. 选择是否"🔄 替换已有属性"
5. 点击"🚀 开始处理"

---

## 🎨 界面设计

- **现代化UI**：采用浅色主题，卡片式布局
- **完美居中对齐**：所有元素在卡片内完美垂直居中
- **统一风格**：所有工具使用一致的设计语言
- **颜色主题**：
  - 主色调：蓝色系 (#3b82f6)
  - 工具卡片：各工具使用不同颜色标识
  - 背景：浅灰色 (#f8f9fa)
  - 文本：深灰 (#1e293b) / 浅灰 (#64748b)

---

## 🔗 相关链接

- 图床地址：https://image.201068.xyz/
- 项目作者：fantasycat6

---

## 📄 许可证

本项目仅供个人学习和使用。

---

## 🙏 致谢

感谢所有为本项目提供支持和建议的用户！
