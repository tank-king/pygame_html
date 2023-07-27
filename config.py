FONT = 'consolas'


class Config:
    DEBUG = False


def debug_print(*args):
    if Config.DEBUG:
        print(*args)
