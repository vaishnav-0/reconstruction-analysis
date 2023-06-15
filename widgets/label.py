from PyQt5.QtWidgets import QLabel


class CustomLabel(QLabel):
    def __init__(self, *args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)
        self._data = None

    def data(self):
        return self._data

    def setData(self, data):
        self._data = data
