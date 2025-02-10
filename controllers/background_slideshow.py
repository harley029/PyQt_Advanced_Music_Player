import os
import random

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap


class BackgroundSlideshow:

    def __init__(self, label, images_dir, interval_ms=120000):
        self.label = label
        self.images_dir = images_dir
        self.slide_index = 0

        # Собственный таймер, который будет вызывать slideshow()
        self.timer = QTimer()
        self.timer.setInterval(interval_ms)
        self.timer.timeout.connect(self.slideshow)

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def slideshow(self):
        # Получаем список файлов в папке с изображениями
        images = os.listdir(self.images_dir)

        # Удаляем лишние файлы (если есть)
        if "bg_overlay.png" in images:
            images.remove("bg_overlay.png")
        if ".DS_Store" in images:
            images.remove(".DS_Store")

        # Если список пустой или недостаточно файлов, можно проверить
        if not images:
            return

        # Берём текущую картинку
        current_file = images[self.slide_index]
        # Формируем полный путь
        full_path = os.path.join(self.images_dir, current_file)

        # Устанавливаем в label
        pixmap = QPixmap(full_path)
        self.label.setPixmap(pixmap)

        # Логика рандомного слайда:
        if self.slide_index == len(images) - 1:
            self.slide_index = 0
        else:
            self.slide_index = random.randint(0, len(images) - 1)
