import re
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem

from VeriablesUi import Ui_MainWindow
from utils.baidu import get_key

TITLES = ['中文名', '小驼峰', '大驼峰', '匈牙利', '蛇形', '常量']


class Variables(QMainWindow, Ui_MainWindow):
    line = 0
    filters = set()
    result = []

    def __init__(self):
        super(Variables, self).__init__()
        self.setupUi(self)
        self.graphicsView.setVisible(False)
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setFixedHeight(50)
        self.tableWidget.itemClicked.connect(self.on_copy)

        self.clipboard = QApplication.clipboard()
        self.pushButton_2.clicked.connect(self.translate)
        self.pushButton.clicked.connect(self.on_paste)

    def translate(self):
        text = self.lineEdit.text().strip()
        text = re.sub(r'[!?,:，。：；.*#^&$-/\\%@\(\)（）【】]', ' ', text)
        text = re.sub('[" "]+', ' ', text)
        words = text.split(' ')
        self.statusbar.showMessage(f"正在翻译 {text},请稍候...")
        for word in words:
            if not word:
                continue
            if word in self.filters:
                continue
            else:
                ret = get_key(word)
                self.result.append(ret)
                self.update_table()
                self.filters.add(word)
        self.statusbar.showMessage("点击表格可直接复制内容到剪贴板", 2000)

    def on_paste(self):
        self.lineEdit.clear()
        self.lineEdit.setText(self.clipboard.text())
        self.translate()

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

    def on_copy(self, x, y):
        item = self.tableWidget.item(x, y)
        text = item.text()
        self.clipboard.setText(text)
        self.statusbar.showMessage(f'{text} 已复制到剪贴板', 1000)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Variables()
    window.show()
    sys.exit(app.exec_())
