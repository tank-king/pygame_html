import pygame

from pygame_html.gui import GUIManager, GUIWindow
from pygame_html.config import Config
import sys
from pathlib import Path

sys.path.append(Path(__file__).absolute().__str__())


def set_default_html_folder_path(path):
    GUIWindow.configure_html_folder(path)


async def async_show_gui_popup(filename, size=None, offset=None, fps=60):
    await GUIManager.async_run_until_close(filename, size, offset, fps)


def show_gui_popup(filename, size=None, offset=None, fps=60):
    GUIManager.run_until_close(filename, size, offset, fps)


def set_debug(value: bool):
    Config.DEBUG = value


_gui_manager = GUIManager()


def update_and_draw(events: list[pygame.event.Event], surf: pygame.Surface, dt=1):
    _gui_manager.update(events, dt)
    _gui_manager.draw(surf)


def show_popup(file_name, size=None, offset=None):
    _gui_manager.load_popup(file_name, size, offset)


def is_showing_popup():
    return _gui_manager.window is not None


def close_popup():
    _gui_manager.close_popup()
