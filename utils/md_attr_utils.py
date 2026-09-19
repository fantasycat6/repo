import sys
import os
import re
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QFileDialog,
    QListWidget, QListWidgetItem, QGroupBox, QSpinBox,
    QCheckBox, QGridLayout, QMessageBox, QProgressBar,
    QSplitter, QFrame, QScrollArea
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# 匹配 YAML frontmatter 块：开头 `---` 行到下一个 `---` 行（容忍空 frontmatter、结尾无换行）
FRONTMATTER_RE = re.compile(r'^---[ \t]*\n(?:.*?\n)?---[ \t]*(?:\n|\Z)', re.DOTALL)

class MarkdownProcessor(QThread):
    progress_update = pyqtSignal(int)
    file_processed = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, files, properties, replace_existing=False, parent=None):
        super().__init__(parent)
        self.files = files
        self.properties = properties
        self.replace_existing = replace_existing
    
    def run(self):
        success_count = 0
        skip_count = 0
        error_messages = []
        
        total_files = len(self.files)
        if total_files == 0:
            self.finished.emit(True, "没有需要处理的文件")
            return
        
        for i, file_path in enumerate(self.files):
            try:
                # 每个文件只读取一次，避免重复 IO
                content = self.read_file(file_path)
                has_frontmatter = self.has_frontmatter(content)
                if has_frontmatter and not self.replace_existing:
                    skip_count += 1
                    self.file_processed.emit(f"已跳过(已有属性): {os.path.basename(file_path)}")
                else:
                    self.process_content(file_path, content)
                    success_count += 1
                    if has_frontmatter:
                        self.file_processed.emit(f"已替换: {os.path.basename(file_path)}")
                    else:
                        self.file_processed.emit(f"已处理: {os.path.basename(file_path)}")
            except Exception as e:
                error_messages.append(f"{os.path.basename(file_path)}: {str(e)}")
            
            progress = int((i + 1) / total_files * 100)
            self.progress_update.emit(progress)
        
        result_msg = f"成功处理 {success_count} 个文件"
        if skip_count > 0:
            result_msg += f"，跳过 {skip_count} 个已有属性的文件"
        
        if error_messages:
            # 失败时也保留成功/跳过计数，避免信息丢失
            msg = f"{result_msg}，失败 {len(error_messages)} 个\n\n" + "\n".join(error_messages)
            self.finished.emit(False, msg)
        else:
            self.finished.emit(True, result_msg)
    
    @staticmethod
    def read_file(file_path):
        """读取文件内容，去除 UTF-8 BOM、统一换行为 LF；编码 utf-8 失败时回退 gbk。"""
        with open(file_path, 'rb') as f:
            raw = f.read()
        raw = raw.lstrip(b'\xef\xbb\xbf')
        try:
            content = raw.decode('utf-8')
        except UnicodeDecodeError:
            content = raw.decode('gbk')
        return content.replace('\r\n', '\n').replace('\r', '\n')
    
    def has_frontmatter(self, content):
        return FRONTMATTER_RE.match(content) is not None
    
    def extract_existing_published(self, content):
        """仅从前置 frontmatter 内提取已有 published 日期，避免误匹配正文中的同名文本。"""
        fm_match = FRONTMATTER_RE.match(content)
        if not fm_match:
            return None
        match = re.search(r'^published:\s*(.*?)\s*$', fm_match.group(0), re.MULTILINE)
        return match.group(1).strip() if match else None
    
    def process_content(self, file_path, content):
        try:
            title = self.extract_title(content, file_path)
            mtime = os.path.getmtime(file_path)
            date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
            
            existing_published = self.extract_existing_published(content)
            published_date = existing_published or date_str
            
            updated_date = datetime.now().strftime('%Y-%m-%d')
            
            frontmatter = self.generate_frontmatter(title, published_date, updated_date)
            content_with_frontmatter = self.add_frontmatter(content, frontmatter)
            
            # newline='' 避免 Windows 下把 LF 转成 CRLF（读取时已统一为 LF）
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                f.write(content_with_frontmatter)
        except Exception as e:
            raise RuntimeError(f'处理文件失败: {str(e)}')
    
    def extract_title(self, content, file_path):
        """默认使用文件名（不含扩展名）作为文章标题；
        仅当文件名缺失（如隐藏文件 ".md"）时才回退到正文一级标题。"""
        title = os.path.splitext(os.path.basename(file_path))[0].strip()
        if title and not title.startswith('.'):
            return self.sanitize_title(title)
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('# '):
                return self.sanitize_title(line[2:].strip())
        
        # 文件名不可用（如隐藏文件 ".md"）且无一级标题时，返回空字符串
        return ''
    
    def sanitize_title(self, title):
        # 先转义反斜杠再转义引号：若顺序颠倒，`\` 会在第二步被翻倍成 `\\"`，YAML 解析出错
        title = title.replace('\\', '\\\\')
        title = title.replace('"', '\\"')
        title = title.replace('\n', ' ')
        title = title.replace('\r', ' ')
        return title
    
    @staticmethod
    def yaml_quote(value):
        """将任意字符串转为安全的 YAML 双引号标量。

        转义顺序与 sanitize_title 一致：先反斜杠后引号，否则 `\` 会在
        第二步被翻倍成 `\\"`，导致 YAML 解析出错。
        """
        value = str(value).replace('\\', '\\\\').replace('"', '\\"')
        return '"' + value.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t') + '"'
    
    def generate_frontmatter(self, title, published_date, updated_date):
        p = self.properties
        q = self.yaml_quote
        lines = ['---']
        lines.append(f'title: "{title}"')
        lines.append(f'published: {published_date}')
        
        if p.get('updated'):
            lines.append(f'updated: {q(p["updated"])}')
        else:
            lines.append(f'updated: {updated_date}')
        
        if p.get('description'):
            lines.append(f'description: {q(p["description"])}')
        else:
            lines.append('description: "这是文章的简短描述"')
        
        if p.get('image'):
            lines.append(f'image: {q(p["image"])}')
        else:
            lines.append('image: ../images/firefly1.avif')
        
        if p.get('tags'):
            # 兼容中英文逗号分隔、忽略空项，逐项转义保证 YAML 安全
            tags = [q(t.strip()) for t in p['tags'].replace('，', ',').split(',') if t.strip()]
            lines.append(f'tags: [{", ".join(tags)}]')
        else:
            lines.append('tags: ["标签"]')
        
        if p.get('category'):
            lines.append(f'category: {q(p["category"])}')
        else:
            lines.append('category: "分类"')
        
        if p.get('author'):
            lines.append(f'author: {q(p["author"])}')
        else:
            lines.append('author: "fantasycat6"')
        
        if 'draft' in p:
            lines.append(f'draft: {str(p["draft"]).lower()}')
        else:
            lines.append('draft: false')
        
        if 'pinned' in p:
            lines.append(f'pinned: {str(p["pinned"]).lower()}')
        else:
            lines.append('pinned: false')
        
        if p.get('password'):
            lines.append(f'password: {q(p["password"])}')
        
        if p.get('passwordHint'):
            lines.append(f'passwordHint: {q(p["passwordHint"])}')
        
        if p.get('lang'):
            lines.append(f'lang: {q(p["lang"])}')
        
        if p.get('licenseName'):
            lines.append(f'licenseName: {q(p["licenseName"])}')
        
        if p.get('licenseUrl'):
            lines.append(f'licenseUrl: {q(p["licenseUrl"])}')
        
        if p.get('sourceLink'):
            lines.append(f'sourceLink: {q(p["sourceLink"])}')
        
        if 'comment' in p:
            lines.append(f'comment: {str(p["comment"]).lower()}')
        
        if p.get('slug'):
            lines.append(f'slug: {q(p["slug"])}')
        
        lines.append('---')
        return '\n'.join(lines)
    
    def add_frontmatter(self, content, frontmatter):
        """已有 frontmatter 时用新 frontmatter 替换，否则在开头插入。

        使用 FRONTMATTER_RE 精确定位前置块，可正确处理结尾 ```---``` 无换行
        （EOF）的情况，避免旧逻辑中 find('\n') 返回 -1 导致内容被重复。
        """
        fm_match = FRONTMATTER_RE.match(content)
        if fm_match:
            # 原 frontmatter 直接整体替换，正文原样保留
            return frontmatter + content[fm_match.end():]
        return frontmatter + '\n\n' + content

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_dark_theme = False
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Markdown 属性添加工具')
        self.setGeometry(100, 100, 1000, 700)
        
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        main_layout = QHBoxLayout(self.main_widget)
        
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(80)
        sidebar_layout = QVBoxLayout(self.sidebar)
        
        self.theme_btn = QPushButton('☀️')
        self.theme_btn.setFixedSize(60, 60)
        self.theme_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 12px;
                font-size: 24px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        self.theme_btn.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(self.theme_btn, 0, Qt.AlignCenter)
        
        theme_label = QLabel('主题')
        theme_label.setStyleSheet("color: #888; font-size: 12px;")
        theme_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(theme_label)
        
        sidebar_layout.addStretch()
        
        self.main_content = QWidget()
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.main_content)
        
        content_layout = QHBoxLayout(self.main_content)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.addWidget(left_panel)
        content_splitter.addWidget(right_panel)
        content_splitter.setSizes([380, 550])
        content_layout.addWidget(content_splitter)
        
        self.setup_left_panel(left_layout)
        self.setup_right_panel(right_layout)
        
        self.apply_theme()
    
    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.apply_theme()
    
    def apply_theme(self):
        if self.is_dark_theme:
            self.theme_btn.setText('🌙')
            self.sidebar.setStyleSheet("""
                QWidget {
                    background-color: #2d2d2d;
                    border-radius: 0;
                }
            """)
            self.main_widget.setStyleSheet("""
                QWidget {
                    background-color: #1a1a1a;
                }
            """)
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1a1a1a;
                }
                QPushButton {
                    background-color: #4a90d9;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #3a7bc8;
                }
                QLineEdit, QTextEdit, QSpinBox {
                    background-color: rgba(60, 60, 60, 0.9);
                    color: white;
                    border: 1px solid rgba(100, 100, 100, 0.5);
                    border-radius: 6px;
                    padding: 8px;
                }
                QListWidget {
                    background-color: rgba(60, 60, 60, 0.9);
                    color: white;
                    border: 1px solid rgba(100, 100, 100, 0.5);
                    border-radius: 6px;
                }
                QListWidget::item {
                    padding: 6px;
                }
                QListWidget::item:hover {
                    background-color: rgba(74, 144, 217, 0.5);
                }
                QScrollArea {
                    background-color: rgba(45, 45, 45, 0.9);
                    border: 1px solid rgba(100, 100, 100, 0.5);
                    border-radius: 6px;
                }
                QLabel {
                    color: #cccccc;
                }
                QGroupBox {
                    color: #cccccc;
                    border: 1px solid rgba(100, 100, 100, 0.5);
                    border-radius: 8px;
                    margin-top: 10px;
                    background-color: rgba(45, 45, 45, 0.9);
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 8px 0 8px;
                    color: #4a90d9;
                }
                QCheckBox {
                    color: #cccccc;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border-radius: 4px;
                    border: 2px solid #4a90d9;
                }
                QCheckBox::indicator:checked {
                    background-color: #4a90d9;
                }
                QProgressBar {
                    border: 1px solid rgba(100, 100, 100, 0.5);
                    border-radius: 6px;
                    text-align: center;
                    color: white;
                    background-color: rgba(60, 60, 60, 0.9);
                }
                QProgressBar::chunk {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4a90d9, stop:1 #5cb85c);
                    border-radius: 6px;
                }
            """)
        else:
            self.theme_btn.setText('☀️')
            self.sidebar.setStyleSheet("""
                QWidget {
                    background-color: #e8e8e8;
                    border-radius: 0;
                }
            """)
            self.main_widget.setStyleSheet("""
                QWidget {
                    background-color: #f5f5f5;
                }
            """)
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f5f5f5;
                }
                QPushButton {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2);
                    color: #000;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #5a6fd6, stop:1 #6a4190);
                }
                QLineEdit, QTextEdit, QSpinBox {
                    background-color: white;
                    color: #333;
                    border: 2px solid #e0e0e0;
                    border-radius: 6px;
                    padding: 8px;
                }
                QLineEdit:focus, QTextEdit:focus {
                    border-color: #667eea;
                }
                QListWidget {
                    background-color: white;
                    color: #333;
                    border: 2px solid #e0e0e0;
                    border-radius: 6px;
                }
                QListWidget::item {
                    padding: 6px;
                }
                QListWidget::item:hover {
                    background-color: rgba(102, 126, 234, 0.1);
                }
                QScrollArea {
                    background-color: white;
                    border: 2px solid #e0e0e0;
                    border-radius: 6px;
                }
                QLabel {
                    color: #333;
                }
                QGroupBox {
                    color: #667eea;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    margin-top: 10px;
                    background-color: white;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 8px 0 8px;
                }
                QCheckBox {
                    color: #333;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border-radius: 4px;
                    border: 2px solid #667eea;
                }
                QCheckBox::indicator:checked {
                    background-color: #667eea;
                }
                QProgressBar {
                    border: 2px solid #e0e0e0;
                    border-radius: 6px;
                    text-align: center;
                    color: #333;
                    background-color: white;
                }
                QProgressBar::chunk {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #667eea, stop:1 #764ba2);
                    border-radius: 6px;
                }
            """)
    
    def setup_left_panel(self, layout):
        file_group = QGroupBox('文件选择')
        file_layout = QVBoxLayout(file_group)
        
        self.file_list = QListWidget()
        self.file_list.setMaximumHeight(180)
        self.file_list.setMinimumHeight(100)
        file_layout.addWidget(self.file_list)
        
        btn_layout = QHBoxLayout()
        
        self.add_file_btn = QPushButton('📁 添加文件')
        self.add_file_btn.clicked.connect(self.add_files)
        btn_layout.addWidget(self.add_file_btn)
        
        self.add_folder_btn = QPushButton('📂 添加文件夹')
        self.add_folder_btn.clicked.connect(self.add_folder)
        btn_layout.addWidget(self.add_folder_btn)
        
        self.clear_btn = QPushButton('🗑️ 清空')
        self.clear_btn.clicked.connect(self.clear_files)
        btn_layout.addWidget(self.clear_btn)
        
        file_layout.addLayout(btn_layout)
        
        depth_group = QGroupBox('文件夹深度')
        depth_layout = QHBoxLayout(depth_group)
        
        depth_layout.addWidget(QLabel('遍历深度:'))
        self.depth_spin = QSpinBox()
        self.depth_spin.setMinimum(1)
        self.depth_spin.setMaximum(10)
        self.depth_spin.setValue(2)
        depth_layout.addWidget(self.depth_spin)
        
        file_layout.addWidget(depth_group)
        
        layout.addWidget(file_group)
        
        prop_group = QGroupBox('常用属性')
        prop_layout = QVBoxLayout(prop_group)
        
        grid = QGridLayout()
        
        grid.addWidget(QLabel('描述:'), 0, 0)
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText('文章的简短描述')
        grid.addWidget(self.desc_edit, 0, 1)
        
        grid.addWidget(QLabel('图片:'), 1, 0)
        self.image_edit = QLineEdit()
        self.image_edit.setText('/images/firefly1.avif')
        grid.addWidget(self.image_edit, 1, 1)
        
        grid.addWidget(QLabel('标签:'), 2, 0)
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText('标签1, 标签2')
        grid.addWidget(self.tags_edit, 2, 1)
        
        grid.addWidget(QLabel('分类:'), 3, 0)
        self.category_edit = QLineEdit()
        self.category_edit.setPlaceholderText('分类名称')
        grid.addWidget(self.category_edit, 3, 1)
        
        grid.addWidget(QLabel('作者:'), 4, 0)
        self.author_edit = QLineEdit()
        self.author_edit.setPlaceholderText('fantasycat6')
        grid.addWidget(self.author_edit, 4, 1)
        
        prop_layout.addLayout(grid)
        
        bool_layout = QHBoxLayout()
        self.draft_check = QCheckBox('📝 草稿')
        self.draft_check.setChecked(False)
        bool_layout.addWidget(self.draft_check)
        
        self.pinned_check = QCheckBox('📌 置顶')
        self.pinned_check.setChecked(False)
        bool_layout.addWidget(self.pinned_check)
        
        self.comment_check = QCheckBox('💬 评论')
        self.comment_check.setChecked(True)
        bool_layout.addWidget(self.comment_check)
        
        prop_layout.addLayout(bool_layout)
        
        process_option_group = QGroupBox('处理选项')
        process_option_layout = QVBoxLayout(process_option_group)
        
        self.replace_check = QCheckBox('🔄 替换已有属性')
        self.replace_check.setToolTip('勾选后会替换已有的笔记属性')
        self.replace_check.setChecked(False)
        process_option_layout.addWidget(self.replace_check)
        
        layout.addWidget(process_option_group)
        
        layout.addWidget(prop_group)
        
        self.process_btn = QPushButton('🚀 开始处理')
        self.process_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #5cb85c, stop:1 #4cae4c);
                font-weight: bold;
                padding: 12px;
                font-size: 16px;
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4cae4c, stop:1 #3d8b40);
            }
        """)
        self.process_btn.clicked.connect(self.start_processing)
        layout.addWidget(self.process_btn)
        
        layout.addStretch()
    
    def setup_right_panel(self, layout):
        right_splitter = QSplitter(Qt.Vertical)
        
        log_group = QGroupBox('处理日志')
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        log_layout.addWidget(self.progress_bar)
        
        right_splitter.addWidget(log_group)
        
        advanced_group = QGroupBox('高级属性')
        advanced_layout = QVBoxLayout(advanced_group)
        
        advanced_scroll = QScrollArea()
        advanced_scroll.setWidgetResizable(True)
        
        self.adv_widget = QWidget()
        adv_layout = QVBoxLayout(self.adv_widget)
        adv_layout.setContentsMargins(5, 5, 5, 5)
        
        adv_grid = QGridLayout()
        
        adv_grid.addWidget(QLabel('更新日期:'), 0, 0)
        self.updated_edit = QLineEdit()
        self.updated_edit.setPlaceholderText('2023-09-09')
        adv_grid.addWidget(self.updated_edit, 0, 1)
        
        adv_grid.addWidget(QLabel('语言:'), 1, 0)
        self.lang_edit = QLineEdit()
        self.lang_edit.setPlaceholderText('zh-CN')
        adv_grid.addWidget(self.lang_edit, 1, 1)
        
        adv_grid.addWidget(QLabel('URL Slug:'), 2, 0)
        self.slug_edit = QLineEdit()
        self.slug_edit.setPlaceholderText('my-awesome-post')
        adv_grid.addWidget(self.slug_edit, 2, 1)
        
        adv_grid.addWidget(QLabel('许可证名称:'), 3, 0)
        self.license_name_edit = QLineEdit()
        self.license_name_edit.setPlaceholderText('CC BY-NC-SA 4.0')
        adv_grid.addWidget(self.license_name_edit, 3, 1)
        
        adv_grid.addWidget(QLabel('许可证链接:'), 4, 0)
        self.license_url_edit = QLineEdit()
        self.license_url_edit.setPlaceholderText('https://...')
        adv_grid.addWidget(self.license_url_edit, 4, 1)
        
        adv_grid.addWidget(QLabel('来源链接:'), 5, 0)
        self.source_link_edit = QLineEdit()
        self.source_link_edit.setPlaceholderText('https://...')
        adv_grid.addWidget(self.source_link_edit, 5, 1)
        
        adv_layout.addLayout(adv_grid)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        adv_layout.addWidget(separator)
        
        encrypt_label = QLabel('🔐 加密设置')
        encrypt_label.setStyleSheet('color: #d9534f; font-weight: bold;')
        adv_layout.addWidget(encrypt_label)
        
        self.encrypt_check = QCheckBox('启用加密')
        self.encrypt_check.setChecked(False)
        self.encrypt_check.stateChanged.connect(self.toggle_encrypt_fields)
        adv_layout.addWidget(self.encrypt_check)
        
        encrypt_grid = QGridLayout()
        encrypt_grid.addWidget(QLabel('密码:'), 0, 0)
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText('请输入密码')
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setEnabled(False)
        encrypt_grid.addWidget(self.password_edit, 0, 1)
        
        encrypt_grid.addWidget(QLabel('密码提示:'), 1, 0)
        self.password_hint_edit = QLineEdit()
        self.password_hint_edit.setPlaceholderText('密码提示')
        self.password_hint_edit.setEnabled(False)
        encrypt_grid.addWidget(self.password_hint_edit, 1, 1)
        
        adv_layout.addLayout(encrypt_grid)
        
        adv_layout.addStretch()
        
        advanced_scroll.setWidget(self.adv_widget)
        advanced_layout.addWidget(advanced_scroll)
        
        right_splitter.addWidget(advanced_group)
        right_splitter.setSizes([200, 450])
        
        layout.addWidget(right_splitter)
    
    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, '选择Markdown文件', '', 'Markdown Files (*.md)'
        )
        for file in files:
            if file not in [self.file_list.item(i).text() for i in range(self.file_list.count())]:
                QListWidgetItem(file, self.file_list)
        self.log(f'已添加 {len(files)} 个文件')
    
    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, '选择文件夹')
        if folder:
            max_depth = self.calculate_max_depth(folder)
            
            current_depth = self.depth_spin.value()
            if max_depth > current_depth:
                self.depth_spin.setValue(max_depth)
                self.log(f'检测到文件夹最深层级: {max_depth}，已自动更新深度设置')
            
            depth = self.depth_spin.value()
            md_files = self.find_md_files(folder, depth)
            
            existing_files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
            new_count = 0
            
            for file in md_files:
                if file not in existing_files:
                    QListWidgetItem(file, self.file_list)
                    new_count += 1
            
            self.log(f'从 {folder} 添加了 {new_count} 个文件')
    
    def calculate_max_depth(self, folder):
        max_depth = 1
        
        for root, dirs, files in os.walk(folder):
            current_depth = root[len(folder):].count(os.sep) + 1
            if current_depth > max_depth:
                max_depth = current_depth
        
        return max_depth
    
    def find_md_files(self, folder, depth):
        md_files = []
        
        for root, dirs, files in os.walk(folder):
            current_depth = root[len(folder):].count(os.sep)
            if current_depth >= depth:
                dirs[:] = []
            
            for file in files:
                if file.lower().endswith('.md'):
                    md_files.append(os.path.join(root, file))
        
        return md_files
    
    def clear_files(self):
        self.file_list.clear()
        self.log('文件列表已清空')
    
    def toggle_encrypt_fields(self, state):
        enabled = state == Qt.Checked
        self.password_edit.setEnabled(enabled)
        self.password_hint_edit.setEnabled(enabled)
    
    def get_properties(self):
        props = {}
        
        if self.desc_edit.text():
            props['description'] = self.desc_edit.text()
        if self.image_edit.text():
            props['image'] = self.image_edit.text()
        if self.tags_edit.text():
            props['tags'] = self.tags_edit.text()
        if self.category_edit.text():
            props['category'] = self.category_edit.text()
        if self.author_edit.text():
            props['author'] = self.author_edit.text()
        
        props['draft'] = self.draft_check.isChecked()
        props['pinned'] = self.pinned_check.isChecked()
        
        if self.updated_edit.text():
            props['updated'] = self.updated_edit.text()
        if self.lang_edit.text():
            props['lang'] = self.lang_edit.text()
        if self.slug_edit.text():
            props['slug'] = self.slug_edit.text()
        if self.license_name_edit.text():
            props['licenseName'] = self.license_name_edit.text()
        if self.license_url_edit.text():
            props['licenseUrl'] = self.license_url_edit.text()
        if self.source_link_edit.text():
            props['sourceLink'] = self.source_link_edit.text()
        
        props['comment'] = self.comment_check.isChecked()
        
        if self.encrypt_check.isChecked():
            if self.password_edit.text():
                props['password'] = self.password_edit.text()
            if self.password_hint_edit.text():
                props['passwordHint'] = self.password_hint_edit.text()
        
        return props
    
    def start_processing(self):
        files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        
        if not files:
            QMessageBox.warning(self, '警告', '请先添加要处理的文件')
            return
        
        properties = self.get_properties()
        replace_existing = self.replace_check.isChecked()
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.process_btn.setEnabled(False)
        
        self.processor = MarkdownProcessor(files, properties, replace_existing)
        self.processor.progress_update.connect(self.update_progress)
        self.processor.file_processed.connect(self.log)
        self.processor.finished.connect(self.on_process_finished)
        self.processor.start()
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def on_process_finished(self, success, message):
        self.progress_bar.setVisible(False)
        self.process_btn.setEnabled(True)
        
        if success:
            self.log(message)
            QMessageBox.information(self, '完成', message)
        else:
            self.log(f'错误: {message}')
            QMessageBox.critical(self, '错误', message)
    
    def log(self, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.append(f'[{timestamp}] {message}')
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


