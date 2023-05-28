# Setting the Qt bindings for QtPy
import os
import shutil

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTabWidget, QFileDialog, QPushButton

from grip import Grip
from loader import LoadingTranslucentScreen

os.environ["QT_API"] = "pyqt5"

from qtpy.QtWidgets import QWidget, QVBoxLayout

from pyvistaqt import QtInteractor
import pyvista as pv


class PanelTab1(QWidget):
    def __init__(self, *args, **kwargs):
        super(PanelTab1, self).__init__(*args, **kwargs)
        self.VLayout = QVBoxLayout()
        self.setLayout(self.VLayout)
        self.VLayout.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)

        self.pushButton = QPushButton(self)
        self.pushButton.setText("save")


class Panel(QWidget):
    fileSave = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Panel, self).__init__(*args, **kwargs)

        self.VLayout = QVBoxLayout()
        self.setLayout(self.VLayout)
        self.VLayout.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)

        self.tabWidget = QTabWidget(self)
        self.grip = Grip(self, self)


        self.VLayout.addWidget(self.grip)
        self.VLayout.addWidget(self.tabWidget)

        tab1 = PanelTab1()
        tab1.pushButton.clicked.connect(self.fileSave)
        self.tabWidget.setTabPosition(QTabWidget.South)
        self.tabWidget.addTab(tab1, "tab1")

    def emitFileSave(self):
        self.fileSave.emit()

class Mesh_Plotter(QWidget):
    readError = pyqtSignal(str)


    def __init__(self, *args, **kwargs):
        super(Mesh_Plotter, self).__init__(*args, **kwargs)

        self.plotter = QtInteractor(self)

        self.file = None
        self.VLayout = QVBoxLayout()
        self.VLayout.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.VLayout)
        self.panel = Panel()
        self.panel.fileSave.connect(self.fileSave)

        self.loader = LoadingTranslucentScreen(self, "loading")
        # layout

        self.VLayout.addWidget(self.plotter.interactor)
        self.VLayout.addWidget(self.panel)
        self.VLayout.setStretch(0, 3)
        self.VLayout.setStretch(1, 1)

    def plotFile(self, file):
        try:
            self.file = file
            reader = pv.get_reader(file)
            mesh = reader.read()
            self.plotter.add_mesh(mesh, show_edges=True)
            _ = self.plotter.add_camera_orientation_widget()
            self.plotter.reset_camera()
        except ValueError as e:
            self.readError.emit(str(e))

    def startLoader(self):
        self.loader.start()

    def stopLoader(self):
        self.loader.stop()

    def fileSave(self):
        name = QFileDialog.getSaveFileName(self, 'Save File')
        shutil.copy(self.file, name[0])
