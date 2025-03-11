import os
import sys
from unittest.mock import MagicMock, patch, Mock
import pytest

from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer

from controllers.background_slideshow import BackgroundSlideshow


# Фикстура для создания QApplication (если ещё не создан)
@pytest.fixture(scope="session", autouse=True)
def app():
    application = QApplication.instance()
    if application is None:
        application = QApplication(sys.argv)
    return application


class TestBackgroundSlideshow:
    @pytest.fixture
    def slideshow(self):
        """Fixture to create a BackgroundSlideshow instance with mocked dependencies."""
        # Создаем мок для метки, на которой отображается изображение
        mock_label = MagicMock(spec=QLabel)
        # Задаем кастомную директорию с изображениями (для теста используем фиктивный путь)
        images_dir = "/mock/path"
        # Интервал таймера задаем небольшой для тестирования
        instance = BackgroundSlideshow(
            mock_label, images_dir=images_dir, interval_ms=1000
        )
        return instance

    def test_init_default(self, slideshow):
        """Test initialization with default parameters."""
        # Проверяем, что конструктор корректно устанавливает поля
        assert slideshow.label is not None
        assert slideshow.images_dir == "/mock/path"
        assert slideshow.slide_index == 0
        assert isinstance(slideshow.timer, QTimer)
        assert slideshow.timer.interval() == 1000

    def test_start_timer(self, slideshow):
        """Test start method activates the timer."""
        with patch.object(slideshow.timer, "start") as mock_start:
            slideshow.start()
            mock_start.assert_called_once()

    def test_stop_timer(self, slideshow):
        """Test stop method deactivates the timer."""
        with patch.object(slideshow.timer, "stop") as mock_stop:
            slideshow.stop()
            mock_stop.assert_called_once()

    @patch("controllers.background_slideshow.os.path.isdir", return_value=False)
    @patch("controllers.background_slideshow.os.listdir")
    @patch("PyQt5.QtWidgets.QMessageBox.critical", return_value=None)
    def test_slideshow_invalid_dir(
        self, mock_msgbox_critical, mock_listdir, mock_isdir, slideshow
    ):
        """Test slideshow with invalid directory."""
        slideshow.slideshow()
        mock_listdir.assert_not_called()
        mock_msgbox_critical.assert_called_once()
        args, _ = mock_msgbox_critical.call_args
        assert args[0] == slideshow.label
        assert args[1] == "Slideshow Error"
        assert "does not exist" in args[2]

    @patch("controllers.background_slideshow.os.path.isdir", return_value=True)
    @patch("controllers.background_slideshow.os.listdir", return_value=[])
    @patch("PyQt5.QtWidgets.QMessageBox.critical", return_value=None)
    def test_slideshow_empty_dir(
        self, mock_msgbox_critical, mock_listdir, mock_isdir, slideshow
    ):
        """Test slideshow with empty directory after filtering."""
        slideshow.slideshow()
        mock_listdir.assert_called_once_with("/mock/path")
        mock_msgbox_critical.assert_not_called()
        slideshow.label.setPixmap.assert_not_called()

    @patch("controllers.background_slideshow.os.path.isdir", return_value=True)
    @patch(
        "controllers.background_slideshow.os.listdir",
        return_value=["bg_overlay.png", ".DS_Store"],
    )
    @patch("PyQt5.QtWidgets.QMessageBox.critical", return_value=None)
    def test_slideshow_filtered_empty(
        self, mock_msgbox_critical, mock_listdir, mock_isdir, slideshow
    ):
        """Test slideshow with only filtered files."""
        slideshow.slideshow()
        mock_listdir.assert_called_once_with("/mock/path")
        mock_msgbox_critical.assert_not_called()
        slideshow.label.setPixmap.assert_not_called()

    @patch("controllers.background_slideshow.os.path.isdir", return_value=True)
    @patch("controllers.background_slideshow.os.listdir", return_value=["image1.jpg"])
    @patch("controllers.background_slideshow.os.path.isfile", return_value=True)
    @patch("controllers.background_slideshow.QPixmap")
    @patch("PyQt5.QtWidgets.QMessageBox.critical", return_value=None)
    def test_slideshow_single_image(
        self,
        mock_msgbox_critical,
        mock_QPixmap,
        mock_isfile,
        mock_listdir,
        mock_isdir,
        slideshow,
    ):
        """Test slideshow with a single valid image."""
        mock_pixmap = Mock(spec=QPixmap)
        mock_pixmap.isNull.return_value = False
        mock_QPixmap.return_value = mock_pixmap

        with patch.object(slideshow.label, "setPixmap") as mock_set_pixmap:
            slideshow.slideshow()
            mock_listdir.assert_called_once_with("/mock/path")
            expected_path = os.path.join("/mock/path", "image1.jpg")
            mock_isfile.assert_called_once_with(expected_path)
            mock_QPixmap.assert_called_once_with(expected_path)
            mock_set_pixmap.assert_called_once_with(mock_pixmap)
            assert slideshow.slide_index == 0
            mock_msgbox_critical.assert_not_called()

    @patch("PyQt5.QtWidgets.QMessageBox.critical", return_value=None)
    @patch("controllers.background_slideshow.os.path.isdir", return_value=True)
    @patch(
        "controllers.background_slideshow.os.listdir",
        return_value=["image1.jpg", "image2.jpg"],
    )
    @patch("controllers.background_slideshow.os.path.isfile", return_value=True)
    @patch("controllers.background_slideshow.random.randint", return_value=1)
    @patch("controllers.background_slideshow.QPixmap")
    def test_slideshow_multiple_images(
        self,
        mock_QPixmap,
        mock_randint,
        mock_isfile,
        mock_listdir,
        mock_isdir,
        mock_msgbox_critical,
        slideshow,
    ):
        """Test slideshow with multiple valid images and random selection."""
        mock_pixmap = Mock(spec=QPixmap)
        mock_pixmap.isNull.return_value = False
        mock_QPixmap.return_value = mock_pixmap

        with patch.object(slideshow.label, "setPixmap") as mock_set_pixmap:
            slideshow.slideshow()
            mock_listdir.assert_called_once_with("/mock/path")
            expected_path = os.path.join("/mock/path", "image1.jpg")
            mock_isfile.assert_called_once_with(expected_path)
            mock_QPixmap.assert_called_once_with(expected_path)
            mock_set_pixmap.assert_called_once_with(mock_pixmap)
            mock_randint.assert_called_once_with(0, 1)
            assert slideshow.slide_index == 1
            mock_msgbox_critical.assert_not_called()

    @patch("controllers.background_slideshow.os.path.isdir", return_value=True)
    @patch("controllers.background_slideshow.os.listdir", return_value=["image1.jpg"])
    @patch("controllers.background_slideshow.os.path.isfile", return_value=False)
    @patch("PyQt5.QtWidgets.QMessageBox.critical", return_value=None)
    def test_slideshow_file_not_found(
        self, mock_msgbox_critical, mock_isfile, mock_listdir, mock_isdir, slideshow
    ):
        """Test slideshow when image file does not exist."""
        slideshow.slideshow()
        mock_msgbox_critical.assert_called_once()
        args, _ = mock_msgbox_critical.call_args
        assert args[0] == slideshow.label
        assert "does not exist" in args[2]

    @patch("controllers.background_slideshow.os.path.isdir", return_value=True)
    @patch("controllers.background_slideshow.os.listdir", return_value=["image1.jpg"])
    @patch("controllers.background_slideshow.os.path.isfile", return_value=True)
    @patch("controllers.background_slideshow.QPixmap")
    @patch("PyQt5.QtWidgets.QMessageBox.critical", return_value=None)
    def test_slideshow_invalid_image(
        self,
        mock_msgbox_critical,
        mock_QPixmap,
        mock_isfile,
        mock_listdir,
        mock_isdir,
        slideshow,
    ):
        """Test slideshow with an invalid image (null pixmap)."""
        mock_pixmap = Mock(spec=QPixmap)
        mock_pixmap.isNull.return_value = True
        mock_QPixmap.return_value = mock_pixmap

        slideshow.slideshow()
        mock_msgbox_critical.assert_called_once()
        args, _ = mock_msgbox_critical.call_args
        assert args[0] == slideshow.label
        assert "Failed to load image" in args[2]
        slideshow.label.setPixmap.assert_not_called()
