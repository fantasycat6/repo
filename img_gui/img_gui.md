# 图片复制程序

## 简介

本项目是一个使用 Python 和 Tkinter 构建的图形用户界面 (GUI) 程序，用户可以选择一个文件夹，点击“开始”按钮后，将文件夹中的图片文件复制到当前工作目录中的 assets 文件夹中。

## 功能

1. 用户可以选择一个包含图片文件的文件夹。
2. 点击“开始”按钮后，将选择的文件夹中的所有图片文件复制到 assets 文件夹中。
3. 支持的图片格式包括: .jpg, .jpeg, .png, .gif, .bmp。
4. 在文本框中显示复制过程和结果。

## 依赖

- Python 3.x
- tkinter
- shutil

```bash
pip install -r requirements.txt
```

## 启动

```bash
python img_gui.py
```

## 打包

1. 安装依赖:
   确保已安装 Python 3.x 和 tkinter。如果未安装，请根据操作系统的要求进行安装。

2. 运行 Python 脚本:
   使用以下命令安装 PyInstaller:
   
   ```sh
   pip install pyinstaller
   ```
   
3. 生成可执行文件 (.exe):
   在命令行中导航到包含 img_gui.py 文件的目录，并运行以下命令:
   
   ```sh
   pyinstaller --onefile --windowed img_gui.py
   ```
   
      生成的可执行文件将位于 dist/ 文件夹中。
   
5. 使用可执行文件: 在 dist/ 文件夹中找到 `img_gui.exe` 文件，双击运行它。程序启动后，按照以下步骤操作:
   
      - 点击“选择文件夹”按钮，选择包含图片文件的文件夹。
      - 文件夹选择完成后，点击“开始”按钮，开始复制图片文件。
      - 程序会在文本框中显示复制过程和结果。

## 注意事项:

-  请确保在执行复制操作前，已选择包含图片文件的文件夹。
- 复制的图片文件将存储在当前工作目录中的 assets 文件夹中。

版权信息: 本项目遵循 MIT 许可证。