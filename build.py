from cx_Freeze import setup, Executable
import sys
import os

build_exe_options = {
    "include_files": [
        ("utils", "utils"),
        ("icons/5.icns", "icons/5.icns"),
    ]
}

options = {
    "build_exe": build_exe_options,
    "bdist_mac": {
        "iconfile": "icons/5.icns"
    },
}

executables = [
    Executable(
        script="QtBeets.py",
        target_name="QtBeets.app",
        base=None,
        icon="icons/5.icns",
    )
]

setup(
    name="QtBeets",
    version="1.1",
    description="Advanced Music Player",
    options=options,
    executables=executables,
)
