from argostranslate import settings

def info(*args):
    if settings.debug:
        print(args)

def warning(*args):
    print(args)

def error(*args):
    print(args)
