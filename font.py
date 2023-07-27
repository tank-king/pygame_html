import pygame
from functools import lru_cache


# class STYLE:
#     DEFAULTS = {
#         'font-settings': {
#             'font': 'consolas',
#             'size': 30,
#             'bold': False,
#             'italic': False,
#             'underline': False,
#             'strikethrough': False,
#             'wraplength': 0,
#             'text': '',
#             'antialias': True,
#             'color': 'white'
#         }
#     }


class FontEngine:
    DEFAULT_FONT_SIZE = 16  # 16 em is the base font size for HTML rendering
    DEFAULTS = {
        'font': 'times new roman',
        'size': 16,
        'bold': False,
        'italic': False,
        'underline': False,
        'strikethrough': False,
        'wraplength': 0,
        'text': '',
        'antialias': True,
        'color': 'black',
        'prepend': '',
        'append': ''
    }

    @staticmethod
    def get_font_size(em):
        return FontEngine.DEFAULT_FONT_SIZE * em

    @staticmethod
    @lru_cache(maxsize=100)
    def get_font(font, size, bold, italic, underline, strikethrough):
        if not pygame.font.get_init():
            pygame.font.init()
        f = pygame.font.SysFont(font, size, bold, italic)
        if underline:
            f.set_underline(underline)
            f.set_strikethrough(strikethrough)
        return f

    @staticmethod
    @lru_cache(maxsize=100)
    def get_text(font, text, antialias, color, size, bold, italic, underline, strikethrough, wraplength=0, prepend='',
                 append=''):
        font = FontEngine.get_font(font, size, bold, italic, underline, strikethrough)
        text = prepend + text + append
        text = text.replace('\t', '    ')  # convert tabs to 4 spaces
        return font.render(text, antialias, color)

    @staticmethod
    def generate_text(**kwargs):
        settings = FontEngine.DEFAULTS.copy()
        for i, j in kwargs.items():
            settings[i] = j
        try:
            settings['size'] = int(settings['size'])
        except ValueError:
            settings['size'] = FontEngine.DEFAULTS.copy()['size']
        return FontEngine.get_text(**settings)
