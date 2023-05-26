import glob
import os
import sys

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, QFormLayout, QLabel, QLineEdit, QGroupBox
)
from qtpy import QtWidgets

from algo import algos
from collapsable import CollapsibleBox
from detachable_tab import DetachableTabWidget
from import_mesh import ImportMeshWidget
from main_window import Ui_MainWindow
from plotter import Mesh_Plotter
from thread import ThreadFn


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tempFolder = "./temp"
        self.setupUi(self)
        self.initTempFolder()
        self.tabs = []
        self.file = None
        self.workerThreads = []

        # mesh area
        self.centralTabs = DetachableTabWidget()
        self.verticalLayout_meshView.addWidget(self.centralTabs)

        self.initAlgoTree()

    """
    Create collapsable elements in the left panel according to the data in the algo module
    """

    def initAlgoTree(self):

        # For importing mesh files directly
        box = CollapsibleBox("Open mesh")
        lay = QtWidgets.QVBoxLayout()
        importMeshWid = ImportMeshWidget()
        importMeshWid.fileOpened.connect(lambda x: self.plotFile(x))

        lay.addWidget(importMeshWid)
        box.setContentLayout(lay)

        self.algoTree.addWidget(box)

        #For algorithms
        for algo in algos:
            box = CollapsibleBox(algo["name"])
            lay = QtWidgets.QVBoxLayout()
            lay.addWidget(self.createAlgoForm(algo["parameters"], algo["fn"]))

            box.setContentLayout(lay)
            self.algoTree.addWidget(box)

    def createAlgoForm(self, parameters, recFn):
        formGroupBox = QGroupBox()
        formLayout = QFormLayout()

        vLayout = QtWidgets.QVBoxLayout()

        for param in parameters:
            formLayout.addRow(QLabel(param), QLineEdit())

        generateBtn = QtWidgets.QPushButton("reconstruct")

        # loader = WaitingSpinner(
        #     formGroupBox,
        #     roundness=98.0,
        #     fade=79.0,
        #     radius=10,
        #     lines=17,
        #     line_length=10,
        #     line_width=2,
        #     speed=0.7,
        #     color=QColor(0, 0, 0)
        # )

        generateBtn.clicked.connect(lambda: self.regenerate(recFn, self.getFormData(formLayout)))

        vLayout.addItem(formLayout)
        vLayout.addWidget(generateBtn)
        # vLayout.addWidget(loader)

        formGroupBox.setLayout(vLayout)
        return formGroupBox

    def addTab(self, widget, label):
        # self.tabs.append(widget)
        self.centralTabs.addTab(widget, label)

    def getFormData(self, form):
        data = {}
        label = ""
        for i in range(form.rowCount() * 2):
            item = form.itemAt(i).widget()
            if i % 2 == 0:
                label = item.text()
            else:
                if isinstance(item, QLineEdit):
                    data[label] = item.text()
        return data

    def show_error(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(message)
        msg.setWindowTitle("Error")
        msg.exec_()

    def openFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "select file", "", "All Files (*)",
                                                  options=options)
        self.file = fileName
        self.file_label.setText(fileName)

        return fileName

    def regenerate(self, recfn, params):
        if self.file is None:
            self.show_error("no input file")
        else:

            thread = ThreadFn(lambda: recfn(input=self.file, output=self.tempFolder, **params),
                              finished=[self.plotFile, lambda: self.workerThreads.remove(thread)])
            self.workerThreads.append(thread)
            thread.start()

    def plotFile(self, fileName):
        if fileName:
            try:
                plotter = Mesh_Plotter()
                self.addTab(plotter, "mesh1")

                plotter.plot_file(fileName)
            except ValueError:
                self.show_error("unsupported file type")

    def initTempFolder(self):
        if os.path.exists(self.tempFolder):
            files = glob.glob(self.tempFolder + "/*")
            for f in files:
                os.remove(f)
        else:
            os.mkdir(self.tempFolder)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
