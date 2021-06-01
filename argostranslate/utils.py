from PyQt5.QtCore import *


class WorkerThread(QThread):
    """Runs a bound function on a thread"""

    def __init__(self, bound_worker_function):
        """Args:
        bound_worker_function (functools.partial)
        """
        super().__init__()
        self.bound_worker_function = bound_worker_function
        self.finished.connect(self.deleteLater)

    def run(self):
        self.bound_worker_function()
