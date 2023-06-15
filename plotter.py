# Setting the Qt bindings for QtPy
import os
import shutil

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTabWidget, QFileDialog, QPushButton, QLabel, QSpacerItem, QTextEdit, QCheckBox, QHBoxLayout
from PyQt5 import QtCore

from globals import global_font
from grip import Grip
from loader import LoadingTranslucentScreen

os.environ["QT_API"] = "pyqt5"

from qtpy.QtWidgets import QWidget, QVBoxLayout

from pyvistaqt import QtInteractor
import pyvista as pv


class HelpPanel(QWidget):
    def __init__(self):
        super(HelpPanel, self).__init__()
        self.VLayout = QVBoxLayout()
        self.setLayout(self.VLayout)

        self.textEdit = QTextEdit()
        self.textEdit.setHtml("<div>"
                              "For a 3-button mouse, the left button is for rotation, the right button for zooming, "
                              "the middle button for panning, and ctrl + left button for spinning the view around the "
                              "vewing axis of the camera. Alternatively, ctrl + shift + left button or mouse wheel "
                              "zooms, and shift + left button pans."
                              "<div>")

        self.VLayout.addWidget(self.textEdit)


class PanelActions(QWidget):
    def __init__(self, *args, **kwargs):
        super(PanelActions, self).__init__(*args, **kwargs)
        self.VLayout = QVBoxLayout()
        self.setLayout(self.VLayout)
        self.VLayout.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)

        self.pushButton = QPushButton("save mesh")
        self.VLayout.addWidget(self.pushButton)

        # interactor toggle
        self.interactor_checkbox = QCheckBox("individual interaction")
        self.VLayout.addWidget(self.interactor_checkbox)

        # clipping
        self.clipping_HLayout = QHBoxLayout()
        self.VLayout.addLayout(self.clipping_HLayout)
        clipLabel = QLabel("clip: ")
        self.clipping_HLayout.addWidget(clipLabel)
        self.clip_btn = QPushButton("open clipping widget")
        self.clip_cancel_btn = QPushButton("cancel")
        self.clip_cancel_btn.setEnabled(False)
        self.clipping_HLayout.addWidget(self.clip_btn)
        self.clipping_HLayout.addWidget(self.clip_cancel_btn)







class PanelInfoTab(QWidget):
    def __init__(self, name, params):
        super(PanelInfoTab, self).__init__()

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.setLayout(self.verticalLayout)

        font = global_font

        self.label_name = QLabel(self)
        self.label_name.setFont(font)
        self.label_name.setText("Algorithm: " + name)
        self.verticalLayout.addWidget(self.label_name)

        for param, value in params.items():
            label = QLabel(self)
            label.setFont(font)
            label.setText(param + ": " + value)
            self.verticalLayout.addWidget(label)

        spacerItem = QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)


class Panel(QWidget):
    fileSave = pyqtSignal()
    interactorChange = pyqtSignal(bool)

    planeClipperOpen = pyqtSignal()
    planeClipperClose = pyqtSignal()
    planeClipperClip = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Panel, self).__init__(*args, **kwargs)

        self.VLayout = QVBoxLayout()
        self.setLayout(self.VLayout)
        self.VLayout.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)

        self.tabWidget = QTabWidget(self)
        self.tabWidget.setTabPosition(QTabWidget.South)
        self.grip = Grip(self, self)

        self.VLayout.addWidget(self.grip)
        self.VLayout.addWidget(self.tabWidget)

    def add_actions_tab(self):
        tab1 = PanelActions()
        tab1.pushButton.clicked.connect(self.fileSave)
        tab1.interactor_checkbox.stateChanged.connect(self.emitInteractorChange)
        self.tabWidget.addTab(tab1, "actions")



    def add_info(self, name, params):
        tab = PanelInfoTab(name, params)
        self.tabWidget.addTab(tab, "info")

    def add_help(self):
        tab = HelpPanel()
        self.tabWidget.addTab(tab, "help")

    def emitFileSave(self):
        self.fileSave.emit()

    def emitInteractorChange(self, state):
        if state == QtCore.Qt.Checked:
            self.interactorChange.emit(True)
        else:
            self.interactorChange.emit(False)


class Mesh_Plotter(QWidget):
    readError = pyqtSignal(str)

    def __init__(self):
        super(Mesh_Plotter, self).__init__()

        self.plotter = QtInteractor(self)

        self.file = None
        self.VLayout = QVBoxLayout()
        self.VLayout.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.VLayout)
        self.panel = Panel()

        # connect the signals
        self.panel.fileSave.connect(self.fileSave)
        self.panel.interactorChange.connect(self.toggle_individual_control)


        self.loader = LoadingTranslucentScreen(self, "loading")
        # layout

        self.VLayout.addWidget(self.plotter.interactor)
        self.VLayout.addWidget(self.panel)
        self.VLayout.setStretch(0, 3)
        self.VLayout.setStretch(1, 1)

    def add_info(self, name, params):
        self.panel.add_info(name, params)

    def add_actions(self):
        self.panel.add_actions_tab()

    def add_help(self):
        self.panel.add_help()

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

    def toggle_individual_control(self, state):
        if state:
            self.plotter.enable_trackball_actor_style()
        else:
            self.plotter.enable_trackball_style()

    def fileSave(self):
        name = QFileDialog.getSaveFileName(self, 'Save File')
        shutil.copy(self.file, name[0])
