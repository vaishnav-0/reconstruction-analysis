# Setting the Qt bindings for QtPy
import os

from PyQt5.QtWidgets import QTabWidget

from grip import Grip

os.environ["QT_API"] = "pyqt5"

from qtpy.QtWidgets import QWidget, QVBoxLayout

from pyvistaqt import QtInteractor
import pyvista as pv


class Panel(QWidget):

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

        dummy = QWidget()
        self.tabWidget.setTabPosition(QTabWidget.South)
        self.tabWidget.addTab(dummy, "tab1")


class Mesh_Plotter(QWidget):
    def __init__(self, *args, **kwargs):
        super(Mesh_Plotter, self).__init__(*args, **kwargs)

        self.plotter = QtInteractor(self)

        self.file = None
        self.VLayout = QVBoxLayout()
        self.VLayout.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.VLayout)
        self.panel = Panel()

        # layout

        self.VLayout.addWidget(self.plotter.interactor)
        self.VLayout.addWidget(self.panel)
        self.VLayout.setStretch(0, 3)
        self.VLayout.setStretch(1, 1)

    def plot_file(self, file):
        self.file = file
        reader = pv.get_reader(file)
        mesh = reader.read()
        self.plotter.add_mesh(mesh, show_edges=True)
        _ = self.plotter.add_camera_orientation_widget()
        self.plotter.reset_camera()
