from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QLabel, QFileDialog
from qtpy.QtWidgets import QWidget, QVBoxLayout
from PyQt5 import QtCore



class ImportMeshWidget(QWidget):

    fileOpened = QtCore.pyqtSignal(str)

    def __init__(self):
        super(ImportMeshWidget, self).__init__()
        self.verticalLayout = QVBoxLayout()

        self.horizontalLayout_fileOpen = QHBoxLayout()
        self.pushButton = QPushButton(self)
        self.horizontalLayout_fileOpen.addWidget(self.pushButton)
        self.file_label = QLabel(self)
        self.file_label.setText("")
        self.pushButton.setText("open")

        self.horizontalLayout_fileOpen.addWidget(self.file_label)

        self.verticalLayout.addLayout(self.horizontalLayout_fileOpen)
        self.setLayout(self.verticalLayout)

        self.pushButton.clicked.connect(self.openFile)


    def openFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "select file", "", "All Files (*)",
                                                  options=options)
        self.file = fileName
        self.file_label.setText(fileName)

        self.fileOpened.emit(fileName)


