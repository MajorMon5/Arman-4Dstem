import sys
import os
import numpy as np
#import polars
import pandas
import pyqtgraph as pg
import hyperspy.api as hs

from PySide6.QtCore import (
    QThread, Signal
)

from PySide6.QtGui import (
    Qt, QAction, QIcon
)

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLineEdit, QFileDialog, QLabel, QMessageBox,
    QProgressBar, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QDialog, QListView, QListWidget, QListWidgetItem, QStackedWidget,
    QSlider
)

#from stem4d import strain

# from stem4d import strain
# from stem4d import orientations




# class Find_Braggs_Points:
#     def __init__(self):
#         super().__init__()



class Imager(QWidget):
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.data_file = None

        self.layout = QHBoxLayout(self)

        # Real-space display
        self.real_space_view = pg.ImageView()
        self.real_space_view.ui.histogram.hide()
        self.real_space_view.ui.roiBtn.hide()
        self.real_space_view.ui.menuBtn.hide()

        # Diffraction display
        self.diffraction_view = pg.ImageView()
        #self.diffraction_view.ui.histogram.hide()
        self.diffraction_view.ui.roiBtn.hide()
        self.diffraction_view.ui.menuBtn.hide()

        self.layout.addWidget(self.real_space_view)
        self.layout.addWidget(self.diffraction_view)

        # ROI on diffraction (virtual detector)
        self.roi_diff = pg.CircleROI([50, 50], [40, 40],
                                     pen={'color': 'r', 'width': 2},
                                     movable=True, resizable=True, removable=False)
        self.diffraction_view.getView().addItem(self.roi_diff)
        self.roi_diff.sigRegionChanged.connect(self.update_virtual_detector_map)

        # ROI on real-space (probe position selector)
        self.roi_real = pg.RectROI([10, 10], [20, 20],
                                   pen={'color': 'r', 'width': 2},
                                   movable=True, resizable=True, removable=False)
        self.real_space_view.getView().addItem(self.roi_real)
        self.roi_real.sigRegionChanged.connect(self.update_probe_diffraction)

    def load_file(self, path):
        self.file_path = path
        self.data_file = hs.load(self.file_path, lazy=False)
        self.data_file = self.data_file.inav[:100,:100]
        print(self.data_file)




    def create_plot(self, path):
        self.load_file(path)
        try:
            # Store diffraction stack
            self.diffraction_stack = np.array(self.data_file.data, dtype=float)  # (Nx, Ny, qx, qy)
            # diffraction_stack shape: (Nx, Ny, qx, qy)
            # We want to sum over arbitrary diffraction ROIs fast

            # Compute cumulative sum along qx and qy for each probe position
            # Shape stays the same: (Nx, Ny, qx+1, qy+1) to handle edge cases
            self.cumsum_stack = np.zeros((self.diffraction_stack.shape[0],
                                self.diffraction_stack.shape[1],
                                self.diffraction_stack.shape[2]+1,
                                self.diffraction_stack.shape[3]+1), dtype=float)

            self.cumsum_stack[:, :, 1:, 1:] = np.cumsum(np.cumsum(self.diffraction_stack, axis=2), axis=3)
            # Average diffraction pattern
            self.avg_dp = self.diffraction_stack.mean(axis=(0, 1))
            self.diffraction_view.setImage(self.avg_dp.T, autoLevels=True)

            # Real-space intensity map
            self.real_space_image = self.diffraction_stack.sum(axis=(-2, -1))
            self.real_space_view.setImage(self.real_space_image.T, autoLevels=True)

            print("Loaded diffraction stack:", self.diffraction_stack.shape)

        except Exception as e:
            print(f"Error creating plot: {e}")
            QMessageBox.critical(self, "Error", f"Failed to Create Plot:\n{e}")

    def update_virtual_detector_map(self):
        """Fast real-space map update when moving diffraction ROI"""
        if not hasattr(self, "cumsum_stack"):
            return

        # Get ROI bounds in diffraction image coordinates
        bounds = self.roi_diff.pos(), self.roi_diff.size()  # top-left corner + size
        x0 = int(bounds[0][0])
        y0 = int(bounds[0][1])
        x1 = min(x0 + int(bounds[1][0]), self.diffraction_stack.shape[2])
        y1 = min(y0 + int(bounds[1][1]), self.diffraction_stack.shape[3])

        # Clamp to valid indices
        x0, y0 = max(x0, 0), max(y0, 0)

        # Get fast sum
        masked_intensity = self.get_roi_sum(self.cumsum_stack, x0, y0, x1, y1)

        self.real_space_view.setImage(masked_intensity.T, autoLevels=False, autoRange=False)


    def update_probe_diffraction(self):
        """Update diffraction pattern continuously while dragging real-space ROI"""
        if not hasattr(self, "diffraction_stack"):
            return

        nx, ny = self.diffraction_stack.shape[:2]
        mask = np.zeros((nx, ny), dtype=bool)
        roi_slice, roi_mask = self.roi_real.getArraySlice(np.zeros((nx, ny)), self.real_space_view.imageItem)
        mask[roi_slice] = roi_mask




        if np.any(mask):
            selected_dp = self.diffraction_stack[mask].mean(axis=0)  # (qx, qy)
            self.diffraction_view.setImage(selected_dp.T, autoLevels=False, autoRange=False)
        else:
            # fallback: show average diffraction
            self.diffraction_view.setImage(self.avg_dp.T, autoLevels=False, autoRange=False)

    def get_roi_sum(self, cumsum_stack, x0, y0, x1, y1):
        """Fast sum over ROI using integral image (cumsum_stack)"""
        # Use broadcasting over Nx, Ny
        total = (cumsum_stack[:, :, x1, y1]
                - cumsum_stack[:, :, x0, y1]
                - cumsum_stack[:, :, x1, y0]
                + cumsum_stack[:, :, x0, y0])
        return total  # shape: (Nx, Ny)




