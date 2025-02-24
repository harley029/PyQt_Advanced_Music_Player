import os
import random

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap

from utils.message_manager import messanger


class BackgroundSlideshow:
    """
    A class that implements a background slideshow functionality for PyQt applications.

    This class handles displaying a sequence of background images from a specified directory,
    changing them automatically at defined intervals. It supports random image selection
    and filters out certain system files.
    """

    def __init__(self, label, images_dir, interval_ms=120000):
        """
        Initialize the BackgroundSlideshow with the specified parameters.

        Args:
            label: The PyQt label widget where images will be displayed.
            images_dir (str): The directory path containing the images for the slideshow.
            interval_ms (int, optional): The time interval between image changes in milliseconds.
                                         Defaults to 120000 (2 minutes).
        """
        self.label = label
        self.images_dir = images_dir
        self.slide_index = 0

        self.timer = QTimer()
        self.timer.setInterval(interval_ms)
        self.timer.timeout.connect(self.slideshow)

    def start(self):
        """
        Start the slideshow timer.

        This method activates the timer that controls the automatic changing of background images.
        """
        self.timer.start()

    def stop(self):
        """
        Stop the slideshow timer.

        This method deactivates the timer, preventing further automatic image changes.
        """
        self.timer.stop()

    def slideshow(self):
        """
        Update the background image according to the slideshow logic.

        This method is called automatically at intervals defined by the timer. It:
        1. Gets the list of image files from the specified directory
        2. Filters out specific files that should not be included in the slideshow
        3. Loads the current image and sets it as the background
        4. Selects the next image index (randomly or sequentially)

        If the images directory is empty after filtering, the method exits without changing the background.
        """
        try:
            # Проверка наличия каталога
            if not os.path.isdir(self.images_dir):
                raise FileNotFoundError(f"Directory '{self.images_dir}' does not exist.")
            images = os.listdir(self.images_dir)
            for unwanted in ["bg_overlay.png", ".DS_Store"]:
                if unwanted in images:
                    images.remove(unwanted)
            if not images:
                return
            current_file = images[self.slide_index]
            full_path = os.path.join(self.images_dir, current_file)
            if not os.path.isfile(full_path):
                raise FileNotFoundError(f"Image file '{full_path}' does not exist.")
            # Загрузка изображения и проверка корректности загрузки
            pixmap = QPixmap(full_path)
            if pixmap.isNull():
                raise ValueError(f"Unable to load image from '{full_path}'.")
            self.label.setPixmap(pixmap)
            if self.slide_index == len(images) - 1:
                self.slide_index = 0
            else:
                self.slide_index = random.randint(0, len(images) - 1)
        except FileNotFoundError as e:
            messanger.show_critical(
                self.label, "Slideshow Error", "Image file or directory not found.", e
            )
        except ValueError as e:
            messanger.show_critical(
                self.label, "Slideshow Error", "Failed to load image.", e
            )
        # except Exception as e:
        #     messanger.show_critical(
        #         self.label,
        #         "Slideshow Error",
        #         "Unexpected error during slideshow update.",
        #         e,
        #     )
