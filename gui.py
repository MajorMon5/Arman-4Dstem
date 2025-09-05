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


class Imager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)


        

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
        self.setFixedWidth(300)
        self.layout = QVBoxLayout(self)

        self.list_widget = QListWidget(self)
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

        self.layout.addWidget(self.list_widget)
        
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        #self.list_widget.itemChanged.connect(self.on_item_check_changed)

    def populate_from_folder(self, folder_path):
        self.list_widget.clear()
        if not folder_path or not os.path.isdir(folder_path):
            return print("Lister is empty")
        for filename in os.listdir(folder_path): # Iterate through the files in the folder
            full_path = os.path.join(folder_path, filename)

            #Here you can look for files of specific names (IE ignore Camera, include .mrc only, etc.)
            #You can use os.path.splitext(full_path) with endswith to only look for .mrc or certain extensions

            
            itemname = os.path.basename(full_path) #Gets the base name of the file
            item = QListWidgetItem(itemname) #Turns the path for this iteration into an item
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable) #Makes the item checkable
            item.setCheckState(Qt.CheckState.Unchecked) #Sets the initial check state to unchecked
            self.list_widget.addItem(item) #adds the item to the list

    def on_item_clicked(self, item):
        print(f"Clicked: {item.text()}")
        # Handle item click event
        if item.checkState() == Qt.CheckState.Checked:
            print(f"This Item is checked: {item.text()}")
        else:
            print(f"This Item is unchecked: {item.text()}")

    # def on_item_check_changed(self, item):
    #     if item.checkState() == Qt.CheckState.Checked:
    #         print(f"Check state changed: Item checked: {item.text()}")
    #     else:
    #         print(f"Check state changed: Item unchecked: {item.text()}")



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("4DStem stuff")

        #Create Layouts

        self.overall_layout = QVBoxLayout()
        self.setLayout(self.overall_layout)

        self.toolbar_layout = QGridLayout()
        self.toolbar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.body_layout = QHBoxLayout()
        self.feet_layout = QHBoxLayout()

        
        self.button_layout1 = QGridLayout()

        #Overall layout setup
        self.overall_layout.addLayout(self.toolbar_layout)
        self.overall_layout.addLayout(self.body_layout)
        self.overall_layout.addLayout(self.feet_layout)

        #Body layout setup
        self.lister = Lister()
        self.body_layout.addWidget(self.lister)

        self.inputter = QWidget()
        self.body_layout.addWidget(self.inputter)
        self.inputter.setLayout(self.button_layout1)

        self.imager = Imager()
        self.body_layout.addWidget(self.imager)


        #Sizes
        self.setMinimumSize(800, 600)
        self.inputter.setFixedWidth(200)
        self.inputter.setFixedHeight(150)
        

        #Toolbar Buttons
        self.btn_folder_explorer = QPushButton("Select Folder")
        self.btn_folder_explorer.clicked.connect(self.folder_explorer)
        self.toolbar_layout.addWidget(self.btn_folder_explorer, 0, 0)

        self.btn_file_explorer = QPushButton("Select File")
        self.btn_file_explorer.clicked.connect(self.file_explorer)
        self.toolbar_layout.addWidget(self.btn_file_explorer, 0, 1)



        # Parameter edits inside the button/paramters grid layout
        
        self.line1_label = QLabel("Line 1:", self)
        self.line2_label = QLabel("Line 2:", self)
        self.btn1_label = QLabel("button1", self)
        
        
        self.line1 = QLineEdit(self)
        self.line2 = QLineEdit(self)
        self.btn1 = QPushButton("Button1", self)


        
        self.button_layout1.addWidget(self.line1_label, 0, 0)
        self.button_layout1.addWidget(self.line1, 0, 1)

        self.button_layout1.addWidget(self.line2_label, 1, 0)
        self.button_layout1.addWidget(self.line2, 1, 1)

        self.button_layout1.addWidget(self.btn1_label, 2, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
        self.button_layout1.addWidget(self.btn1, 3, 0, 1, 2)


        
        
        
        
        


        

        #Connect buttons
        self.btn1.clicked.connect(self.btn1_clicked)
















###########################################################################################
# Main Functions
###########################################################################################


    def btn1_clicked(self):
        try:
            self.btn1_label.setText(f"{self.folder}")
        except:
            self.btn1_label.setText("Invalid folder selected.")
            #ErrorMessageInvalidFolderSelected()


    # def start_task(self):
    
    # def finished(self):
    

    #def export_to_csv(self):




    def folder_explorer(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            print(f"Selected folder path: {folder}")
            self.folder = folder
            self.btn1_label.setText(f"{self.folder}")
            self.lister.populate_from_folder(self.folder)
        else:
            print("No folder selected.")
            # ErrorMessageInvalidFolderSelected()

    def file_explorer(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file:
            print(f"Selected file path: {file}")
            self.file = file
            self.btn1_label.setText(f"{self.file}")
        else:
            print("No file selected.")
            # ErrorMessageInvalidFileSelected()













###########################################################################################
#Error Message Classes
###########################################################################################


class Errorwindow_generic(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Error")
        self.setIcon(QMessageBox.Icon.Critical)
        self.setStandardButtons(QMessageBox.StandardButton.Ok)




app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()