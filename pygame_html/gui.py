from html.parser import HTMLParser
import importlib

from pygame_html.container import *
from pygame_html.container_definitions import *


# class MyHTMLParser(HTMLParser):
#     def handle_starttag(self, tag, attrs):
#         print("Encountered a start tag:", tag)
#
#     def handle_endtag(self, tag):
#         print("Encountered an end tag :", tag)
#
#     def handle_data(self, data):
#         print("Encountered some data  :", data)
#

class GUIWindow(BaseStructure, HTMLParser):
    def __init__(self, width, height):
        super().__init__()
        self.root: Container = Container(width=width, height=height)
        self.root.window = self
        self.root.label = 'root'
        # self.root.move((50, 50))
        # self.root.set_pos((100, 100))
        # print(self.root.get_capped_width())
        # self.root.align = 'right'
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
        # self.stack.pop() if self.stack else True

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

    def get_container_from_tag(self, tag, attrs):
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

    # def set_layout(self, parent: Container, element: Element):
    #     for child in element:
    #         cont = self.create_gui_container(child)
    #         self.set_layout(cont, child)
    #         parent.add_child(cont)

    def update(self, events: list[pygame.event.Event], dt=1.0):
        self.root.update(events, dt)
        # print(self.root.effective_rect)

    def draw(self, surf: pygame.Surface, offset=(0, 0)):
        self.root.draw(surf, offset)


class GUIManager(BaseStructure):
    def __init__(self):
        self.window: Optional[GUIWindow] = None
        self.queued_windows = ['sample.html']

    def display_popup(self, file_name):
        self.queued_windows.append(file_name)

    def close_popup(self):
        # to be used externally
        if self.window:
            self.window = None

    def update(self, events: list[pygame.event.Event], dt=1.0):
        if self.window:
            self.window.update(events, dt)
        else:
            if self.queued_windows:
                self.window = GUIWindow(*pygame.display.get_surface().get_size())
                # self.window = GUIWindow(0, 0)
                self.window.load_from_html(self.queued_windows.pop(0))

    def draw(self, surf: pygame.Surface, offset=(0, 0)):
        if self.window:
            self.window.draw(surf, offset)
            # pygame.draw.rect(pygame.display.get_surface(), 'red', self.window.root.rect, 10)
