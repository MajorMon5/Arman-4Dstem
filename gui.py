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
    QProgressBar, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QDialog, QListView, QListWidget, QListWidgetItem
)

#from stem4d import strain

# from stem4d import strain
# from stem4d import orientations


class Errorwindow_generic(QMessageBox):
    def __init__(self):
        super().__init__()


# class Worker(QThread):
#     def __init__(self, path):
#         super().__init__()
        
#         self.finished = Signal()

#     def setparams(self):
#         self.path = path
#         #self.reciprocal_px_size = reciprocal_pixel_size
#         #self.QR_Rotation = QR_Rotation
#         #self.real_px_size = real_pixel_size


#     def runStrain(self):
#         # Call the strain function with the provided path
#         for paths in path:
#         strain.RunStrainSinglefile(self.path)
#         self.finished.emit()

class Lister(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        

        self.list_widget = QListWidget(self)
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.list_widget.itemClicked.connect(self.on_item_clicked)

    def populate_from_folder(self, folder_path):
        self.clear()
        if not folder_path or not os.path.isdir(folder_path):
            return
        for filename in os.listdir(folder_path):
            full_path = os.path.join(folder_path, filename)
            item = QListWidgetItem(full_path)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.addItem(item)

    def on_item_clicked(self, item):
        print(f"Clicked: {item.text()}")

        # Handle item click event
        if item.checkState() == Qt.CheckState.Checked:
            print(f"Item checked: {item.text()}")
        else:
            print(f"Item unchecked: {item.text()}")

    # def on_item_changed(self, item):
    #     if item.checkState() == Qt.CheckState.Checked:
    #         self.list.append(item.text())
    #     else:
    #         self.list.remove(item.text())


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("4DStem stuff")

        #Layouts (ORDER MATTERS FOR CORRECT ALIGNMENTS)

        self.overall_layout = QVBoxLayout()
        self.setLayout(self.overall_layout)

        self.toolbar_layout = QHBoxLayout()
        self.toolbar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.body_layout = QHBoxLayout()
        self.feet_layout = QHBoxLayout()
        
        


        self.button_layout1 = QGridLayout()

        self.overall_layout.addLayout(self.toolbar_layout)
        self.overall_layout.addLayout(self.body_layout)
        self.overall_layout.addLayout(self.feet_layout)


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