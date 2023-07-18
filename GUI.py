import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
import yinghuadongman
import zipfile
import requests
import os
import configparser
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("影画动漫")
        self.setGeometry(100, 100, 400, 300)

        # 创建URL输入窗口
        self.url_label = QLabel("URL:", self)
        self.url_label.setAlignment(Qt.AlignLeft)
        self.url_entry = QLineEdit(self)

        # 创建按钮用于处理URL
        self.process_button = QPushButton("处理", self)
        self.process_button.clicked.connect(self.process_url)

        # 创建显示结果的窗口
        self.result_label = QLabel("结果:", self)
        self.result_label.setAlignment(Qt.AlignLeft)
        self.result_text = QTextEdit(self)
        self.result_text.setReadOnly(True)

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_entry)
        layout.addWidget(self.process_button)
        layout.addWidget(self.result_label)
        layout.addWidget(self.result_text)

        # 创建主窗口部件并设置布局
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def process_url(self):
        if(not os.path.exists(os.path.join(os.getcwd(),"tmp"))):
            os.mkdir("tmp")
        url = self.url_entry.text()  # 获取输入的URL
        install_ffmpeg_windows()  # 安装FFmpeg并返回FFmpeg路径
        config_file = "config.txt"
        config = configparser.ConfigParser()
        config.read(config_file)
        ffmpeg_path = config.get("FFmpeg","path")
        yinghuadongman.yinghuadongman(url, ffmpeg_path)
        self.result_text.setPlainText("视频下载和合并已完成！")

def install_ffmpeg_windows():
    # 定义下载链接和保存路径
    ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    save_path = os.path.join(os.getcwd(), ffmpeg_url.split('/')[-1])
    config = configparser.ConfigParser()
    config_file = os.path.join(os.getcwd(), "config.txt")
    if os.path.exists(save_path):
        print("FFmpeg压缩包已存在，无需下载！")
    else:
        # 下载FFmpeg压缩包
        response = requests.get(ffmpeg_url)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(response.content)
            print("FFmpeg压缩包下载成功！")
        else:
            print("FFmpeg压缩包下载失败！")
            return
    # 解压缩FFmpeg压缩包
    if os.path.exists(config_file):
        # 读取路径
        config.read(config_file)
        path = config.get("FFmpeg", "path")
        if(not os.path.exists(path)):
            with zipfile.ZipFile(save_path, 'r') as zip_ref:
                zip_ref.extractall(os.getcwd())
                extracted_files = zip_ref.namelist()
            print(extracted_files)
            extract_path = extracted_files[2] if extracted_files else None
            if extract_path:
                config["FFmpeg"] = {"path": os.path.join(os.getcwd(),extract_path.replace('/','\\'))}
                with open(config_file, "w") as configfile:
                    config.write(configfile)
                print("已将FFmpeg路径写入配置文件：", extract_path)
    else:
        with zipfile.ZipFile(save_path, 'r') as zip_ref:
            zip_ref.extractall(os.getcwd())
            extracted_files = zip_ref.namelist()
        print(extracted_files)
        extract_path = extracted_files[2] if extracted_files else None
        if extract_path:
            config["FFmpeg"] = {"path": os.path.join(os.getcwd(),extract_path.replace('/','\\'))}
            with open(config_file, "w") as configfile:
                config.write(configfile)
            print("已将FFmpeg路径写入配置文件：", extract_path)
    print("FFmpeg解压缩完成！")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
