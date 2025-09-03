import sys
import os
import numpy as np
#import polars
import pandas
import pyqtgraph

from PySide6.QtCore import (
    QThread, Signal
)

from PySide6.QtGui import (
    Qt, QAction, QIcon
)

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLineEdit, QFileDialog, QLabel, QMessageBox,
    QProgressBar, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QDialog, QListView, QListWidget
)

# from stem4d import strain
# from stem4d import orientations


class Errorwindow_generic(QMessageBox):
    def __init__(self):
        super().__init__()


class Worker(QThread):
    def __init__(self):
        super().__init__()
        finished = Signal()

class ListWidget(QListWidget):
    def __init__(self, path):
        super().__init__()
        self.list_widget = QListWidget(self)
        self.setWidget(self.list_widget)

        # self.list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        # self.list_widget.setDragEnabled(True)
        # self.list_widget.setAcceptDrops(True)
        # self.list_widget.setDropIndicatorShown(True)

        self.list_widget.itemChanged.connect(self.on_item_changed)

    def on_item_changed(self, item):
        if item.checkState() == Qt.CheckState.Checked:
            self.list.append(item.text())
        else:
            self.list.remove(item.text())


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("4DStem stuff")

        #Layouts (ORDER MATTERS FOR CORRECT ALIGNMENTS)

        self.overall_layout = QVBoxLayout()
        self.setLayout(self.overall_layout)

        self.toolbar_layout = QHBoxLayout()
        self.body_layout = QHBoxLayout()
        self.feet_layout = QHBoxLayout()
        self.list = list()

        self.button_layout1 = QGridLayout()

        self.overall_layout.addLayout(self.toolbar_layout,  Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.overall_layout.addLayout(self.body_layout)
        self.overall_layout.addLayout(self.feet_layout)

        self.body_layout.addWidget(self.list_layout)
        self.body_layout.addLayout(self.button_layout1)
        
    
        #Sizes
        self.setMinimumSize(800, 600)


        #Toolbar Buttons
        self.btn_folder_explorer = QPushButton("Select Folder")
        self.btn_folder_explorer.clicked.connect(self.folder_explorer)
        self.toolbar_layout.addWidget(self.btn_folder_explorer)

        self.btn_file_explorer = QPushButton("Select File")
        self.btn_file_explorer.clicked.connect(self.file_explorer)
        self.toolbar_layout.addWidget(self.btn_file_explorer)

        # self.btn1_label = QLabel(self, "button1")
        # self.btn1 = QPushButton("Button1")

        # self.button_layout1.addWidget(self.btn1, 0 ,1)

        # self.btn1.clicked.connect(self.btn1_clicked)





    # def btn1_clicked(self):

    # def begin_worker(self):
    
    # def finished(self):
    


    def folder_explorer(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            print(f"Selected folder path: {folder}")
            return folder
        else:
            print("No folder selected.")
            return None
    


    def file_explorer(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file:
            print(f"Selected file path: {file}")
            return file
        else:
            print("No file selected.")
            return None







app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()