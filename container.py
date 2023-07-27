from typing import Optional

import pygame
from pygame import Vector2

from pygame_html.config import *
from pygame_html.font import *


class BaseStructure:
    def update(self, events: list[pygame.event.Event], dt=1.0):
        pass

    def draw(self, surf: pygame.Surface, offset=(0, 0)):
        pass


class Container(BaseStructure):
    # TODO
    BEFORE_APPEND = ''
    AFTER_APPEND = ''

    def __init__(self, width=0, height=0, label='unlabeled', **kwargs):
        try:
            width = int(width)
        except ValueError:
            width = 0
        try:
            height = int(height)
        except ValueError:
            height = 0
        self.font_settings = FontEngine.DEFAULTS.copy()
        self.label = label
        self.cursor = Vector2(0, 0)
        self.children: list[Container] = []
        self.effective_rect = pygame.Rect(0, 0, width, height)
        self.pos = Vector2()
        self.width = width
        self.height = height
        self.capped_width = width
        self.capped_height = height
        self.pos_type = 'relative'  # or absolute
        self.align = 'left'
        self.parent: Optional['Container'] = None
        self.attributes = {}
        self.init_kwargs = kwargs
        for i, j in kwargs.items():
            self.__setattr__(i, j)

    def __repr__(self):
        return f'<Container(label = {self.label})'

    def __setattr__(self, key, value):
        if hasattr(self, 'font_settings') and key in self.font_settings:
            self.font_settings[key] = value
        else:
            super().__setattr__(key, value)

    def override_font_settings_from_parent(self):
        for i in self.font_settings:
            # TODO this is a temporary fix
            if i == 'text' and self.__class__.__name__ == 'TextContainer':
                continue
            if i not in self.init_kwargs and not self.font_setting_overriden(i):
                # if self.label == 'p':
                # print(i)
                # print(self.parent, self.align, self.parent.align)
                self.__setattr__(i, self.get_override_from_parent(i))
            # if i == 'size':
            #     debug_print(self.label, i, self.get_override_from_parent(i))

    def override_other_settings_from_parent(self):
        pass

    def get_overriden_align_from_parent(self):
        if self.align != 'left' or not self.parent:
            return self.align
        else:
            return self.parent.get_overriden_align_from_parent()

    # def get_setting_overriden(self, setting):
    #     return self.__getattribute__(setting) !=

    def font_setting_overriden(self, setting):
        return self.font_settings.get(setting) != FontEngine.DEFAULTS.get(setting)

    def get_override_from_parent(self, setting):
        if not self.parent or self.font_setting_overriden(setting):
            return self.font_settings[setting]
        else:
            return self.parent.get_override_from_parent(setting)

    def setattr(self, key, value):
        self.attributes[key] = value

    @property
    def size(self):
        return self.width, self.height

    @property
    def capped_rect(self):
        return pygame.Rect(*self.pos, self.capped_width, self.capped_height)

    @property
    def position(self):
        if self.parent is None:
            return self.pos
        else:
            return self.parent.position + self.pos

    @property
    def root(self):
        if self.parent:
            return self.parent.root
        else:
            return self

    @property
    def rect(self):
        return pygame.Rect(*self.pos, self.width, self.height)

    @property
    def rect_absolute(self):
        return pygame.Rect(*self.position, self.width, self.height)

    @property
    def selected(self):
        return self.rect.collidepoint(*pygame.mouse.get_pos())

    @property
    def capped_selected(self):
        return self.capped_rect.collidepoint(*pygame.mouse.get_pos()) and (
            self.parent.capped_selected if self.parent else True
        )

    def move(self, d_pos):
        self.pos += d_pos
        for i in self.children:
            # i.pos += d_pos
            i.move(d_pos)

    def get_capped_width(self):
        if self.children:
            max_width = max(i.width for i in self.children)
        else:
            max_width = 0
        if self.capped_width:
            if max_width > self.capped_width:
                return max_width
            else:
                return self.capped_width
        else:
            if self.parent:
                return self.parent.get_capped_width()
            else:
                if max_width > self.capped_width:
                    return max_width
                else:
                    return self.capped_width

    def setup(self):
        pass

    def set_parent(self, parent: 'Container'):
        self.parent = parent
        self.override_font_settings_from_parent()
        self.align = self.get_overriden_align_from_parent()
        self.setup()

    def set_pos(self, pos):
        d_pos = pygame.Vector2(pos) - self.pos
        self.move(d_pos)

    def add_child(self, child: 'Container'):
        self.children.append(child)
        child.set_parent(self)

    def rearrange_layout(self):
        if self.label in ['body', 'html', 'center', 'p']:
            if self.parent:
                debug_print(self, self.parent, '>>>>>>>>>', self.width, self.parent.width)
                if self.parent.capped_width:
                    self.width = self.parent.capped_width
                else:
                    self.width = self.root.capped_width
        cursor = self.pos + pygame.Vector2()
        lines = [[0, 0]]
        line_containers = [[]]
        # self.effective_rect = pygame.Rect(*self.pos, 0, 0)
        self.effective_rect = self.rect.copy()
        for i in self.children:
            i.rearrange_layout()

            if isinstance(i, BRContainer):
                cursor = pygame.Vector2(*self.effective_rect.bottomleft)
                # cursor = pygame.Vector2(self.pos.x, lines[-1][1])
                lines.append([0, 0])
                line_containers.append([])
            else:
                if self.get_capped_width() and lines[-1][0]:
                    if lines[-1][0] + i.width > self.get_capped_width():
                        cursor = pygame.Vector2(*self.effective_rect.bottomleft)
                        # cursor = pygame.Vector2(self.pos.x, lines[-1][1])
                        lines.append([0, 0])
                        line_containers.append([])

            i.set_pos(cursor)
            line_containers[-1].append(i)
            cursor += [i.width, 0]
            lines[-1][0] += i.width
            lines[-1][1] = max(lines[-1][1], i.height)
            self.effective_rect = pygame.Rect(*self.pos, max([row[0] for row in lines]),
                                              sum([row[1] for row in lines]))
            # TODO temp fixing for hard-capping vertical
            if self.label == 'body':
                if self.effective_rect.height > self.root.capped_height and self.root.capped_height:
                    deleted_containers: list[Container] = line_containers.pop()
                    index = self.children.index(deleted_containers[0])
                    # deleted containers should have at least 1 element
                    self.children = self.children[0:index]
                    for j in deleted_containers:
                        j.parent = None
                        if j in self.children:
                            self.children.remove(j)
                    break

        size_less = self.effective_rect.w < self.width or self.effective_rect.h < self.height
        self.width = max(self.width, self.effective_rect.width)
        self.height = max(self.height, self.effective_rect.height)
        if size_less:
            if not self.capped_width:
                self.width = self.effective_rect.width
            if not self.capped_height:
                self.height = self.effective_rect.height

        # TODO temporary fix as original HTML parsing is different than this GUI system
        if self.align != 'left' or True:
            if self.label in ['body', 'html', 'center', 'p']:
                if self.parent:
                    debug_print(self, self.parent, '>>>>>>>>>', self.width, self.parent.width)
                    if self.parent.capped_width:
                        self.width = self.parent.capped_width
                    else:
                        self.width = self.root.capped_width
                    # self.width = self.parent.width

                for i in line_containers:
                    if not i:
                        continue
                    w = sum(j.width for j in i)
                    align = self.align
                    if align == 'center':
                        d = self.rect.size[0] / 2 - w / 2
                    elif align == 'right':
                        d = self.rect.size[0] - w
                    else:
                        d = 0
                    for j in i:
                        j.move(Vector2(d, 0))

    def set_alignment(self):
        pass

    def update(self, events: list[pygame.event.Event], dt=1.0):
        for i in self.children:
            i.update(events, dt)

    def draw(self, surf: pygame.Surface, offset=(0, 0)):
        if Config.DEBUG:
            if self.selected:
                color = 'red'
            else:
                color = 'black'
            pygame.draw.rect(surf, color, self.rect.move(offset), 1)
        for i in self.children:
            i.draw(surf, offset)
        # pygame.draw.rect(pygame.display.get_surface(), 'red', self.effective_rect.inflate(5, 5), 10)
        # pygame.draw.rect(pygame.display.get_surface(), 'green', self.rect.inflate(5, 5), 10)


class BRContainer(Container):
    def __init__(self, height=None):
        font_size = FontEngine.DEFAULTS['size']
        super().__init__(0, font_size if not height else height, label='br')


class EmptyContainer(Container):
    pass
