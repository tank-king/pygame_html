from .gui import GUIManager, GUIWindow


def set_default_html_folder_path(path):
    GUIWindow.configure_html_folder(path)


async def show_gui_popup(filename, size=None, offset=None, fps=60):
    await GUIManager.run_until_close(filename, size, offset, fps)
