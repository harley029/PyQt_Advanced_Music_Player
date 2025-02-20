# marquee_label.py

from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QTimer, Qt


class MarqueeLabel(QLabel):
    def __init__(self, parent=None, speed=30, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.speed = speed  # Скорость прокрутки в миллисекундах
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.scroll_text)
        self.offset = 0
        self.display_text = self.text()
        self.setText("")
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.timer.start(self.speed)

    def setText(self, text):
        self.display_text = text
        self.offset = 0
        super().setText("")
        self.update()

    def scroll_text(self):
        font_metrics = self.fontMetrics()
        text_width = font_metrics.width(self.display_text)
        label_width = self.width()

        if text_width <= label_width:
            # Если текст помещается, не прокручиваем
            self.setText(self.display_text)
            self.timer.stop()
            return
        else:
            # Прокрутка текста
            self.offset += 1
            if self.offset > text_width:
                self.offset = 0
            # Создаём видимую часть текста
            visible_text = (
                self.display_text + "    " + self.display_text
            )  # Пробелы для плавности
            avg_char_width = font_metrics.averageCharWidth()
            num_chars = label_width // avg_char_width
            display = visible_text[self.offset: self.offset + num_chars]
            self.setText(display)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Перезапуск таймера при изменении размера
        self.timer.start(self.speed)