##################################################################################################
        

# class Worker(QThread):
#     def __init__(self, path):
#         super().__init__()
        
#         self.path = path
#         self.progress = Signal(int)
#         self.finished = Signal()



################################################################################################

class Lister(QWidget):
    fileSelected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(300)
        self.layout = QVBoxLayout(self)

        self.list_widget = QListWidget(self)
        # Use itemChanged so we react to check-state changes (not clicks)
        self.list_widget.itemChanged.connect(self.on_item_changed)

        self.layout.addWidget(self.list_widget)

    def populate_from_folder(self, folder_path):
        self.list_widget.blockSignals(True)   # prevent itemChanged during population
        self.list_widget.clear()

        if not folder_path or not os.path.isdir(folder_path):
            self.list_widget.blockSignals(False)
            print("Lister is empty")
            return

        for filename in os.listdir(folder_path):
            if filename.endswith(".emd") or filename.endswith(".mrc") or filename.endswith(".hspy"):
                full_path = os.path.join(folder_path, filename)
                itemname = os.path.basename(full_path)

                item = QListWidgetItem(itemname)
                item.setData(Qt.ItemDataRole.UserRole, full_path)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.list_widget.addItem(item)

        self.list_widget.blockSignals(False)

    def on_item_changed(self, item: QListWidgetItem):
        """Called when an item's data or check state changes.
           Emit the checked file path to MainWindow, but do not plot here.
           Also enforce single-checked-item behavior.
        """
        # Only respond to check state changes (avoid other changes)
        if item.checkState() == Qt.CheckState.Checked:
            full_path = item.data(Qt.ItemDataRole.UserRole)
            print(f"[Lister] Checked: {full_path}")

            # Enforce single check: uncheck all other items without firing signals
            self.list_widget.blockSignals(True)
            for i in range(self.list_widget.count()):
                it = self.list_widget.item(i)
                if it is not item and it.checkState() == Qt.CheckState.Checked:
                    it.setCheckState(Qt.CheckState.Unchecked)
            self.list_widget.blockSignals(False)

            # Emit the selected path to whoever is listening (MainWindow)
            self.fileSelected.emit(full_path)
        else:
            # Item was unchecked (you can ignore or emit something else if you want)
            print(f"[Lister] Unchecked: {item.text()}")






class MainWindow(QWidget):
    imagerRequested = Signal(str)
    def __init__(self):
        super().__init__()

        self.setWindowTitle("4DStem stuff")
        self.selected_path = None

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
        #self.btn_file_explorer.clicked.connect(self.file_explorer)
        self.btn_file_explorer.clicked.connect(self.folder_explorer)
        self.toolbar_layout.addWidget(self.btn_file_explorer, 0, 1)



        # Parameter edits inside the button/paramters grid layout
        
        self.line1_label = QLabel("Line 1:", self)
        self.line2_label = QLabel("Line 2:", self)
        self.btn1_label = QLabel("button1", self)
        
        
        self.line1 = QLineEdit(self)
        self.line2 = QLineEdit(self)

        #Build the 4dstem image, eventually change this to connect with the lister file name buttons
        self.btn1 = QPushButton("Open 4DSTEM Image", self)
        self.lister.fileSelected.connect(self.set_selected_file)
        self.btn1.clicked.connect(self.btn1_clicked)
        
        #Signals
        


        
        self.button_layout1.addWidget(self.line1_label, 0, 0)
        self.button_layout1.addWidget(self.line1, 0, 1)

        self.button_layout1.addWidget(self.line2_label, 1, 0)
        self.button_layout1.addWidget(self.line2, 1, 1)

        self.button_layout1.addWidget(self.btn1_label, 2, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
        self.button_layout1.addWidget(self.btn1, 3, 0, 1, 2)


        
    


        






###########################################################################################
# Main Functions
###########################################################################################


    def set_selected_file(self, path: str):
        """Receive path from Lister and store it"""
        print(f"[MainWindow] File stored: {path}")
        self.selected_path = path

    def btn1_clicked(self):
        if self.selected_path:
            print(f"[MainWindow] Creating plots for {self.selected_path}")
            self.imager.create_plot(self.selected_path)
        else:
            QMessageBox.warning(self, "No file selected", "Please select a file in the list first.")



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

    # def file_explorer(self):
    #     file, _ = QFileDialog.getOpenFileName(self, "Select File")
    #     if file:
    #         print(f"Selected file path: {file}")
    #         self.file = file
    #         self.btn1_label.setText(f"{self.file}")
    #     else:
    #         print("No file selected.")
    #         # ErrorMessageInvalidFileSelected()













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