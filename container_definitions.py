from pathlib import Path

import pygame.image

import pygame_html
from pygame_html.container import *
from pygame_html.event import QUIT_EVENT


class TextContainer(Container):
    """
    Leaf Node/Container
    Very important class
    """

    def setup(self):
        text = FontEngine.generate_text(**self.font_settings)
        self.width, self.height = text.get_size()

    # def update(self, events: list[pygame.event.Event], dt=1.0):
    #     super().update(events, dt)

    def __repr__(self):
        return f'<TextContainer(text={self.font_settings["text"]})>'

    def draw(self, surf: pygame.Surface, offset=(0, 0)):
        super().draw(surf, offset)
        text = FontEngine.generate_text(**self.font_settings)
        surf.blit(text, text.get_rect(topleft=self.rect.topleft))


class AContainer(Container):
    def __init__(self, **kwargs):
        kwargs['underline'] = True
        self.href = ''
        super().__init__(**kwargs)
        self.current_color = self.font_settings['color']

    def on_link_pressed(self):
        debug_print('select')
        if self.href.lower() == '__exit__':
            pygame.event.post(pygame.Event(QUIT_EVENT, {'anchor': self}))
            return
        try:
            href = self.root.window.base_path / Path(self.href)
            window = self.root.window
            window.manager.show_popup(href, size=window.root.size, offset=window.window_offset)
            # self.root.window.load_from_html(self.href)
        except Exception as e:
            _ = e
            debug_print(e)

    @property
    def selected(self):
        return any(i.selected for i in self.children)

    def update(self, events: list[pygame.event.Event], dt=1.0):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if self.selected and self.href:
                        self.on_link_pressed()
        self.font_settings['color'] = 'orange' if self.selected else 'blue'
        for i in self.children:
            if isinstance(i, TextContainer):
                i.font_settings['color'] = self.font_settings['color']
        super().update(events, dt)


class BContainer(Container):
    def __init__(self, **kwargs):
        kwargs['bold'] = True
        super().__init__(**kwargs)


class BodyContainer(Container):
    pass


class ButtonContainer(Container):
    # TODO
    pass


class CenterContainer(Container):
    def __init__(self, **kwargs):
        kwargs['align'] = 'center'
        debug_print('centteerrr')
        super().__init__(**kwargs)
        # self.align = 'center'


class EMContainer(Container):
    def __init__(self, **kwargs):
        kwargs['italic'] = True
        super().__init__(**kwargs)


class H1Container(Container):
    def __init__(self, **kwargs):
        kwargs['size'] = FontEngine.get_font_size(2)
        kwargs['bold'] = True
        super().__init__(**kwargs)


class H2Container(Container):
    def __init__(self, **kwargs):
        kwargs['size'] = FontEngine.get_font_size(1.5)
        kwargs['bold'] = True
        super().__init__(**kwargs)


class H3Container(Container):
    def __init__(self, **kwargs):
        kwargs['size'] = FontEngine.get_font_size(1.17)
        kwargs['bold'] = True
        super().__init__(**kwargs)


class H4Container(Container):
    def __init__(self, **kwargs):
        kwargs['size'] = FontEngine.get_font_size(1)
        kwargs['bold'] = True
        super().__init__(**kwargs)


class H5Container(Container):
    def __init__(self, **kwargs):
        kwargs['size'] = FontEngine.get_font_size(0.83)
        kwargs['bold'] = True
        super().__init__(**kwargs)


class H6Container(Container):
    def __init__(self, **kwargs):
        kwargs['size'] = FontEngine.get_font_size(0.67)
        super().__init__(**kwargs)


# class HeadContainer(Container):
#     pass


class HTMLContainer(Container):
    pass


class IContainer(Container):
    def __init__(self, **kwargs):
        kwargs['italic'] = True
        super().__init__(**kwargs)


class IMGContainer(Container):
    def __init__(self, **kwargs):
        self.src = ''
        self.image = None
        self.image_to_render = None
        super().__init__(**kwargs)

    def setup(self):
        if self.src:
            try:
                self.image = pygame.image.load(self.src).convert_alpha()
                self.image_to_render = self.image.copy()
                if not self.width:
                    self.width = self.image.get_width()
                if not self.height:
                    self.height = self.image.get_height()
            except (pygame.error, FileNotFoundError):
                pass

    def draw(self, surf: pygame.Surface, offset=(0, 0)):
        if self.image and self.image_to_render:
            w = self.width if self.width else self.image.get_width()
            h = self.height if self.height else self.image.get_height()
            if self.image.get_size() != (w, h):
                self.image_to_render = pygame.transform.smoothscale(self.image, (w, h))
            surf.blit(self.image_to_render, [*self.pos])


class ListContainer(Container):
    pass


class LIContainer(Container):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_child(TextContainer(text=' - '))
        # self.font_settings['prepend'] = '\t- '


class PContainer(Container):
    BEFORE_APPEND = [['BRContainer', {}]]
    AFTER_APPEND = [['BRContainer', {}]]

    def __init__(self, **kwargs):
        debug_print(kwargs)
        super().__init__(**kwargs)


class PreContainer(Container):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_settings['font'] = 'consolas'


class StrikeContainer(Container):
    def __init__(self, **kwargs):
        kwargs['strikethrough'] = True
        super().__init__(**kwargs)
