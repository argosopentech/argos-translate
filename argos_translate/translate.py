import os

languages = []

class Language:
    def __init__(self, code, name):
        self.code = code
        self.name = name
        self.translations_from = []
        self.translations_to = []
        languages.append(self)

    def __str__(self):
        return self.name

    def get_translation(self, to):
        print(list(map(str, self.translations_from)))
        valid_translations = list(filter(lambda x: x.to_lang.code == to.code, self.translations_from))
        if len(valid_translations) > 0:
            return valid_translations[0]
        return None

class Translation:
    def __init__(self, from_lang, to_lang, translate_function):
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.translate_function = translate_function
        from_lang.translations_from.append(self)
        to_lang.translations_to.append(self)

    def __str__(self):
        return str(self.from_lang) + ' -> ' + str(self.to_lang)

def apertium_translation(from_lang, to_lang):
    def to_return(input_text):
        return os.popen('echo \'' + input_text + '\' | apertium ' + from_lang.code + '-' + to_lang.code + '').read()
    return to_return

# Languages
en = Language('en', 'English')
es = Language('es', 'Spanish')
eo = Language('eo', 'Esperanto')

# Translations
en_es = Translation(en, es, apertium_translation(en, es))
es_en = Translation(es, en, apertium_translation(es, en))
en_eo = Translation(en, eo, apertium_translation(en, eo))
eo_en = Translation(eo, en, apertium_translation(eo, en))
