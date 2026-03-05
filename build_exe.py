import PyInstaller.__main__
import os
import shutil

def build():
    # Ensure dist directory
    if not os.path.exists("dist"):
        os.makedirs("dist")

    # PyInstaller arguments
    params = [
        'src/main.py',
        '--onefile',
        '--windowed',
        '--name=PyTestConnection',
        '--icon=NONE', # You can add an .ico file here
        '--add-data=config;config',
        '--add-data=data;data',
        '--hidden-import=speedtest',
        '--hidden-import=pyspeedtest',
        '--hidden-import=psutil',
        '--distpath=dist',
        '--workpath=build',
        '--clean'
    ]

    print("Building executable...")
    PyInstaller.__main__.run(params)
    print("Build complete. Executable located in ./dist/PyTestConnection.exe")

if __name__ == "__main__":
    build()
