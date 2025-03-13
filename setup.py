import sys
from cx_Freeze import setup, Executable

app_icon = "icons/5.icns"

include_files= [
    ("utils/bg_imgs", "utils/bg_imags"),
]

build_exe_options = {
    "packages": ["os", "PyQt5"],
    "include_files": include_files,
    "excludes": ["PyQt5.QtQml", "libpq.5.dylib"],
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="QtBeets",
    version="1.4",
    description="Advanced Music Player",
    options={"build_exe":build_exe_options},
    executables=[Executable("QtBeets.py", base=base)],
)
