import importlib
import os.path
from html.parser import HTMLParser

from pygame_html.container_definitions import *


class GUIWindow(BaseStructure, HTMLParser):
    def __init__(self, width, height):
        super().__init__()
        self.root: Container = Container(width=width, height=height)
        self.root.window = self
        self.root.label = 'root'
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        parent = self.stack[-1] if self.stack else self.root
        container = self.get_container_from_tag(tag, dict(attrs))
        container.label = tag
        self.stack.append(container)
        parent.add_child(container)

    def handle_endtag(self, tag: str):
        if self.stack:
            self.stack.pop()

    def handle_data(self, data: str):
        data = data.strip()
        if not data:
            return
        parent = self.stack[-1] if self.stack else self.root
        words = data.split(' ')
        for i in range(len(words)):
            if words[i]:
                words[i] += ' '
        words = [i if i else ' ' for i in words]
        for i in words:
            settings = parent.font_settings
            settings['text'] = i
            container = TextContainer(**settings)
            container.label = 'text_container'
            parent.add_child(container)

    @staticmethod
    def get_container_from_tag(tag, attrs):
        tag = tag.lower()
        lib = importlib.import_module('pygame_html.container_definitions')
        for i in dir(lib):
            if i.endswith('Container'):
                if i.rstrip('Container').lower() == tag:
                    return getattr(lib, i)(**attrs)
        if tag == 'br':
            return BRContainer()
        return Container(**attrs)

    def load_from_html(self, file):
        if not os.path.isfile(file):
            return
        self.root.children.clear()
        with open(file, 'r') as f:
            data = f.read().strip().replace('\n', '')
            # print(data)
        self.feed(data)
        # TODO temporary fix
        self.root.rearrange_layout()  # first time rearrangement to estimate size of all containers
        self.root.rearrange_layout()  # second time rearrangement to position and align all containers properly
        # self.root.rearrange_layout()
        # self.recursive_children(self.root)

    def recursive_children(self, container: Container, indent=0):
        print(' ' * indent, container)
        for i in container.children:
            self.recursive_children(i, indent + 10)

    def update(self, events: list[pygame.event.Event], dt=1.0):
        self.root.update(events, dt)
        # print(self.root.effective_rect)

    def draw(self, surf: pygame.Surface, offset=(0, 0)):
        self.root.draw(surf, offset)


class GUIManager(BaseStructure):
    def __init__(self, auto_resize=True):
        self.auto_resize = auto_resize
        self.window: Optional[GUIWindow] = None
        self.queued_windows = ['sample.html']
        self.current_window = ''
        self.minimized = False

    def queue_popup(self, file_name):
        self.queued_windows.append(file_name)

    def load_popup(self, file_name):
        self.window = GUIWindow(*pygame.display.get_surface().get_size())
        self.current_window = file_name
        self.window.load_from_html(file_name)

    def minimize(self):
        self.minimized = True

    def restore(self):
        self.minimized = False

    @staticmethod
    def set_font_config(**kwargs):
        for i, j in kwargs.items():
            if i in FontEngine.DEFAULTS:
                FontEngine.DEFAULTS[i] = j

    def close_popup(self):
        if self.window:
            self.window = None

    def update(self, events: list[pygame.event.Event], dt=1.0):
        if self.minimized:
            return
        for e in events:
            if e.type == pygame.WINDOWRESIZED:
                if self.auto_resize:
                    self.window = GUIWindow(e.x, e.y)
                    self.window.load_from_html(self.current_window)
        if self.window:
            self.window.update(events, dt)
        else:
            if self.queued_windows:
                self.window = GUIWindow(*pygame.display.get_surface().get_size())
                self.current_window = self.queued_windows.pop(0)
                self.window.load_from_html(self.current_window)

    def draw(self, surf: pygame.Surface, offset=(0, 0)):
        if self.minimized:
            return
        if self.window:
            self.window.draw(surf, offset)
            # pygame.draw.rect(pygame.display.get_surface(), 'red', self.window.root.rect, 10)
