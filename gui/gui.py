import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QMessageBox, QLineEdit, \
    QPushButton, QLabel, QAction, QMainWindow, qApp

from audioP import playFile

EMPTY_STATE_MESSAGE = "No files :'("

MAX_COLMUN_COUNT = 2

MAX_ROWS_TABLE = 4


class App(QMainWindow):

    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.form_widget = FormWidget(self)
        self.create_toolbar()
        self.setCentralWidget(self.form_widget)
        self.setGeometry(200, 100, 800, 600)

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
        self.create_search_table(self.layout)
        self.create_files_downloading_table(self.layout)

        # Add box layout, add table to box layout and add box layout to widget
        self.setLayout(self.layout)

        # Show widget
        self.show()

    def create_search_button(self, layout):
        # Create a button in the window
        self.button = QPushButton('Search', self)
        self.button.move(20, 80)
        # connect button to function on_click
        self.button.clicked.connect(self.on_click_search)
        layout.addWidget(self.button)

    def create_text_box(self, layout):
        # Create textbox
        self.textbox = QLineEdit(self)
        self.textboxLabel = QLabel("File name")
        self.textbox.move(20, 20)
        self.textbox.resize(280, 40)
        layout.addWidget(self.textboxLabel)
        layout.addWidget(self.textbox)

    def create_search_table(self, layout):
        # Create table

        self.tableSearchWidgetLabel = QLabel("Arquivos no server")
        self.tableSearchWidget = QTableWidget()
        self.tableSearchWidget.setRowCount(MAX_ROWS_TABLE)
        self.tableSearchWidget.setColumnCount(MAX_COLMUN_COUNT)
        self.tableSearchWidget.setItem(0, 0, QTableWidgetItem(EMPTY_STATE_MESSAGE))
        self.tableSearchWidget.move(0, 0)
        self.tableSearchWidget.setHorizontalHeaderLabels(['File name', 'Actions'])
        # table selection change
        self.tableSearchWidget.doubleClicked.connect(self.on_click_search_table)

        btn = QPushButton(self.tableSearchWidget)
        btn.setText('Download')
        self.tableSearchWidget.setCellWidget(0, 1, btn)

        #
        header = self.tableSearchWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        layout.addWidget(self.tableSearchWidgetLabel)
        layout.addWidget(self.tableSearchWidget)

    def create_files_downloading_table(self, layout):
        # Create table
        self.tableFileDownloadingWidgetLabel = QLabel("Downloading")
        self.tableFileDownloadingWidget = QTableWidget()
        self.tableFileDownloadingWidget.setRowCount(MAX_ROWS_TABLE)
        self.tableFileDownloadingWidget.setColumnCount(MAX_COLMUN_COUNT)
        self.tableFileDownloadingWidget.setItem(0, 0, QTableWidgetItem(EMPTY_STATE_MESSAGE))
        self.tableFileDownloadingWidget.move(0, 0)

        # table selection change
        self.tableFileDownloadingWidget.setHorizontalHeaderLabels(['File name', 'Actions'])
        self.tableFileDownloadingWidget.doubleClicked.connect(self.on_click_search_table)

        btn = QPushButton(self.tableFileDownloadingWidget)
        btn.setText('Play')
        btn.clicked.connect(self.play_sound)
        self.tableFileDownloadingWidget.setCellWidget(0, 1, btn)

        #
        header = self.tableFileDownloadingWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        layout.addWidget(self.tableFileDownloadingWidgetLabel)
        layout.addWidget(self.tableFileDownloadingWidget)

    @pyqtSlot()
    def on_click_search(self):
        textboxValue = self.textbox.text()
        QMessageBox.question(self, 'Busca', "We are going to download: " + textboxValue, QMessageBox.Ok,
                             QMessageBox.Ok)
        self.textbox.setText("")

    @pyqtSlot()
    def on_click_search_table(self):
        print("\n")
        for currentQTableWidgetItem in self.tableSearchWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())

    # Greetings
    def play_sound(self):
        playFile('novo.wav')
        print("Sound!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
