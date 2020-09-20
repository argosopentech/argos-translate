from pathlib import Path

import ctranslate2
import sentencepiece as spm
import stanza

from argostranslate import package

class Language:
    """Represents a language that can be translated from/to.

    Attributes:
        code (str): The code representing the language.
        name (str): The human readable name of the language.
        translations_from ([Translation]): A list of the translations
            that translate from this language.
        translations_to ([Translation]): A list of the translations
            that translate to this language

    """

    def __init__(self, code, name):
        self.code = code
        self.name = name
        self.translations_from = []
        self.translations_to = []

    def __str__(self):
        return self.name

    def get_translation(self, to):
        """Gets a translation from this Language to another Language.

        Args:
            to (Language): The Language to look for a Translation to.

        Returns:
            Translation: A valid Translation if there is one in translations_from
                else None.

        """
        valid_translations = list(filter(lambda x: x.to_lang.code == to.code,
                self.translations_from))
        if len(valid_translations) > 0:
            return valid_translations[0]
        return None

class Translation:
    """Respresents a translation between two Languages

    Attributes:
        from_lang (Language): The Language this Translation translates from.
        to_lang (Language): The Language this Translation translates to.
        pkg (Package): The installed package that provides this translation.

    """

    def __init__(self, from_lang, to_lang, pkg):
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.pkg = pkg
        from_lang.translations_from.append(self)
        to_lang.translations_to.append(self)

    def translate(self, input_text):
        """Translates a string using self.pkg.

        Args:
            input_text (str): The text to be translated.

        Returns:
            str: input_text translated.

        """
        return apply_packaged_translation(self.pkg, input_text)

    def __str__(self):
        return str(self.from_lang) + ' -> ' + str(self.to_lang)

class IdentityTranslation(Translation):
    """A Translation that doesn't modify input_text."""

    def __init__(self, lang):
        """Creates an IdentityTranslation.

        Args:
            lang (Language): The Language this Translation translates
                from and to.

        """
        super().__init__(lang, lang, None)

    def translate(self, input_text):
        return input_text

class CompositeTranslation(Translation):
    """A Translation that is performed by chaining two Translations
    
    Attributes:
        t1 (Translation): The first Translation to apply.
        t2 (Translation): The second Translation to apply.

    """

    def __init__(self, t1, t2):
        super().__init__(t1.from_lang, t2.to_lang, None)
        self.t1 = t1
        self.t2 = t2

    def translate(self, input_text):
        return self.t2.translate(self.t1.translate(input_text))

def apply_packaged_translation(pkg, input_text): 
    """Applies the translation in pkg to translate input_text.

    Args:
        pkg (Package): The package that provides the translation.
        input_text (str): The text to be translated.

    Returns:
        str: The translated text.

    """

    model_path = str(pkg.package_path / 'model')
    translator = ctranslate2.Translator(model_path)
    sp_model_path = str(pkg.package_path / 'sentencepiece.model')
    sp_processor = spm.SentencePieceProcessor(model_file=sp_model_path)
    stanza_pipeline = stanza.Pipeline(lang=pkg.from_code,
            dir=str(pkg.package_path / 'stanza'),
            processors='tokenize', use_gpu=False,
            logging_level='WARNING')
    split_by_newlines = input_text.split('\n')
    translated_paragraphs = []
    for paragraph in split_by_newlines:
        stanza_sbd = stanza_pipeline(paragraph)
        sentences = [sentence.text for sentence in stanza_sbd.sentences]
        translated_paragraph = ''
        for sentence in sentences:
            tokenized = sp_processor.encode(sentence, out_type=str)
            translated = translator.translate_batch([tokenized])
            translated = translated[0][0]['tokens']
            detokenized = ''.join(translated)
            detokenized = detokenized.replace('▁', ' ')
            translated_paragraph += detokenized
        translated_paragraphs.append(translated_paragraph)
    return '\n'.join(translated_paragraphs)

def load_installed_languages():
    """Returns a list of Languages installed from packages"""
    
    packages = package.get_installed_packages()
    language_of_code = dict()
    for pkg in packages:
        if pkg.from_code not in language_of_code:
            language_of_code[pkg.from_code] = Language(
                    pkg.from_code, pkg.from_name)
        if pkg.to_code not in language_of_code:
            language_of_code[pkg.to_code] = Language(
                    pkg.to_code, pkg.to_name)

        Translation(language_of_code[pkg.from_code],
                language_of_code[pkg.to_code], pkg)

    languages = list(language_of_code.values())
    # Everything can translate to itself
    for language in languages:
        IdentityTranslation(language)

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
                        CompositeTranslation(translation, translation_2)
    languages.sort(key=lambda x: x.code)
    return languages

