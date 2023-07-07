from .gui import GUIManager


def show_gui_popup(filename):
    GUIManager.run_until_close(filename)
