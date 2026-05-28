# pptx2md_gui

## 项目介绍

github：https://github.com/ssine/pptx2md

一个将Powerpoint pptx文件转换为markdown的工具。

## 安装

```bash
pip install pptx2md

pip install --upgrade pptx2md
pip uninstall pptx2md
```

## 帮助

```bash
# pptx2md.exe -h
usage: pptx2md [-h] [-t TITLE] [-o OUTPUT] [-i IMAGE_DIR] [--image-width IMAGE_WIDTH] [--disable-image]
               [--disable-wmf] [--disable-color] [--disable-escaping] [--disable-notes] [--enable-slides] [--wiki]
               [--mdk] [--qmd] [--min-block-size MIN_BLOCK_SIZE] [--page PAGE]
               pptx_path

Convert pptx to markdown

positional arguments:
  pptx_path             path to the pptx file to be converted

options:
  -h, --help            show this help message and exit
  -t TITLE, --title TITLE
                        path to the custom title list file
  -o OUTPUT, --output OUTPUT
                        path of the output file
  -i IMAGE_DIR, --image-dir IMAGE_DIR
                        where to put images extracted
  --image-width IMAGE_WIDTH
                        maximum image with in px
  --disable-image       disable image extraction
  --disable-wmf         keep wmf formatted image untouched(avoid exceptions under linux)
  --disable-color       do not add color HTML tags
  --disable-escaping    do not attempt to escape special characters
  --disable-notes       do not add presenter notes
  --enable-slides       deliniate slides ` --- `
  --wiki                generate output as wikitext(TiddlyWiki)
  --mdk                 generate output as madoko markdown
  --qmd                 generate output as quarto markdown presentation
  --min-block-size MIN_BLOCK_SIZE
                        the minimum character number of a text block to be converted
  --page PAGE           only convert the specified page
```

## 使用

```bash
pptx2md.exe -i ./assets -o AI编程.md  AI编程.pptx 
pptx2md.exe -i ../../../../repo/assets -o AI编程.md AI编程.pptx
```



## gui编写

### 思路

要求:使用python编写pptx2md.exe的使用，

```bash
pptx2md.exe -i ../../../../repo/assets -o AI编程.md AI编程.pptx
```



```bash
# pptx2md.exe -h
usage: pptx2md [-h] [-t TITLE] [-o OUTPUT] [-i IMAGE_DIR] [--image-width IMAGE_WIDTH] [--disable-image]
               [--disable-wmf] [--disable-color] [--disable-escaping] [--disable-notes] [--enable-slides] [--wiki]
               [--mdk] [--qmd] [--min-block-size MIN_BLOCK_SIZE] [--page PAGE]
               pptx_path

Convert pptx to markdown

positional arguments:
  pptx_path             path to the pptx file to be converted

options:
  -h, --help            show this help message and exit
  -t TITLE, --title TITLE
                        path to the custom title list file
  -o OUTPUT, --output OUTPUT
                        path of the output file
  -i IMAGE_DIR, --image-dir IMAGE_DIR
                        where to put images extracted
  --image-width IMAGE_WIDTH
                        maximum image with in px
  --disable-image       disable image extraction
  --disable-wmf         keep wmf formatted image untouched(avoid exceptions under linux)
  --disable-color       do not add color HTML tags
  --disable-escaping    do not attempt to escape special characters
  --disable-notes       do not add presenter notes
  --enable-slides       deliniate slides ` --- `
  --wiki                generate output as wikitext(TiddlyWiki)
  --mdk                 generate output as madoko markdown
  --qmd                 generate output as quarto markdown presentation
  --min-block-size MIN_BLOCK_SIZE
                        the minimum character number of a text block to be converted
  --page PAGE           only convert the specified page
```

制作gui界面，字体为宋体，18



用户可以使用文件管理器文件后缀是`.pptx`的目标ppt文件，

用户可以使用文件管理器选择图片要存放的位置，默认为`../../../../repo/assets`，

输出的文件名可以用户输入文本框填写，默认为ppt的文件名，文件后缀以.md 。

最后生成的md文件内容将图片的地方加上`../../../../`

例如：`../../../../repo/assets`，生成后是`repo/assets`，需要添加`../../../../`，让图片找得到位置



### 成果

```python
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
        output_filename_var.set(os.path.splitext(os.path.basename(file_path))[0] + ".md")


def select_image_dir():
    dir_path = filedialog.askdirectory(
        title="选择图片存储路径"
    )
    if dir_path:
        image_dir_var.set(dir_path)


def convert_to_md():
    pptx_path = pptx_path_var.get()
    image_dir = image_dir_var.get()
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

        # 修改生成的Markdown文件中的图片路径
        with open(output_file, 'r', encoding='utf-8') as file:
            content = file.read()

        content = content.replace(image_dir, f"../../../../{os.path.basename(image_dir)}")

        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(content)

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
image_dir_var = tk.StringVar(value="../../../../repo/assets")
tk.Label(root, text="图片存储路径:", font=font).pack(pady=5)
tk.Entry(root, textvariable=image_dir_var, font=font, width=40).pack()
tk.Button(root, text="选择路径", command=select_image_dir, font=font).pack(pady=5)

# 输出文件名设置
output_filename_var = tk.StringVar()
tk.Label(root, text="输出文件名:", font=font).pack(pady=5)
tk.Entry(root, textvariable=output_filename_var, font=font, width=40).pack()

# 转换按钮
tk.Button(root, text="开始转换", command=convert_to_md, font=font).pack(pady=20)

# 运行主循环
root.mainloop()

```



### 打包

```bash
pyinstaller --onefile --windowed --add-binary "pptx2md.exe;." .\pptx2md_gui.py
```

