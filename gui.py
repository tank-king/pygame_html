import importlib
import os.path
import re
from pathlib import Path

import pygame.event

from html.parser import HTMLParser
from pygame_html.container_definitions import *


class GUIWindow(BaseStructure, HTMLParser):
    def __init__(self, width, height, offset=None):
        super().__init__()
        self.root: Container = Container(width=width, height=height)
        self.root.window = self
        self.root.label = 'root'
        self.window_offset = offset
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
            debug_print(tag, self.ignore_stack)
            return
        # debug_print(self.stack)
        container = self.get_container_from_tag(tag, dict(attrs))
        container.label = tag
        if tag in ['p', *['h' + str(i + 1) for i in range(6)]]:
            self.handle_startendtag('br', [])
        self_closing_tags = ['img', 'hr', 'br']
        if tag not in self_closing_tags:
            self.stack.append(container)
        parent.add_child(container)
        # if tag in self_closing_tags:
        #     self.handle_endtag(tag)

    def handle_endtag(self, tag: str):
        tag = tag.lower()
        if self.ignore_stack:
            self.ignore_stack.pop()
            return
        if self.stack:
            self.stack.pop()
        if tag in ['p', *['h' + str(i + 1) for i in range(6)]]:
            self.handle_startendtag('br', [])

    def handle_data(self, data: str):
        if self.stack and self.stack[-1].label == 'pre':
            lines = data.split('\n')
            if lines and not lines[-1]:
                lines.pop()
            parent = self.stack[-1] if self.stack else self.root
            for i in lines:
                settings = parent.font_settings
                settings['text'] = i
                container = TextContainer(**settings)
                container.label = 'text_container'
                parent.add_child(container)
                parent.add_child(BRContainer())
            return
        data = data.strip()
        data = data.replace('\n', ' ')
        data = re.sub('[ ]+', ' ', data)
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
                # debug_print(i[:-len('Container')].lower())
                if i[:-len('Container')].lower() == tag:
                    return getattr(lib, i)(**attrs)
        debug_print(tag)
        return Container(**attrs)

    def offset_root_window(self):
        self.root.set_pos((0, 0))
        if self.window_offset is None:
            return
        if type(self.window_offset) == str:
            rect = pygame.Rect(*self.root.pos, self.root.width, self.root.height)
            display_rect = pygame.display.get_surface().get_rect()
            try:
                rect.__setattr__(self.window_offset, display_rect.__getattribute__(self.window_offset))
                self.root.move(rect.topleft)
            except pygame.error:
                pass

    def load_from_html(self, file):
        path = Path(self.base_path) / file
        if not os.path.isfile(path):
            return
        self.base_path = path.parent
        self.root.children.clear()
        with open(path, 'r', encoding='utf-8') as f:
            data = f.read().strip().replace('\n', '\n')
            debug_print(data)

            # data = re.sub('<[ ]*br[ ]*>', '<br/>', data)
            # data = re.sub('<[ ]*hr[ ]*>', '<br/>', data)
            # debug_print(data)
        self.feed(data)
        # TODO temporary fix
        self.root.rearrange_layout()  # first time rearrangement to estimate size of all containers
        self.root.rearrange_layout()  # second time rearrangement to position and align all containers properly
        self.offset_root_window()

    def recursive_children(self, container: Container, indent=0):
        debug_print(' ' * indent, container)
        for i in container.children:
            self.recursive_children(i, indent + 10)

    def update(self, events: list[pygame.event.Event], dt=1.0):
        self.root.update(events, dt)
        # debug_print(self.root.effective_rect)

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
    def run_until_close(file_name, size=None, offset=None, fps=60):
        manager = GUIManager()
        manager.load_popup(file_name, size, offset)
        surf = pygame.display.get_surface()
        clock = pygame.time.Clock()
        while True:
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    return
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        return
            surf.fill('white')
            manager.update(events)
            manager.draw(surf)
            pygame.display.update()
            clock.tick(fps)

    def queue_popup(self, file_name):
        self.queued_windows.append(file_name)

    def load_popup(self, file_name, size=None, offset=None):
        if not size:
            size = pygame.display.get_surface().get_size()
        self.queued_windows.clear()
        self.current_window = ''
        self.window = GUIWindow(*size, offset)
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

    def draw(self, surf: pygame.Surface, offset=(0, 0)):
        if self.minimized:
            return
        if self.window:
            self.window.draw(surf, offset)
            # pygame.draw.rect(pygame.display.get_surface(), 'red', self.window.root.rect, 10)
