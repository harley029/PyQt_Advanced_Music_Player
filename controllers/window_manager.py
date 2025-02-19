from PyQt5.QtCore import Qt


class WindowManager:
    """
    Manages custom window behavior for a frameless window.

    This class provides functionality for making a window draggable and customizing
    its appearance by removing the standard window frame and enabling transparency.
    """

    def __init__(self, window):
        """
        Initialize the WindowManager with a window instance.

        Parameters:
            window: The main window instance to be managed
        """
        self.window = window
        self.initialPosition = window.pos()

    def setup_window(self):
        """
        Configure window properties for custom appearance.

        Sets up the window to be frameless and have a translucent background.
        This allows for custom window styling and removes the default window decorations.
        """
        self.window.setAttribute(Qt.WA_TranslucentBackground)
        self.window.setWindowFlags(Qt.FramelessWindowHint)

    def handleMousePressEvent(self, event):
        """
        Handle mouse press events for window dragging.

        Records the initial position when the left mouse button is pressed,
        preparing for potential window movement.

        Parameters:
            event: Mouse press event containing position information
        """
        if event.button() == Qt.LeftButton:
            self.initialPosition = event.globalPos()

    def handleMouseMoveEvent(self, event):
        """
        Handle mouse move events for window dragging.

        Moves the window in response to mouse movement while the left button is held down.
        The window follows the mouse cursor, creating a dragging effect.

        Parameters:
            event: Mouse move event containing position information
        """
        if event.buttons() == Qt.LeftButton:
            self.window.move(
                self.window.pos() + event.globalPos() - self.initialPosition
            )
            self.initialPosition = event.globalPos()
            event.accept()
