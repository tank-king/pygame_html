import pygame.image

from .container import *


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

    def draw(self, surf: pygame.Surface, offset=(0, 0)):
        super().draw(surf, offset)
        text = FontEngine.generate_text(**self.font_settings)
        surf.blit(text, text.get_rect(topleft=self.rect.topleft))


class BContainer(Container):
    def __init__(self, **kwargs):
        kwargs['bold'] = True
        super().__init__(**kwargs)


class IContainer(Container):
    def __init__(self, **kwargs):
        kwargs['italic'] = True
        super().__init__(**kwargs)


class CENTERContainer(Container):
    def __init__(self, **kwargs):
        kwargs['align'] = 'center'
        super().__init__(**kwargs)


class PContainer(Container):
    BEFORE_APPEND = [['BRContainer', {}]]
    AFTER_APPEND = [['BRContainer', {}]]


class AContainer(Container):
    def __init__(self, **kwargs):
        kwargs['underline'] = True
        self.href = ''
        super().__init__(**kwargs)

    def on_link_pressed(self):
        try:
            self.root.window.load_from_html(self.href)
        except Exception as e:
            _ = e
            print(e)

    def update(self, events: list[pygame.event.Event], dt=1.0):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if self.selected and self.href:
                        self.on_link_pressed()
        # current = self.font_settings['color']
        self.font_settings['color'] = 'magenta' if self.selected else 'white'
        for i in self.children:
            if isinstance(i, TextContainer):
                i.font_settings['color'] = self.font_settings['color']
        super().update(events, dt)


class IMGContainer(Container):
    def __init__(self, **kwargs):
        self.src = ''
        self.image = None
        self.image_to_render = None
        super().__init__(**kwargs)

    def setup(self):
        if self.src:
            self.image = pygame.image.load(self.src).convert_alpha()
            self.image_to_render = self.image.copy()
            if not self.width:
                self.width = self.image.get_width()
            if not self.height:
                self.height = self.image.get_height()

    def draw(self, surf: pygame.Surface, offset=(0, 0)):
        if self.image and self.image_to_render:
            w = self.width if self.width else self.image.get_width()
            h = self.height if self.height else self.image.get_height()
            if self.image.get_size() != (w, h):
                self.image_to_render = pygame.transform.scale(self.image, (w, h))
            surf.blit(self.image_to_render, [*self.pos])


class BUTTONContainer(Container):
    # TODO
    pass
