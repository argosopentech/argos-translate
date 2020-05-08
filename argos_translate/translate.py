import os

class Language:
    def __init__(self, code):
        self.code = code
        self.translations_from = []
        self.translations_to = []

class Translation:
    def __init__(self, from_lang, to_lang, translate_function):
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.translate_function = translate_function

def apertium_translation(from_lang, to_lang):
    def to_return(input_text):
        return os.popen('echo \'' + input_text + '\' | apertium ' + from_lang.code + '-' + to_lang.code + '').read()
    return to_return

en = Language('en')
es = Language('es')

en_es = Translation(en, es, apertium_translation(en, es))
