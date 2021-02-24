import os
import pickle
import re
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QMessageBox

from VeriablesUi import Ui_MainWindow
from utils.baidu import get_key

TITLES = ['中文名', '小驼峰', '大驼峰', '匈牙利', '蛇形', '常量']


class Variables(QMainWindow, Ui_MainWindow):
    line = 0
    filters = set()
    result = []
    translate_thread = None

    def __init__(self):
        super(Variables, self).__init__()
        self.setupUi(self)
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setFixedHeight(50)
        self.tableWidget.cellClicked.connect(self.on_copy)
        self.tableWidget.setToolTip("点击单元格直接复制内容到剪贴板")

        self.clipboard = QApplication.clipboard()
        self.pushButton_2.clicked.connect(self.translate)
        self.pushButton.clicked.connect(self.on_paste)
        self.pushButton_3.clicked.connect(self.clear)
        try:
            with open('variable.his', 'rb') as f:
                self.result = pickle.load(f)
                if self.result:
                    self.filters = set([x[0] for x in self.result])
                    self.update_table()
        except:
            pass

    def translate(self):
        text = self.lineEdit.text().strip()
        text = re.sub(r'[!?,:，。：；.*#^&$-/\\%@\(\)（）【】]', ' ', text)
        text = re.sub('[" "]+', ' ', text)
        words = text.split(' ')
        self.statusbar.showMessage(f"正在翻译 {text},请稍候...", 2000)
        words.reverse()
        for word in words:
            if not word:
                continue
            if word in self.filters:
                for item in self.result:
                    if item[0] == word:
                        assert isinstance(self.result, list)
                        self.result.remove(item)
                        self.result.append(item)
                        self.update_table()
            else:
                self.translate_thread = VariableGen(self)
                self.translate_thread.result.connect(self.update_result)
                self.translate_thread.translate(word)
                # ret = get_key(word)
                # self.result.append(ret)
                # self.update_table()
                # self.filters.add(word)

    def update_result(self, word, ret):
        self.result.append(ret)
        self.update_table()
        self.filters.add(word)

    def on_paste(self):
        self.lineEdit.setText(self.clipboard.text())
        self.translate()

    def clear(self):
        response = QMessageBox.warning(self,"警告","是否要清空历史记录,一旦清除不可恢复!",QMessageBox.Ok|QMessageBox.Cancel)
        if response == QMessageBox.Ok:
            self.result = []
            self.filters = set()
            with open('variable.his','wb') as f:
                pickle.dump(self.result,f)
            self.update_table()

    def update_table(self):
        self.tableWidget.clear()
        self.tableWidget.horizontalHeader().setVisible(True)
        self.tableWidget.horizontalHeader().setStyleSheet("")
        line = 0
        self.tableWidget.setRowCount(len(self.result))
        self.tableWidget.setColumnCount(len(TITLES))
        self.tableWidget.setHorizontalHeaderLabels(TITLES)
        self.result.reverse()
        for item in self.result:
            for i, val in enumerate(item):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(line, i, item)
            line += 1
        self.result.reverse()
        with open('variable.his', 'wb') as f:
            pickle.dump(self.result, f)

    def on_copy(self, x, y):
        item = self.tableWidget.item(x, y)
        text = item.text()
        self.clipboard.setText(text)
        self.statusbar.showMessage(f'{text} 已复制到剪贴板', 1000)


class VariableGen(QThread):
    result = pyqtSignal(str, list)
    word = ''

    def __init__(self, parent):
        super(VariableGen, self).__init__(parent=parent)

    def run(self):
        ret = get_key(self.word)
        self.result.emit(self.word, ret)

    def translate(self, word):
        self.word = word
        self.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Variables()
    window.show()
    sys.exit(app.exec_())
