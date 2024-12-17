"""
Copyright (c) 2024 豆伯

This software is licensed under the MIT License. See LICENSE for details.
"""
from CodeObfuscator import CodeObfuscator
from SendMail import SendMail
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableView
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QStandardItemModel, QStandardItem, QIcon
from pathlib import Path
from faker import Faker
from queue import Queue, Empty
from threading import Lock
import threading
import keyring
import random
import string
import json
import os


class ObfuscatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("Obfuscate_code.ui", self)
        # 宣告屬性
        self.ModeItems = ['隨機ascii英數', '混合姓名',
                          '繁中姓名', '簡中姓名', '英文姓名', '日文姓名', '韓文姓名']
        self.fakeLangs = [None, ['zh_TW', 'zh_CN', 'en_US', 'ja_JP',
                                 'ko_KR'], 'zh_TW', 'zh_CN', 'en_US', 'ja_JP', 'ko_KR']
        self.InputFilePath = ""
        self.OutputFilePath = ""
        self.Length = self.Length_SpinBox.value()
        self.EmailQueue = []
        self.EmailFilePath = ""
        self.EmailDefaultSubject = "混淆後的程式碼"
        self.EmailDefaultContent = "這是您的混淆後程式碼，請查收附件。"

        # 設定元件初始值
        self.setWindowIcon(QIcon(":/Image/fox.png"))
        self.groupBox_3.setAcceptDrops(True)
        self.groupBox_9.setAcceptDrops(True)
        self.Obfuscate_Mode.addItems(self.ModeItems)
        self.Mode = self.Obfuscate_Mode.currentText()
        self.InputFile_LineEdit.setText("⚠️尚未選擇文件⚠️")
        self.OutputFile_LineEdit.setText("⚠️尚未選擇文件⚠️")
        self.Result_TextBrowser.setPlainText("請選擇輸入和輸出文件，然後點擊開始混淆。")
        self.set_Result_Label("❓未執行❓")
        self.Email_Filename.setText("⚠️無文件⚠️")
        self.subject_textEdit.setPlainText(self.EmailDefaultSubject)
        self.content_textEdit.setPlainText(self.EmailDefaultContent)

        # 初始化Email預覽表格
        self.Email_preview.setModel(QStandardItemModel())
        self.Email_preview.horizontalHeader().setStretchLastSection(True)
        self.Email_preview.setEditTriggers(QTableView.NoEditTriggers)
        model = self.Email_preview.model()
        model.setHorizontalHeaderLabels(['名稱', '模式', '亂數範圍', '地址'])
        self.UpdateEmailPath("./UserConfig/default.json")

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
        self.Email_edit.clicked.connect(lambda: os.startfile("run-config.bat"))
        self.Email_send.clicked.connect(self.send_email)
        self.Email_refresh.clicked.connect(self.update_Email_preview)
        self.subject_textEdit.textChanged.connect(lambda: setattr(
            self, 'EmailDefaultSubject', self.subject_textEdit.toPlainText()))
        self.content_textEdit.textChanged.connect(lambda: setattr(
            self, 'EmailDefaultContent', self.content_textEdit.toPlainText()))

        self.groupBox_3.dragEnterEvent = self.input_dragEnterEvent
        self.groupBox_3.dragMoveEvent = self.input_dragMoveEvent
        self.groupBox_3.dropEvent = self.input_dropEvent
        self.groupBox_9.dragEnterEvent = self.Email_dragEnterEvent
        self.groupBox_9.dragMoveEvent = self.Email_dragMoveEvent
        self.groupBox_9.dropEvent = self.Email_dropEvent

        self.ob = CodeObfuscator()
        self.fake = Faker()
        # 初始化預覽
        self.update_preview()

    def UpdateEmailPath(self, path):
        self.EmailFilePath = path
        self.Email_Filename.setText(Path(path).name)
        self.update_Email_preview()

    def set_Result_Label(self, text):
        self.Result_Label.setText("執行結果:"+text)

    def input_path_changed(self, text):
        self.InputFilePath = text
        self.OutputFilePath = str(
            Path(text).parent / f"obfuscated_{Path(text).name}")
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
                self.OutputFilePath = str(
                    Path(file_path).parent / f"obfuscated_{Path(file_path).name}")
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
                self.UpdateEmailPath(file_path)
                break

    def update_Email_preview(self):
        model = self.Email_preview.model()
        model.clear()
        model.setHorizontalHeaderLabels(['名稱', '模式', '亂數範圍', '地址'])
        self.EmailQueue.clear()

        with open(self.EmailFilePath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for i, item in enumerate(data):
                # 處理預設值
                enabled = item.get('enabled', False)
                mode = item.get('mode', 'normal')
                fake_langs = item.get('fakeLangs', None)
                range_val = item.get('range', [5, 10])
                email = item['email']  # 必要欄位
                name = item['name']    # 必要欄位
                subject = item.get('subject', None)
                content = item.get('content', None)

                if enabled:
                    # 更新表格顯示
                    if mode != 'normal' and mode != 'Normal':
                        row = [
                            QStandardItem(name),
                            QStandardItem(str(fake_langs)),
                            QStandardItem(f"{range_val[0]}~{range_val[1]}"),
                            QStandardItem(email)
                        ]
                    else:
                        row = [
                            QStandardItem(name),
                            QStandardItem("英數亂碼"),
                            QStandardItem(f"{range_val[0]}~{range_val[1]}"),
                            QStandardItem(email)
                        ]
                    model.appendRow(row)

                    # 更新郵件佇列
                    self.EmailQueue.append([
                        mode,
                        fake_langs,
                        range_val,
                        email,
                        name,
                        subject,
                        content
                    ])
        for i in range(4):
            self.Email_preview.resizeColumnToContents(i)

    def select_input_file(self):
        # 開啟文件選擇器並將選定文件路徑設置到文字框
        self.InputFilePath, _ = QFileDialog.getOpenFileName(
            self, "選擇輸入文件", filter="Python Files (*.py)")
        if self.InputFilePath:
            self.InputFile_LineEdit.setText(self.InputFilePath)
            # 設定輸出文件路徑
            self.OutputFilePath = str(
                Path(self.InputFilePath).parent / f"obfuscated_{Path(self.InputFilePath).name}")
            self.OutputFile_LineEdit.setText(self.OutputFilePath)

    def select_output_file(self):
        # 開啟文件保存對話框並將選定路徑設置到文字框
        if self.OutputFilePath:
            self.OutputFilePath, _ = QFileDialog.getSaveFileName(
                self, "選擇輸出文件", filter="Python Files (*.py)", directory=self.OutputFilePath)
        else:
            self.OutputFilePath, _ = QFileDialog.getSaveFileName(
                self, "選擇輸出文件", filter="Python Files (*.py)")
        if self.OutputFilePath:
            self.OutputFile_LineEdit.setText(self.OutputFilePath)

    def select_Email_file(self):
        # 開啟文件選擇器並將選定文件路徑設置到文字框
        self.EmailFilePath, _ = QFileDialog.getOpenFileName(
            self, "選擇Email文件", filter="JSON Files (*.json)")
        if self.EmailFilePath:
            self.UpdateEmailPath(self.EmailFilePath)

    def name_generator(self):
        return ''.join(
            self.fake.name().replace(' ', '_').replace('.', '') +
            ('_' if i < self.Length-1 else '')
            for i in range(self.Length)
        )
    
    def set_mode(self):
        # 設定混淆模式
        self.Mode = self.Obfuscate_Mode.currentText()
        self.fake = Faker(self.fakeLangs[self.ModeItems.index(self.Mode)])
        if self.Mode != self.ModeItems[0]:
            self.ob.set_name_generator(self.name_generator)
        else:
            self.ob.set_name_generator(None)
        self.update_preview()

    def random_length(self):
        # 隨機生成長度
        self.Length_SpinBox.setValue(random.randint(10, 10000))

    def set_length(self):
        # 設定長度
        self.Length = self.Length_SpinBox.value()
        self.update_preview()

    def update_preview(self):
        self.ob.set_name_length(self.Length)
        self.PreView_TextBrowser.setPlainText(self.ob.get_Preview())

    def start_process(self):
        # 開始混淆代碼
        if self.InputFilePath and self.OutputFilePath:
            try:
                
                self.ob.obfuscate(self.InputFilePath, self.OutputFilePath)
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
            self.Email_Result.setText("⚠️請選擇輸入檔案和郵件清單⚠️")
            return

        account = "5b1g0028@stust.edu.tw"
        mailer = SendMail(
            account=account,
            password=keyring.get_password(
                "Obfuscate_code_email_service", account)
        )

        # 建立工作佇列和執行緒同步鎖
        work_queue = Queue()
        status_lock = Lock()
        total = len(self.EmailQueue)
        success = 0

        # 將工作加入佇列
        for task in self.EmailQueue:
            work_queue.put(task)

        def worker():
            nonlocal success
            while True:
                try:
                    # 從佇列取得工作
                    mode, fakeLangs, range_val, email, name, subject, content = work_queue.get_nowait()
                    output_file = str(Path(self.OutputFilePath).parent /
                                      f"obfuscated_{name}_{Path(self.InputFilePath).name}")

                    try:
                        # 生成混淆後的程式碼
                        
                        length = random.randint(range_val[0], range_val[1])
                        Mail_ob = CodeObfuscator()
                        self.fake = Faker(fakeLangs)
                        if mode != "normal":
                            Mail_ob.set_name_generator(self.name_generator)
                        else:
                            Mail_ob.set_name_generator(None)
                        Mail_ob.set_name_length(length)
                        Mail_ob.obfuscate(self.InputFilePath, output_file)

                        # 發送郵件
                        status = mailer.send(
                            to=email,
                            subject=subject or self.EmailDefaultSubject,
                            content=content or self.EmailDefaultContent,
                            attach_file=output_file
                        )

                        if not status:
                            with status_lock:
                                success += 1

                        # 清理臨時檔案
                        if os.path.exists(output_file):
                            os.remove(output_file)

                        # 更新進度
                        with status_lock:
                            remaining = work_queue.qsize()
                            self.Email_Result.setText(
                                f"執行結果：\n處理中... {success}/{total}\n"
                                f"剩餘: {remaining}"
                            )

                    except Exception as e:
                        print(f"Error processing {email}: {str(e)}")
                        if os.path.exists(output_file):
                            os.remove(output_file)

                    work_queue.task_done()

                except Empty:
                    break

        # 啟動多個工作執行緒
        threads = []
        for _ in range(min(4, total)):  # 最多4個執行緒
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            threads.append(t)

        # 等待所有工作完成的監控執行緒
        def monitor():
            for t in threads:
                t.join()
            self.Email_Result.setText(
                f"執行結果：結束！\n"
                f"✅成功: {success}\n"
                f"❌失敗: {total-success}"
            )

        threading.Thread(target=monitor, daemon=True).start()
        self.Email_Result.setText("執行結果：\n開始處理...")

if __name__ == "__main__":
    app = QApplication([])
    window = ObfuscatorGUI()
    window.show()
    app.exec_()
