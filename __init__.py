from .gui import GUIManager, GUIWindow
import sys
from pathlib import Path

# sys.path.append(Path(__file__).absolute().__str__())


def set_default_html_folder_path(path):
    GUIWindow.configure_html_folder(path)


async def show_gui_popup(filename, size=None, offset=None, fps=60):
    await GUIManager.run_until_close(filename, size, offset, fps)
