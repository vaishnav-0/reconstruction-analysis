from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel


class Grip(QLabel):
    def __init__(self, parent, move_widget):
        super(Grip, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.move_widget = move_widget
        self.setText("≡")
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.min_height = 20

        self.mouse_start = None
        self.height_start = self.move_widget.height()
        self.resizing = False
        self.setMouseTracking(True)

        self.setCursor(QtCore.Qt.SizeVerCursor)

    def showEvent(self, event):
        super(Grip, self).showEvent(event)
        self.reposition()

    def mousePressEvent(self, event):
        super(Grip, self).mousePressEvent(event)
        self.resizing = True
        self.height_start = self.move_widget.height()
        self.mouse_start = event.globalPos()

    def mouseMoveEvent(self, event):
        super(Grip, self).mouseMoveEvent(event)
        if self.resizing:
            delta = event.globalPos() - self.mouse_start
            height = self.height_start - delta.y()
            if height > self.min_height:
                self.move_widget.setFixedHeight(height)
            else:
                self.move_widget.setFixedHeight(self.min_height)

            self.reposition()


    def mouseReleaseEvent(self, event):
        super(Grip, self).mouseReleaseEvent(event)
        self.resizing = False

    def reposition(self):
        pass
        # rect = self.move_widget.geometry()
        # self.move(rect.right(), rect.bottom())
