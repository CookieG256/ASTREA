import platform
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

from PIL import Image, ImageDraw

from version import VERSION


ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
VERSION_OUTPUT = DIST / VERSION
VERSION_BUILD = ROOT / "build" / VERSION
BUILD_ASSETS = ROOT / "build_assets"
APP_NAME = "ASTREA"
ASSETS = ROOT / "assets"


def create_icons():
    BUILD_ASSETS.mkdir(exist_ok=True)
    image = Image.new("RGBA", (256, 256), (13, 16, 29, 255))
    draw = ImageDraw.Draw(image)
    draw.ellipse((22, 22, 234, 234), outline=(133, 112, 206, 255), width=8)
    draw.ellipse((57, 57, 199, 199), outline=(74, 89, 125, 255), width=4)
    draw.polygon(
        ((128, 48), (151, 105), (208, 128), (151, 151),
         (128, 208), (105, 151), (48, 128), (105, 105)),
        fill=(177, 135, 255, 255),
    )
    draw.ellipse((116, 116, 140, 140), fill=(245, 222, 255, 255))
    png_path = BUILD_ASSETS / "astrea.png"
    ico_path = BUILD_ASSETS / "astrea.ico"
    icns_path = BUILD_ASSETS / "astrea.icns"
    image.save(png_path)
    image.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    image.save(icns_path, format="ICNS")
    return png_path, ico_path, icns_path


def main():
    system = platform.system()
    if system not in ("Windows", "Darwin", "Linux"):
        raise SystemExit(f"Plataforma não suportada: {system}")

    png_icon, windows_icon, mac_icon = create_icons()
    icon = windows_icon if system == "Windows" else mac_icon if system == "Darwin" else png_icon
    command = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean", "--name", APP_NAME,
        "--icon", str(icon),
        "--distpath", str(VERSION_OUTPUT),
        "--workpath", str(VERSION_BUILD),
    ]
    if system == "Darwin":
        command.extend(("--windowed", "--onedir"))
    else:
        command.extend(("--windowed", "--onefile"))
    if ASSETS.is_dir():
        command.extend(("--add-data", f"{ASSETS}{os.pathsep}assets"))
    command.append(str(ROOT / "main.py"))
    subprocess.run(command, cwd=ROOT, check=True)

    DIST.mkdir(exist_ok=True)
    if system == "Darwin":
        app = VERSION_OUTPUT / f"{APP_NAME}.app"
        shutil.make_archive(
            str(DIST / f"ASTREA-{VERSION}-macOS"),
            "zip",
            root_dir=VERSION_OUTPUT,
            base_dir=app.name,
        )
    elif system == "Windows":
        executable = VERSION_OUTPUT / f"{APP_NAME}.exe"
        shutil.copy2(executable, DIST / f"ASTREA-{VERSION}-Windows.exe")
    else:
        executable = VERSION_OUTPUT / APP_NAME
        desktop_file = VERSION_OUTPUT / "ASTREA.desktop"
        desktop_file.write_text(
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=ASTREA\n"
            "Exec=./ASTREA\n"
            "Icon=ASTREA.png\n"
            "Terminal=false\n"
            "Categories=Game;\n",
            encoding="utf-8",
        )
        shutil.copy2(png_icon, VERSION_OUTPUT / "ASTREA.png")
        with tarfile.open(DIST / f"ASTREA-{VERSION}-Linux.tar.gz", "w:gz") as archive:
            for caminho in (executable, desktop_file, VERSION_OUTPUT / "ASTREA.png"):
                archive.add(caminho, arcname=caminho.name)

    print(f"Build finalizado para {system}: {DIST}")


if __name__ == "__main__":
    main()
