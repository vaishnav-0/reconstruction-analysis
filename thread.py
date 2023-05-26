from PyQt5.QtCore import QObject, pyqtSignal, QThread


class Worker(QObject):
    finished = pyqtSignal(str)
    # progress = pyqtSignal(int)

    def __init__(self, fn):
        super().__init__()
        self.fn = fn


    def run(self):
        self.finished.emit(self.fn())


class ThreadFn(QThread):
    def __init__(self, fn, started=[], finished=[]):
        super().__init__()
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker(fn)
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)

        # Step 5: Connect signals and slots
        for fn in started:
            self.thread.started.connect(fn)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        for fn in finished:
            self.worker.finished.connect(fn)

        self.thread.started.connect(self.worker.run)


    def start(self):
        self.thread.start()



