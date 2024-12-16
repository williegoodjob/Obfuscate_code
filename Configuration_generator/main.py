from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QStyledItemDelegate, QPlainTextEdit, QSizePolicy
from dataclasses import dataclass
from PyQt5.QtCore import Qt, QAbstractTableModel, QSize
import json
import sys

@dataclass
class ConfigItem:
    enabled: bool = False
    name: str = ""
    email: str = ""
    mode: str = "normal"
    fakeLangs: list = None
    range: list = None
    subject: str = None
    content: str = None
    
    def __post_init__(self):
        if self.fakeLangs is None:
            self.fakeLangs = []
        if self.range is None:
            self.range = []

class ConfigTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent):
        return len(self._data)

    def columnCount(self, parent):
        return 8

    def data(self, index, role):
        if not index.isValid():
            return None
            
        if role == Qt.CheckStateRole and index.column() == 0:
            item = self._data[index.row()]
            return Qt.Checked if item.enabled else Qt.Unchecked
            
        if role == Qt.DisplayRole:
            item = self._data[index.row()]
            if index.column() == 1:
                return item.name
            elif index.column() == 2:
                return item.email
            elif index.column() == 3:
                return item.mode
            elif index.column() == 4:
                return ', '.join(item.fakeLangs) if item.fakeLangs else '-'
            elif index.column() == 5:
                return f'{item.range[0]} ~ {item.range[1]}' if item.range else '-'
            elif index.column() == 6:
                return item.subject or '-'
            elif index.column() == 7:
                return item.content or '-'
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                headers = ['啟用','姓名', '信箱地址', '模式', 'FakeLangs', '長度範圍', '主旨', '內容']
                return headers[section]
            if orientation == Qt.Vertical:
                return str(section + 1)
        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        if index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def setData(self, index, value, role):
        if not index.isValid():
            return False
            
        if role == Qt.EditRole:
            row = index.row()
            col = index.column()
            item = self._data[row]
            if value:
                if col == 1:
                    item.name = str(value)
                elif col == 2:
                    item.email = str(value)
                elif col == 3:
                    item.mode = str(value)
                elif col == 4:
                    item.fakeLangs = str(value).split(',') if value != '-' else []
                elif col == 5:
                    try:
                        if value != '-':
                            ranges = str(value).split('~')
                            item.Range = [int(r.strip()) for r in ranges]
                        else:
                            item.Range = []
                    except:
                        return False
                elif col == 6:
                    item.subject = str(value)
                elif col == 7:
                    item.content = str(value)
            self.dataChanged.emit(index, index)
            return True
            
        if role == Qt.CheckStateRole and index.column() == 0:
            row = index.row()
            self._data[row].enabled = (value == Qt.Checked)
            self.dataChanged.emit(index, index)
            return True
            
        return False

class TextEditDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        if index.column() == 7:  # 內容欄位
            editor = QPlainTextEdit(parent)
            # 設定最小尺寸
            editor.setMinimumSize(400, 200)
            # 設定大小策略
            editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            return editor
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        if isinstance(editor, QPlainTextEdit):
            editor.setPlainText(index.data() or '')
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if isinstance(editor, QPlainTextEdit):
            model.setData(index, editor.toPlainText(), Qt.EditRole)
        else:
            super().setModelData(editor, model, index)

    def sizeHint(self, option, index):
        # 設定單元格提示大小
        if index.column() == 7:
            return QSize(400, 200)
        return super().sizeHint(option, index)

    def updateEditorGeometry(self, editor, option, index):
        if isinstance(editor, QPlainTextEdit):
            # 獲取表格視圖
            view = editor.parent()
            # 獲取視窗底部位置
            bottom_boundary = view.height()
            
            # 計算編輯框位置
            x = option.rect.x()
            y = option.rect.y()
            width = 400
            height = 200
            
            # 如果編輯框會超出底部
            if (y + height) > bottom_boundary:
                # 向上移動編輯框
                y = bottom_boundary - height - 10  # 10為邊距
            
            # 設定編輯器位置和大小
            editor.setGeometry(x, y, width, height)
        else:
            super().updateEditorGeometry(editor, option, index)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('CG.ui', self)
        self.ConfigData = []
        self.ConfigFile = ''
        
        # 綁定檔案操作事件
        self.actionNew.triggered.connect(self.newfile)
        self.actionOpen.triggered.connect(self.openFile)
        self.actionSave.triggered.connect(self.saveFile)
        
        # 初始化表格
        model = ConfigTableModel(self.ConfigData)
        self.tableView_Overview.setModel(model)
        # 連接信號
        model.dataChanged.connect(self.on_data_changed)
        self.adjust_columns()
        
        # 設定delegate
        delegate = TextEditDelegate()
        self.tableView_Overview.setItemDelegateForColumn(7, delegate)

    def adjust_columns(self):
        for i in range(8):
            self.tableView_Overview.resizeColumnToContents(i)

    def on_data_changed(self, topLeft, bottomRight):
        self.adjust_columns()

    def newfile(self):
        fileName, _ = QFileDialog.getSaveFileName(self, "儲存檔案", "", "JSON Files (*.json)")
        if fileName:
            self.ConfigFile = fileName
            self.ConfigData = []
            model = ConfigTableModel(self.ConfigData)
            model.dataChanged.connect(self.on_data_changed)
            self.tableView_Overview.setModel(model)
            self.adjust_columns()

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "開啟檔案", "", "JSON Files (*.json)")
        if fileName:
            self.ConfigFile = fileName
            with open(fileName, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.ConfigData = [ConfigItem(**item) for item in data]
                model = ConfigTableModel(self.ConfigData)
                model.dataChanged.connect(self.on_data_changed)
                self.tableView_Overview.setModel(model)
                self.adjust_columns()

    def saveFile(self):
        if self.ConfigFile:
            with open(self.ConfigFile, 'w', encoding='utf-8') as f:
                cleaned_data = []
                for item in self.ConfigData:
                    item_dict = {}
                    if item.enabled:
                        item_dict['enabled'] = item.enabled
                    if item.name:
                        item_dict['name'] = item.name
                    if item.email:
                        item_dict['email'] = item.email
                    if item.mode and item.mode != "normal":
                        item_dict['mode'] = item.mode
                    if item.fakeLangs:
                        item_dict['fakeLangs'] = item.fakeLangs
                    if item.range and len(item.range) == 2:
                        item_dict['range'] = item.range
                    if item.subject:
                        item_dict['subject'] = item.subject
                    if item.content:
                        item_dict['content'] = item.content
                    if item_dict:
                        cleaned_data.append(item_dict)
                json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())