from .gui import GUIManager


def show_gui_popup(filename, size=None, fps=60):
    GUIManager.run_until_close(filename, size, fps)
