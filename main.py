"""
Copyright (c) 2024 豆伯

This software is licensed under the MIT License. See LICENSE for details.
"""
from CodeObfuscator import CodeObfuscator
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QStandardItemModel, QStandardItem
from pathlib import Path
from faker import Faker
from SendMail import SendMail
import keyring
import threading
import random
import string
import json
import os

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
        self.EmailQueue = []
        self.EmailFilePath = ""

        # 設定元件初始值
        self.groupBox_3.setAcceptDrops(True)
        self.groupBox_9.setAcceptDrops(True)
        self.Obfuscate_Mode.addItems(self.ModeItems)
        self.Mode = self.Obfuscate_Mode.currentText()
        self.InputFile_LineEdit.setText("⚠️尚未選擇文件⚠️")
        self.OutputFile_LineEdit.setText("⚠️尚未選擇文件⚠️")
        self.Result_TextBrowser.setPlainText("請選擇輸入和輸出文件，然後點擊開始混淆。")
        self.set_Result_Label("❓未執行❓")
        self.Email_Filename.setText("⚠️無文件⚠️")

        # 初始化Email預覽表格
        self.Email_preview.setModel(QStandardItemModel())
        self.Email_preview.horizontalHeader().setStretchLastSection(True)
        self.Email_preview.setEditTriggers(QTableView.NoEditTriggers)
        model = self.Email_preview.model()
        model.setHorizontalHeaderLabels(['名稱', '模式', '亂數範圍', '地址'])
        
        # 綁定事件
        self.InputFile_Button.clicked.connect(self.select_input_file)
        self.OutputFile_Button.clicked.connect(self.select_output_file)
        self.InputFile_LineEdit.textChanged.connect(self.input_path_changed)
        self.OutputFile_LineEdit.textChanged.connect(self.output_path_changed)
        self.Start_Button.clicked.connect(self.start_process)
        self.RandomLength_Button.clicked.connect(self.random_length)
        self.Length_SpinBox.valueChanged.connect(self.set_length)
        self.Obfuscate_Mode.currentTextChanged.connect(self.set_mode)
        self.Email_openfile.clicked.connect(self.select_Email_file)
        self.Email_send.clicked.connect(self.send_email)

        self.groupBox_3.dragEnterEvent = self.input_dragEnterEvent
        self.groupBox_3.dragMoveEvent = self.input_dragMoveEvent
        self.groupBox_3.dropEvent = self.input_dropEvent
        self.groupBox_9.dragEnterEvent = self.Email_dragEnterEvent
        self.groupBox_9.dragMoveEvent = self.Email_dragMoveEvent
        self.groupBox_9.dropEvent = self.Email_dropEvent
        
        # 初始化預覽
        self.update_preview()

    def set_Result_Label(self, text):
        self.Result_Label.setText("執行結果:"+text)

    def input_path_changed(self, text):
        self.InputFilePath = text
        self.OutputFilePath = str(Path(text).parent / f"obfuscated_{Path(text).name}")
        self.OutputFile_LineEdit.setText(self.OutputFilePath)

    def output_path_changed(self, text):
        self.OutputFilePath = text

    def input_dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().endswith('.py'):
                    event.acceptProposedAction()
                    return
        event.ignore()
    
    def input_dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def input_dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith('.py'):
                self.InputFilePath = file_path
                self.InputFile_LineEdit.setText(file_path)
                self.OutputFilePath = str(Path(file_path).parent / f"obfuscated_{Path(file_path).name}")
                self.OutputFile_LineEdit.setText(self.OutputFilePath)
                break

    def Email_dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().endswith('.json'):
                    event.acceptProposedAction()
                    return
        event.ignore()
    
    def Email_dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def Email_dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith('.json'):
                self.EmailFilePath = file_path
                self.Email_Filename.setText(Path(file_path).name)
                self.update_Email_preview()
                break
        
    def update_Email_preview(self):
        model = self.Email_preview.model()
        model.clear()
        model.setHorizontalHeaderLabels(['名稱', '模式', '亂數範圍', '地址'])
        self.EmailQueue.clear()
        with open(self.EmailFilePath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for i, item in enumerate(data):
                row = [QStandardItem(item['name']), QStandardItem(item['mode']), QStandardItem(f"{item['range'][0]} - {item['range'][1]}"), QStandardItem(item['email'])]
                model.appendRow(row)
                self.EmailQueue.append([item['mode'],item['fakeLangs'],item['range'],item['email']])

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
        if self.OutputFilePath:
            self.OutputFilePath, _ = QFileDialog.getSaveFileName(self, "選擇輸出文件",filter="Python Files (*.py)", directory=self.OutputFilePath)
        else:
            self.OutputFilePath, _ = QFileDialog.getSaveFileName(self, "選擇輸出文件",filter="Python Files (*.py)")
        if self.OutputFilePath:
            self.OutputFile_LineEdit.setText(self.OutputFilePath)

    def select_Email_file(self):
        # 開啟文件選擇器並將選定文件路徑設置到文字框
        self.EmailFilePath, _ = QFileDialog.getOpenFileName(self, "選擇Email文件",filter="JSON Files (*.json)")
        if self.EmailFilePath:
            self.Email_Filename.setText(Path(self.EmailFilePath).name)
            self.update_Email_preview()
    
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
                self.set_Result_Label("✅完成✅")
                self.Result_TextBrowser.setPlainText("無錯誤，請檢查輸出文件")
            except Exception as e:
                self.set_Result_Label("❗錯誤❗")
                self.Result_TextBrowser.setPlainText(f"發生例外情況：\n{str(e)}")
        else:
            self.set_Result_Label("❗錯誤❗")
            self.Result_TextBrowser.setPlainText("請設定輸入和輸出文件")
    
    def send_email(self):
        if not self.InputFilePath or not self.EmailQueue:
            self.Email_Result.setText("請選擇輸入檔案和郵件清單")
            return
            
        def send_thread():
            try:
                # 建立郵件發送實例
                account = "5b1g0028@stust.edu.tw"
                mailer = SendMail(
                    account=account,  # 需要設定
                    password=keyring.get_password("Obfuscate_code_email_service", account)
                )
                
                total = len(self.EmailQueue)
                success = 0
                
                for mode, fakeLangs, range_val, email in self.EmailQueue:
                    try:
                        # 為每個收件者生成獨特的混淆程式碼
                        output_file = str(Path(self.OutputFilePath).parent / f"obfuscated_{email.split('@')[0]}_{Path(self.InputFilePath).name}")
                        
                        # 根據模式設定混淆器
                        if mode != "normal":  # normal 使用預設的 ascii 英數
                            fake = Faker(fakeLangs)  # 可以根據需求調整語言
                            length = random.randint(range_val[0], range_val[1]+1)
                            name_generator = lambda: ''.join(fake.name().replace(' ', '_').replace('.','') + ('_' if i < random.randint(range_val[0], range_val[1])-1 else '') for i, _ in enumerate(range(length)))
                            ob = CodeObfuscator(
                                name_generator=name_generator,
                                length=random.randint(range_val[0], range_val[1])
                            )
                        else:
                            ob = CodeObfuscator(
                                length=random.randint(range_val[0], range_val[1])
                            )
                        
                        # 生成混淆後的程式碼
                        ob.obfuscate(self.InputFilePath, output_file)
                        
                        # 發送郵件
                        status = mailer.send(
                            to=email,
                            subject="混淆後的程式碼",
                            content="這是您的混淆後程式碼，請查收附件。",
                            attach_file=output_file
                        )
                        
                        if not status:
                            success += 1
                            os.remove(output_file)
                        
                        # 更新UI
                        self.Email_Result.setText(f"執行結果：\n處理中... {success}/{total}")
                        
                    except Exception as e:
                        print(f"Error sending to {email}: {str(e)}")
                        
                # 完成後更新UI
                self.Email_Result.setText(f"執行結果：\n完成！\n成功: {success}\n失敗: {total-success}")
                
            except Exception as e:
                self.Email_Result.setText(f"執行結果：\n發生錯誤：\n{str(e)}")
        
        # 啟動執行緒
        threading.Thread(target=send_thread, daemon=True).start()
        self.Email_Result.setText("執行結果：\n開始處理...")

if __name__ == "__main__":
    app = QApplication([])
    window = ObfuscatorGUI()
    window.show()
    app.exec_()
