import logging
import sys
from _thread import start_new_thread
from functools import partial
from os import path

from AudioPlayer import AudioPlayer
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QMessageBox, QLineEdit, \
    QPushButton, QLabel, QAction, QMainWindow, qApp

sys.path.append(path.join(path.dirname(__file__), '..'))
from leecher import Leecher, setup_logging

EMPTY_STATE_MESSAGE = "No files :'("

MAX_COLMUN_COUNT = 1

MAX_ROWS_TABLE = 4

file_list = []


class App(QMainWindow):

    def __init__(self, leecher, parent=None):
        super(App, self).__init__(parent)
        self.form_widget = FormWidget(self)
        self.create_toolbar()
        self.setCentralWidget(self.form_widget)
        self.setGeometry(200, 100, 800, 600)
        self.leecher = leecher
        self.leecher.setup_update_table = self.form_widget.update_table_item
        start_new_thread(self.leecher.broadcast, ())

    def create_toolbar(self):
        exitAct = QAction(QIcon.fromTheme('exit'), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.triggered.connect(qApp.quit)
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAct)


class FormWidget(QWidget):

    def __init__(self, parent):
        super(FormWidget, self).__init__(parent)
        self.title = 'P2P audio streamer'
        self.left = 0
        self.top = 0
        self.width = 300
        self.setWindowTitle(self.title)
        self.layout = QVBoxLayout()
        self.create_text_box(self.layout)
        self.create_search_button(self.layout)
        self.create_files_downloading_table(self.layout)
        self.setLayout(self.layout)
        self.show()

    def create_search_button(self, layout):
        self.button = QPushButton('Search', self)
        self.button.move(20, 80)
        self.button.clicked.connect(self.on_click_search)
        layout.addWidget(self.button)

    def create_text_box(self, layout):
        self.textbox = QLineEdit(self)
        self.textboxLabel = QLabel("File name")
        self.textbox.move(20, 20)
        self.textbox.resize(280, 40)
        layout.addWidget(self.textboxLabel)
        layout.addWidget(self.textbox)

    def create_files_downloading_table(self, layout):
        # Create table
        self.tableFileDownloadingWidgetLabel = QLabel("Downloading")
        self.tableFileDownloadingWidget = QTableWidget()
        self.tableFileDownloadingWidget.setRowCount(MAX_ROWS_TABLE)
        self.tableFileDownloadingWidget.setColumnCount(MAX_COLMUN_COUNT)

        for i in range(0, len(file_list)):
            self.update_table_item(i)

        self.tableFileDownloadingWidget.setHorizontalHeaderLabels(['File name'])
        self.tableFileDownloadingWidget.doubleClicked.connect(self.on_click_downloading_table)

        header = self.tableFileDownloadingWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        layout.addWidget(self.tableFileDownloadingWidgetLabel)
        layout.addWidget(self.tableFileDownloadingWidget)

    @pyqtSlot()
    def update_table_item(self, i):
        i_ = file_list[i - 1]
        self.tableFileDownloadingWidget.setItem(i - 1, 0, QTableWidgetItem(str(i_)))

    @pyqtSlot()
    def on_click_search(self):
        textboxValue = self.textbox.text()
        start_new_thread(self.parent().leecher.search_file_fron_gui, (textboxValue,))
        QMessageBox.question(self, 'Busca', "We are going to download: " + textboxValue, QMessageBox.Ok,
                             QMessageBox.Ok)
        self.textbox.setText("")
        print(file_list)

    @pyqtSlot()
    def on_click_downloading_table(self):
        print("\n")
        for currentQTableWidgetItem in self.tableFileDownloadingWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())
            audio = AudioPlayer(currentQTableWidgetItem.text())
            start_new_thread(audio.start_audio, ())
            print("Sound!")


if __name__ == '__main__':
    setup_logging()
    logging.info('Iniciando GUI')

    leecher = Leecher(file_list)
    leecher.main(gui=True)

    app = QApplication(sys.argv)
    ex = App(leecher=leecher)
    ex.show()
    sys.exit(app.exec_())
