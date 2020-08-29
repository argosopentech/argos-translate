import os
from pathlib import Path

import ctranslate2
import sentencepiece as spm

MODELS_DIR = Path('models/')

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

def c_translation(from_code, to_code):
    def to_return(input_text):
        model_dir = MODELS_DIR / (from_code + '_' + to_code)
        translator = ctranslate2.Translator(str(model_dir / 'converted_model/'))
        sp_processor = spm.SentencePieceProcessor(model_file=str(model_dir / 'sentencepiece.model'))
        tokenized = sp_processor.encode(input_text, out_type=str)
        translated = translator.translate_batch([tokenized])
        translated = translated[0][0]['tokens']
        detokenized = ''.join(translated)
        detokenized = detokenized.replace('▁', ' ')
        return detokenized
    return to_return

# Languages
en = Language('en', 'English')
es = Language('es', 'Spanish')

# Translations
en_es = Translation(en, es, c_translation('en', 'es'))

# Everything can translate to itself
for language in languages:
    Translation(language, language, lambda x: x)

# Pivot through other languages to add translations
def composite_fun(first, second):
    return lambda x: second(first(x))

for language in languages:
    keep_adding_translations = True
    while keep_adding_translations:
        keep_adding_translations = False
        for translation in language.translations_from:
            for translation_2 in translation.to_lang.translations_from:
                if language.get_translation(translation_2.to_lang) == None:
                    # The language currently doesn't have a way to translate to this language
                    keep_adding_translations = True
                    trans_fun = composite_fun(translation.translate_function, translation_2.translate_function)
                    Translation(language, translation_2.to_lang, trans_fun) 
                
