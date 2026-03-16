import PyInstaller.__main__
import os
import shutil
import re

def generate_version_info(version):
    # Converte '1.0.5' para (1, 0, 5, 0)
    ver_parts = version.split('.')
    while len(ver_parts) < 4:
        ver_parts.append('0')
    ver_tuple = tuple(int(x) for x in ver_parts[:4])
    
    content = f"""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={ver_tuple},
    prodvers={ver_tuple},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        '040904b0',
        [StringStruct('CompanyName', 'Felix Neto'),
        StringStruct('FileDescription', 'PyTestConnection - Avaliador de Qualidade de Internet'),
        StringStruct('FileVersion', '{version}'),
        StringStruct('InternalName', 'PyTestConnection'),
        StringStruct('LegalCopyright', 'Copyright (c) 2026 Felix Neto'),
        StringStruct('OriginalFilename', 'PyTestConnection.exe'),
        StringStruct('ProductName', 'PyTestConnection'),
        StringStruct('ProductVersion', '{version}')])
      ]), 
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""
    with open("version_info.txt", "w", encoding="utf-8") as f:
        f.write(content.strip())

def build():
    # Ensure dist directory
    if not os.path.exists("dist"):
        os.makedirs("dist")

    # Read and increment VERSION in src/constants.py
    constants_path = os.path.join("src", "constants.py")
    version = "1.0.0"
    if os.path.exists(constants_path):
        with open(constants_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        match = re.search(r'VERSION\s*=\s*"(\d+)\.(\d+)\.(\d+)"', content)
        if match:
            major, minor, patch = match.groups()
            new_patch = int(patch) + 1
            version = f"{major}.{minor}.{new_patch}"
            
            new_content = re.sub(
                r'VERSION\s*=\s*"[^"]+"', 
                f'VERSION = "{version}"', 
                content
            )
            with open(constants_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Versão incrementada no constants.py para: {version}")
        else:
            match = re.search(r'VERSION\s*=\s*"([^"]+)"', content)
            if match:
                version = match.group(1)

    # Generate version info file for Windows executable Details
    generate_version_info(version)

    # Process README_EXE.md and generate a copy in dist
    readme_src = "README_EXE.md"
    readme_dest = os.path.join("dist", "README_EXE.md")
    if os.path.exists(readme_src):
        with open(readme_src, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Replace version in the first line
        if lines:
            if "{{VERSION}}" in lines[0]:
                lines[0] = lines[0].replace("{{VERSION}}", version)
            else:
                lines[0] = f"# PyTestConnection - Avaliador de Qualidade de Internet v{version}\n"
        
        with open(readme_dest, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"Generated {readme_dest} with version {version}.")

    # PyInstaller arguments
    params = [
        'src/main.py',
        '--onefile',
        '--windowed',
        '--name=PyTestConnection',
        '--icon=src/assets/app_icon.ico',
        '--version-file=version_info.txt',
        '--add-data=config;config',
        '--add-data=data;data',
        '--add-data=src/assets;src/assets',
        '--hidden-import=speedtest',
        '--hidden-import=pyspeedtest',
        '--hidden-import=psutil',
        '--paths=.',  # Garante que o diretório raiz seja base para imports do tipo 'from src...'
        '--distpath=dist',
        '--workpath=build',
        '--clean'
    ]

    print("Building executable...")
    PyInstaller.__main__.run(params)
    
    # Cleanup temporary version file
    if os.path.exists("version_info.txt"):
        os.remove("version_info.txt")

    print(f"Build complete. Executable located in ./dist/PyTestConnection.exe with version {version}")

if __name__ == "__main__":
    build()
