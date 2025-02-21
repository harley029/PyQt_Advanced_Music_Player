from cx_Freeze import setup, Executable
app_icon = "icons/5.icns"

build_exe_options = {
    "include_files": [
        ("utils", "utils"),
        (app_icon, app_icon),
    ]
}

options = {
    "build_exe": build_exe_options,
    "bdist_mac": {"iconfile": app_icon},
}

executables = [
    Executable(
        script="QtBeets.py",
        target_name="QtBeets.app",
        base=None,
        icon=app_icon,
    )
]

setup(
    name="QtBeets",
    version="1.3",
    description="Advanced Music Player",
    options=options,
    executables=executables,
)
