import os
import sys
from unittest.mock import MagicMock, patch, Mock
import pytest

from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer

from controllers.background_slideshow import BackgroundSlideshow


@pytest.fixture(scope="session", autouse=True)
def app():
    """
    Create and return a QApplication instance for the test session.

    This fixture is automatically used for all tests in the session and ensures
    a QApplication instance exists, which is required for QtWidgets components.
    If an instance already exists, it returns that instance instead of creating a new one.

    Returns:
        QApplication: The application instance to be used by all tests.
    """
    application = QApplication.instance()
    if application is None:
        application = QApplication(sys.argv)
    return application


class TestBackgroundSlideshow:
    @pytest.fixture
    def slideshow(self):
        """
        Create a BackgroundSlideshow instance with mocked dependencies for testing.

        This fixture sets up a BackgroundSlideshow object with controlled test
        dependencies including a mock QLabel and predefined parameters.

        Returns:
            BackgroundSlideshow: An instance of the BackgroundSlideshow class with
                                mocked components ready for testing.
        """
        mock_label = MagicMock(spec=QLabel)
        images_dir = "/mock/path"
        instance = BackgroundSlideshow(
            mock_label, images_dir=images_dir, interval_ms=1000
        )
        return instance

    def test_init_default(self, slideshow):
        """
        Test that the BackgroundSlideshow initializes with the correct default parameters.

        Verifies that:
        - The label attribute is properly set
        - The images_dir is correctly assigned
        - The slide_index starts at 0
        - A QTimer is created with the correct interval

        Args:
            slideshow (BackgroundSlideshow): The fixture providing the instance to test.
        """
        assert slideshow.label is not None
        assert slideshow.images_dir == "/mock/path"
        assert slideshow.slide_index == 0
        assert isinstance(slideshow.timer, QTimer)
        assert slideshow.timer.interval() == 1000

    def test_start_timer(self, slideshow):
        """
        Test that the start method activates the timer correctly.

        Verifies that calling the start method triggers the timer's start method.

        Args:
            slideshow (BackgroundSlideshow): The fixture providing the instance to test.
        """
        with patch.object(slideshow.timer, "start") as mock_start:
            slideshow.start()
            mock_start.assert_called_once()

    def test_stop_timer(self, slideshow):
        """
        Test that the stop method deactivates the timer correctly.

        Verifies that calling the stop method triggers the timer's stop method.

        Args:
            slideshow (BackgroundSlideshow): The fixture providing the instance to test.
        """
        with patch.object(slideshow.timer, "stop") as mock_stop:
            slideshow.stop()
            mock_stop.assert_called_once()

    @patch("controllers.background_slideshow.os.path.isdir", return_value=False)
    @patch("controllers.background_slideshow.os.listdir")
    @patch("PyQt5.QtWidgets.QMessageBox.critical", return_value=None)
    def test_slideshow_invalid_dir(
        self, mock_msgbox_critical, mock_listdir, mock_isdir, slideshow
    ):
        """
        Test slideshow behavior when given an invalid directory path.

        Verifies that:
        - The function checks if the directory exists
        - It doesn't attempt to list directory contents when the path is invalid
        - A critical error message is shown to the user with appropriate text

        Args:
            mock_msgbox_critical (MagicMock): Mock for QMessageBox.critical
            mock_listdir (MagicMock): Mock for os.listdir
            mock_isdir (MagicMock): Mock for os.path.isdir that returns False
            slideshow (BackgroundSlideshow): The fixture providing the instance to test.
        """
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
        """
        Test slideshow behavior when the directory exists but is empty.

        Verifies that:
        - The function attempts to list directory contents
        - No error message is shown for an empty directory
        - No image is set in the label when no images are found

        Args:
            mock_msgbox_critical (MagicMock): Mock for QMessageBox.critical
            mock_listdir (MagicMock): Mock for os.listdir returning an empty list
            mock_isdir (MagicMock): Mock for os.path.isdir that returns True
            slideshow (BackgroundSlideshow): The fixture providing the instance to test.
        """
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
        """
        Test slideshow behavior when directory contains only files that should be filtered out.

        Verifies that:
        - The function attempts to list directory contents
        - No error message is shown when there are only filtered files
        - No image is set in the label when all files are filtered

        Args:
            mock_msgbox_critical (MagicMock): Mock for QMessageBox.critical
            mock_listdir (MagicMock): Mock for os.listdir returning only filtered files
            mock_isdir (MagicMock): Mock for os.path.isdir that returns True
            slideshow (BackgroundSlideshow): The fixture providing the instance to test.
        """
        slideshow.slideshow()
        mock_listdir.assert_called_once_with("/mock/path")
        mock_msgbox_critical.assert_not_called()
        slideshow.label.setPixmap.assert_not_called()

    # pylint: disable=too-many-arguments,too-many-positional-arguments
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
        """
        Test slideshow behavior when directory contains a single valid image.

        Verifies that:
        - The function properly lists directory contents
        - It checks if the image file exists
        - It creates a QPixmap with the correct path
        - The QPixmap is set on the label
        - The slide index is correctly set
        - No error messages are shown for valid images

        Args:
            mock_msgbox_critical (MagicMock): Mock for QMessageBox.critical
            mock_QPixmap (MagicMock): Mock for QPixmap constructor
            mock_isfile (MagicMock): Mock for os.path.isfile that returns True
            mock_listdir (MagicMock): Mock for os.listdir returning a single image
            mock_isdir (MagicMock): Mock for os.path.isdir that returns True
            slideshow (BackgroundSlideshow): The fixture providing the instance to test.
        """
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

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    @patch("PyQt5.QtWidgets.QMessageBox.critical", return_value=None)
    @patch("controllers.background_slideshow.os.path.isdir", return_value=True)
    @patch("controllers.background_slideshow.os.listdir", return_value=["image1.jpg", "image2.jpg"])
    @patch("controllers.background_slideshow.os.path.isfile", return_value=True)
    @patch("controllers.background_slideshow.secrets.randbelow", return_value=1)
    @patch("controllers.background_slideshow.QPixmap")
    def test_slideshow_multiple_images(
        self,
        mock_QPixmap,
        mock_randbelow,
        mock_isfile,
        mock_listdir,
        mock_isdir,
        mock_msgbox_critical,
        slideshow,
    ):
        """
        Test slideshow behavior when directory contains multiple valid images with random selection.

        Verifies that:
        - The function properly lists directory contents
        - It uses secure random selection (secrets.randbelow) to choose the next image
        - It checks if the selected image file exists
        - It creates a QPixmap with the correct path
        - The QPixmap is set on the label
        - The slide index is correctly updated to match the random selection
        - No error messages are shown for valid images
        """
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
            mock_randbelow.assert_called_once_with(2)
            assert slideshow.slide_index == 1
            mock_msgbox_critical.assert_not_called()


    # pylint: disable=too-many-arguments,too-many-positional-arguments
    @patch("controllers.background_slideshow.os.path.isdir", return_value=True)
    @patch("controllers.background_slideshow.os.listdir", return_value=["image1.jpg"])
    @patch("controllers.background_slideshow.os.path.isfile", return_value=False)
    @patch("PyQt5.QtWidgets.QMessageBox.critical", return_value=None)
    def test_slideshow_file_not_found(
        self, mock_msgbox_critical, mock_isfile, mock_listdir, mock_isdir, slideshow
    ):
        """
        Test slideshow behavior when an image file listed in the directory does not actually exist.

        Verifies that:
        - The function properly lists directory contents
        - It checks if the image file exists
        - A critical error message is shown when the file doesn't exist
        - The error message contains appropriate text

        Args:
            mock_msgbox_critical (MagicMock): Mock for QMessageBox.critical
            mock_isfile (MagicMock): Mock for os.path.isfile that returns False
            mock_listdir (MagicMock): Mock for os.listdir returning a single image
            mock_isdir (MagicMock): Mock for os.path.isdir that returns True
            slideshow (BackgroundSlideshow): The fixture providing the instance to test.
        """
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
        """
        Test slideshow behavior when an image file exists but cannot be loaded as a valid image.

        Verifies that:
        - The function properly lists directory contents
        - It checks if the image file exists
        - It attempts to create a QPixmap from the file
        - It checks if the QPixmap is valid (not null)
        - A critical error message is shown when the QPixmap is null
        - The error message contains appropriate text
        - No attempt is made to set an invalid pixmap on the label

        Args:
            mock_msgbox_critical (MagicMock): Mock for QMessageBox.critical
            mock_QPixmap (MagicMock): Mock for QPixmap constructor
            mock_isfile (MagicMock): Mock for os.path.isfile that returns True
            mock_listdir (MagicMock): Mock for os.listdir returning a single image
            mock_isdir (MagicMock): Mock for os.path.isdir that returns True
            slideshow (BackgroundSlideshow): The fixture providing the instance to test.
        """
        mock_pixmap = Mock(spec=QPixmap)
        mock_pixmap.isNull.return_value = True
        mock_QPixmap.return_value = mock_pixmap

        slideshow.slideshow()
        mock_msgbox_critical.assert_called_once()
        args, _ = mock_msgbox_critical.call_args
        assert args[0] == slideshow.label
        assert "Failed to load image" in args[2]
        slideshow.label.setPixmap.assert_not_called()
