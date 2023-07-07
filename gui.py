import importlib
import os.path
from html.parser import HTMLParser
from pathlib import Path

import pygame.event

from pygame_html.container_definitions import *


class GUIWindow(BaseStructure, HTMLParser):
    def __init__(self, width, height):
        super().__init__()
        self.root: Container = Container(width=width, height=height)
        self.root.window = self
        self.root.label = 'root'
        self.stack = [self.root]
        self.ignore_stack = []
        self.base_path = ''

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        parent = self.stack[-1] if self.stack else self.root
        exists = False
        lib = importlib.import_module('pygame_html.container_definitions')
        for i in dir(lib):
            if i.endswith('Container'):
                if i[:-len('Container')].lower() == tag:
                    exists = True
        if tag == 'container':
            exists = True
        if not exists or self.ignore_stack:
            self.ignore_stack.append(tag)
            return
        container = self.get_container_from_tag(tag, dict(attrs))
        container.label = tag
        self.stack.append(container)
        parent.add_child(container)

    def handle_endtag(self, tag: str):
        tag = tag.lower()
        if self.ignore_stack:
            self.ignore_stack.pop()
            return
        if self.stack:
            self.stack.pop()

    def handle_data(self, data: str):
        data = data.strip()
        if not data:
            return
        if self.ignore_stack:
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

    def get_container_from_tag(self, tag, attrs):
        tag = tag.lower()
        lib = importlib.import_module('pygame_html.container_definitions')
        if tag == 'img' and attrs.get('src'):
            attrs['src'] = os.path.join(self.base_path, attrs['src'])
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
        self.base_path = Path(file).parent.absolute()
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

    @staticmethod
    def run_until_close(file_name):
        manager = GUIManager()
        manager.load_popup(file_name)
        surf = pygame.display.get_surface()
        clock = pygame.time.Clock()
        while True:
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        quit()
            surf.fill(0)
            manager.update(events)
            manager.draw(surf)
            pygame.display.update()
            clock.tick(60)

    def queue_popup(self, file_name):
        self.queued_windows.append(file_name)

    def load_popup(self, file_name):
        self.queued_windows.clear()
        self.current_window = ''
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
            self.queued_windows.clear()

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
        # else:
        #     if self.queued_windows:
        #         self.window = GUIWindow(*pygame.display.get_surface().get_size())
        #         self.current_window = self.queued_windows.pop(0)
        #         self.window.load_from_html(self.current_window)

    def draw(self, surf: pygame.Surface, offset=(0, 0)):
        if self.minimized:
            return
        if self.window:
            self.window.draw(surf, offset)
            # pygame.draw.rect(pygame.display.get_surface(), 'red', self.window.root.rect, 10)
