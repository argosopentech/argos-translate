from pathlib import Path

import ctranslate2
import sentencepiece as spm
import nltk

from argos_translate import package

class Language:
    """Represents a language that can be translated from/to"""

    def __init__(self, code, name):
        self.code = code
        self.name = name
        self.translations_from = []
        self.translations_to = []

    def __str__(self):
        return self.name

    def get_translation(self, to):
        valid_translations = list(filter(lambda x: x.to_lang.code == to.code,
                self.translations_from))
        if len(valid_translations) > 0:
            return valid_translations[0]
        return None

class Translation:
    """Respresents a translation between two Languages"""

    def __init__(self, from_lang, to_lang, translate_function):
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.translate_function = translate_function
        from_lang.translations_from.append(self)
        to_lang.translations_to.append(self)

    def __str__(self):
        return str(self.from_lang) + ' -> ' + str(self.to_lang)

def load_languages_from_packages():
    """Returns a list of Languages loaded from packages"""
    
    packages = package.get_installed_packages()
    language_of_code = dict()
    for pkg in packages:
        if pkg.from_code not in language_of_code:
            language_of_code[pkg.from_code] = Language(
                    pkg.from_code, pkg.from_name)
        if pkg.to_code not in language_of_code:
            language_of_code[pkg.to_code] = Language(
                    pkg.to_code, pkg.to_name)

        def translate_function(input_text):
            model_path = str(pkg.package_path / 'model')
            translator = ctranslate2.Translator(model_path)
            sp_model_path = str(pkg.package_path / 'sentencepiece.model')
            sp_processor = spm.SentencePieceProcessor(model_file=sp_model_path)
            punkt_path = str(pkg.package_path / 'punkt.pickle')
            punkt = nltk.data.load(punkt_path)
            sentences = punkt.tokenize(input_text.strip())
            to_return = ''
            for sentence in sentences:
                tokenized = sp_processor.encode(sentence, out_type=str)
                translated = translator.translate_batch([tokenized])
                translated = translated[0][0]['tokens']
                detokenized = ''.join(translated)
                detokenized = detokenized.replace('▁', ' ')
                to_return += detokenized
            return to_return

        Translation(language_of_code[pkg.from_code],
                language_of_code[pkg.to_code], translate_function)

    languages = list(language_of_code.values())

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
                        # The language currently doesn't have a way to translate
                        # to this language
                        keep_adding_translations = True
                        trans_fun = composite_fun(translation.translate_function,
                                translation_2.translate_function)
                        Translation(language, translation_2.to_lang, trans_fun) 
    
    languages.sort(key=lambda x: x.code)
    return languages

