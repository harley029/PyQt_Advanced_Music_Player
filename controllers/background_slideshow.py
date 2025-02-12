import os
import random

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap


class BackgroundSlideshow:

    def __init__(self, label, images_dir, interval_ms=120000):
        self.label = label
        self.images_dir = images_dir
        self.slide_index = 0

        self.timer = QTimer()
        self.timer.setInterval(interval_ms)
        self.timer.timeout.connect(self.slideshow)

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def slideshow(self):
        images = os.listdir(self.images_dir)
        if "bg_overlay.png" in images:
            images.remove("bg_overlay.png")
        if ".DS_Store" in images:
            images.remove(".DS_Store")
        if not images:
            return
        current_file = images[self.slide_index]
        full_path = os.path.join(self.images_dir, current_file)
        pixmap = QPixmap(full_path)
        self.label.setPixmap(pixmap)
        if self.slide_index == len(images) - 1:
            self.slide_index = 0
        else:
            self.slide_index = random.randint(0, len(images) - 1)
