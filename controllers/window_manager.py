from PyQt5.QtCore import Qt


class WindowManager:
    def __init__(self, window):
        self.window = window
        self.initialPosition = window.pos()

    def setup_window(self):
        self.window.setAttribute(Qt.WA_TranslucentBackground)
        self.window.setWindowFlags(Qt.FramelessWindowHint)

    def handleMousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.initialPosition = event.globalPos()

    def handleMouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.window.move(self.window.pos() + event.globalPos() - self.initialPosition)
            self.initialPosition = event.globalPos()
            event.accept()
