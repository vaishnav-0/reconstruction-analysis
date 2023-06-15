import glob
import os
import sys

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, QFormLayout, QLineEdit, QGroupBox
)
from qtpy import QtWidgets

from algo import algos
from widgets.collapsable import CollapsibleBox
from widgets.detachable_tab import DetachableTabWidget
from globals import global_font
from widgets.import_mesh import ImportMeshWidget
from widgets.label import CustomLabel
from main_window import Ui_MainWindow
from widgets.plotter import Mesh_Plotter
from thread import ThreadFn
from utils import get_filename



class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # set up temporary folder for storing generated mesh files
        self.tempFolder = "./temp"
        self.initTempFolder()

        # selected point cloud file
        self.file = None

        self.workerThreads = []
        self.setupUi(self)

        # mesh area(right side)
        self.centralTabs = DetachableTabWidget()
        self.verticalLayout_meshView.addWidget(self.centralTabs)

        # left side panel
        self.initAlgoTree()

    """
    Create collapsable elements in the left panel according to the data in the algo module
    """

    def initAlgoTree(self):

        # For importing mesh files directly
        box = CollapsibleBox("Open mesh")
        lay = QtWidgets.QVBoxLayout()
        importMeshWid = ImportMeshWidget()

        importMeshWid.fileOpened.connect(lambda x: self.createMeshTab("mesh" + "_" + get_filename(x), "None", {})[0](x))

        lay.addWidget(importMeshWid)
        box.setContentLayout(lay)

        self.algoTree.addWidget(box)

        # drop down for each algorithm
        for algo in algos:
            box = CollapsibleBox(algo["name"])
            lay = QtWidgets.QVBoxLayout()

            def rec_fn_wrapper(x, _algo=algo):
                self.regenerate(_algo, x)

            lay.addWidget(self.createAlgoForm(algo["parameters"], rec_fn_wrapper))

            box.setContentLayout(lay)
            self.algoTree.addWidget(box)

    # generates form of each algorithm
    def createAlgoForm(self, parameters, recFn):
        formGroupBox = QGroupBox()
        formLayout = QFormLayout()

        vLayout = QtWidgets.QVBoxLayout()

        for param, opts in parameters.items():
            label = CustomLabel(param if opts.get("label") is None else opts["label"])
            label.setData(param)
            formLayout.addRow(label, QLineEdit(opts["default"]))

        generateBtn = QtWidgets.QPushButton("reconstruct")

        generateBtn.clicked.connect(lambda: recFn(self.getFormData(formLayout)))

        vLayout.addItem(formLayout)
        vLayout.addWidget(generateBtn)

        formGroupBox.setLayout(vLayout)
        return formGroupBox

    def addTab(self, widget, label):
        self.centralTabs.addTab(widget, label)

    # extract data from a form of an algorithm
    def getFormData(self, form):
        data = {}
        label = ""
        for i in range(form.rowCount() * 2):
            item = form.itemAt(i).widget()
            if i % 2 == 0:
                label = item.data()
            else:
                if isinstance(item, QLineEdit):
                    data[label] = item.text()
        return data

    # display error message in a dialog
    def show_error(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        # div added for rich text formatting
        msg.setInformativeText("<div>" + message + "</div>")
        msg.setWindowTitle("Error")
        msg.exec_()

    # open dialog to open a file
    def openFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "select file", "", "All Files (*)",
                                                  options=options)
        self.file = fileName
        self.file_label.setText(fileName)

        return fileName

    # create mesh and open a tab to view it
    def regenerate(self, algo, params):

        recfn = algo["fn"]
        tab_title = algo["name"] + "_" + get_filename(self.file)

        if self.file is None:
            self.show_error("no input file")
        else:
            plotFn, plotter = self.createMeshTab(tab_title, algo["name"], params)

            thread = ThreadFn(lambda: recfn(input=self.file, output=self.tempFolder, **params),
                              finished=[plotFn, lambda: self.workerThreads.remove(thread)],
                              failed=[
                                  self.show_error,
                                  lambda: self.centralTabs.removeTab(self.centralTabs.indexOf(plotter))
                              ])
            self.workerThreads.append(thread)
            thread.start()

    def createMeshTab(self, tabTitle, algoName, params):
        """
        opens a mesh tab and initialize a loader
        :return:
            - function - function(str) to plot the mesh
            - plotter added to the tab
        """
        plotter = Mesh_Plotter()
        plotter.startLoader()
        plotter.add_info(algoName, params)
        plotter.add_actions()
        plotter.add_help()
        plotter.readError.connect(self.show_error)
        self.addTab(plotter, tabTitle)
        return self.plotFileWrap(plotter), plotter

    def plotFileWrap(self, plotter):
        def wrapped(file):
            plotter.stopLoader()
            plotter.plotFile(file)

        return wrapped

    # creates or initialize temporary folder
    def initTempFolder(self):
        if os.path.exists(self.tempFolder):
            files = glob.glob(self.tempFolder + "/*")
            for f in files:
                os.remove(f)
        else:
            os.mkdir(self.tempFolder)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(global_font)
    win = Window()
    win.show()
    sys.exit(app.exec())
