"""
Copyright (c) 2024 豆伯

This software is licensed under the MIT License. See LICENSE for details.
"""
from CodeObfuscator import CodeObfuscator
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from pathlib import Path
from faker import Faker
import random
import string

class ObfuscatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("Obfuscate_code.ui", self)
        # 宣告屬性
        self.ModeItems = ['隨機ascii英數', '混合姓名', '繁中姓名', '簡中姓名', '英文姓名', '日文姓名', '韓文姓名']
        self.fakeLangs = [None, ['zh_TW', 'zh_CN', 'en_US', 'ja_JP', 'ko_KR'], 'zh_TW', 'zh_CN', 'en_US', 'ja_JP', 'ko_KR']
        self.InputFilePath = ""
        self.OutputFilePath = ""
        self.Length =self.Length_SpinBox.value()

        # 設定元件初始值
        self.setAcceptDrops(True)
        self.Obfuscate_Mode.addItems(self.ModeItems)
        self.Mode = self.Obfuscate_Mode.currentText()
        self.InputFile_LineEdit.setText("尚未選擇文件")
        self.OutputFile_LineEdit.setText("尚未選擇文件")
        self.Result_TextBrowser.setPlainText("歡迎使用代碼混淆器，請選擇輸入和輸出文件，然後點擊開始混淆。")
        
        # 綁定事件
        self.InputFile_Button.clicked.connect(self.select_input_file)
        self.OutputFile_Button.clicked.connect(self.select_output_file)
        self.InputFile_LineEdit.textChanged.connect(self.input_path_changed)
        self.OutputFile_LineEdit.textChanged.connect(self.output_path_changed)
        self.Start_Button.clicked.connect(self.start_process)
        self.RandomLength_Button.clicked.connect(self.random_length)
        self.Length_SpinBox.valueChanged.connect(self.set_length)
        self.Obfuscate_Mode.currentTextChanged.connect(self.set_mode)
        
        
        # 初始化預覽
        self.update_preview()

    def input_path_changed(self, text):
        self.InputFilePath = text
        self.OutputFilePath = str(Path(text).parent / f"obfuscated_{Path(text).name}")
        self.OutputFile_LineEdit.setText(self.OutputFilePath)

    def output_path_changed(self, text):
        self.OutputFilePath = text

    def dragEnterEvent(self, event: QDragEnterEvent):
        # 檢查是否為檔案且副檔名為 .py
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().endswith('.py'):
                    event.acceptProposedAction()
                    return
        event.ignore()
    
    def dragMoveEvent(self, event):
        # 允許拖動過程中的視覺回饋
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        # 拖放文件到窗口
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith('.py'):
                self.InputFilePath = file_path
                self.InputFile_LineEdit.setText(file_path)
                self.OutputFilePath = str(Path(file_path).parent / f"obfuscated_{Path(file_path).name}")
                self.OutputFile_LineEdit.setText(self.OutputFilePath)
                break

    def select_input_file(self):
        # 開啟文件選擇器並將選定文件路徑設置到文字框
        self.InputFilePath, _ = QFileDialog.getOpenFileName(self, "選擇輸入文件",filter="Python Files (*.py)")
        if self.InputFilePath:
            self.InputFile_LineEdit.setText(self.InputFilePath)
            # 設定輸出文件路徑
            self.OutputFilePath = str(Path(self.InputFilePath).parent / f"obfuscated_{Path(self.InputFilePath).name}")
            self.OutputFile_LineEdit.setText(self.OutputFilePath)
    
    def select_output_file(self):
        # 開啟文件保存對話框並將選定路徑設置到文字框
        self.OutputFilePath, _ = QFileDialog.getSaveFileName(self, "選擇輸出文件",filter="Python Files (*.py)")
        if self.OutputFilePath:
            self.OutputFile_LineEdit.setText(self.OutputFilePath)

    def set_mode(self):
        # 設定混淆模式
        self.Mode = self.Obfuscate_Mode.currentText()
        self.update_preview()

    def random_length(self):
        # 隨機生成長度
        self.Length_SpinBox.setValue(random.randint(10, 10000))
    
    def set_length(self):
        # 設定長度
        self.Length = self.Length_SpinBox.value()
        self.update_preview()
    
    def update_preview(self):
            # faker_lang = self.faker_langs.get(self.faker_var.get())
            if self.Obfuscate_Mode.currentText() != '隨機ascii英數':
                fake = Faker(self.fakeLangs[self.ModeItems.index(self.Obfuscate_Mode.currentText())])
                names = ''.join(fake.name().replace(' ', '_').replace('.','') + ('_' if i < self.Length-1 else '') for i, _ in enumerate(range(self.Length)))# for _ in range(5)
            else:
                letters = string.ascii_letters + string.digits
                names = ''.join(random.choice(letters) for _ in range(self.Length))# for _ in range(5)
            
            # print(names)
            self.PreView_TextBrowser.setPlainText(names)
    
    def start_process(self):
        # 開始混淆代碼
        if self.InputFilePath and self.OutputFilePath:
            try:
                if self.Obfuscate_Mode.currentText() != '隨機ascii英數':
                    fake = Faker(self.fakeLangs[self.ModeItems.index(self.Obfuscate_Mode.currentText())])
                    name_generator = lambda : ''.join(fake.name().replace(' ', '_').replace('.','') + ('_' if i < self.Length-1 else '') for i, _ in enumerate(range(self.Length)))
                    ob = CodeObfuscator(
                        name_generator=name_generator,
                        length=self.Length
                    )
                else:
                    ob = CodeObfuscator(
                        length=self.Length
                    )
                ob.obfuscate(self.InputFilePath, self.OutputFilePath)
                self.Result_TextBrowser.setPlainText("✅混淆完成，請檢查輸出文件✅")
            except Exception as e:
                self.Result_TextBrowser.setPlainText(f"❗發生錯誤❗：\n{str(e)}")
        else:
            self.Result_TextBrowser.setPlainText("❗請選擇輸入和輸出文件❗")
if __name__ == "__main__":
    app = QApplication([])
    window = ObfuscatorGUI()
    window.show()
    app.exec_()
