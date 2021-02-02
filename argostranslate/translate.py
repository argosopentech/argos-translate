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
        translations_from ([ITranslation]): A list of the translations
            that translate from this language.
        translations_to ([ITranslation]): A list of the translations
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
            ITranslation: A valid Translation if there is one in translations_from
                else None.

        """
        valid_translations = list(filter(lambda x: x.to_lang.code == to.code,
                self.translations_from))
        if len(valid_translations) > 0:
            return valid_translations[0]
        return None

class ITranslation:
    """Respresents a translation between two Languages

    Attributes:
        from_lang (Language): The Language this Translation translates from.
        to_lang (Language): The Language this Translation translates to.

    """
    def translate(self, input_text):
        """Translates a string from self.from_lang to self.to_lang

        Args:
            input_text (str): The text to be translated.

        Returns:
            str: input_text translated.

        """
        raise NotImplementedError()

    def split_into_paragraphs(self, input_text):
        """Splits input_text into paragraphs and returns a list of paragraphs.

        Args:
            input_text (str): The text to be split.

        Returns:
            [str]: A list of paragraphs.

        """
        return input_text.split('\n')

    def combine_paragraphs(self, paragraphs):
        """Combines a list of paragraphs together.

        Args:
            paragraphs ([str]): A list of paragraphs.

        Returns:
            str: paragraphs combined into one string.

        """
        return '\n'.join(paragraphs)

    def __str__(self):
        return str(self.from_lang) + ' -> ' + str(self.to_lang)

class PackageTranslation(ITranslation):
    """Translation from a package

    Attributes:
        from_lang (Language): The Language this Translation translates from.
        to_lang (Language): The Language this Translation translates to.
        pkg (Package): The installed package that provides this translation.

    """

    def __init__(self, from_lang, to_lang, pkg):
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.pkg = pkg
        self.translator = None

    def translate(self, input_text):
        if self.translator == None:
            model_path = str(self.pkg.package_path / 'model')
            self.translator = ctranslate2.Translator(model_path)
        paragraphs = self.split_into_paragraphs(input_text)
        translated_paragraphs = []
        for paragraph in paragraphs:
            translated_paragraphs.append(
                    apply_packaged_translation(self.pkg, paragraph, self.translator))
        return self.combine_paragraphs(translated_paragraphs)

class IdentityTranslation(ITranslation):
    """A Translation that doesn't modify input_text."""

    def __init__(self, lang):
        """Creates an IdentityTranslation.

        Args:
            lang (Language): The Language this Translation translates
                from and to.

        """
        self.from_lang = lang
        self.to_lang = lang

    def translate(self, input_text):
        return input_text

class CompositeTranslation(ITranslation):
    """A ITranslation that is performed by chaining two Translations
    
    Attributes:
        t1 (ITranslation): The first Translation to apply.
        t2 (ITranslation): The second Translation to apply.

    """

    def __init__(self, t1, t2):
        self.t1 = t1
        self.t2 = t2
        self.from_lang = t1.from_lang
        self.to_lang = t2.to_lang

    def translate(self, input_text):
        return self.t2.translate(self.t1.translate(input_text))

class CachedTranslation(ITranslation):
    """Caches a translation to improve performance.

    This is done by splitting up the text passed for translation
    into paragraphs and translating each paragraph individually.
    A hash of the paragraphs and their corresponding translations
    are saved from the previous translation and used to improve
    performance on the next one. This is especially useful if you
    are repeatedly translating nearly identical text with a small
    change at the end of it. 

    """

    def __init__(self, underlying):
        """Creates a CachedTranslation.

        Args:
            translation (ITranslation): The underlying translation to cache.

        """
        self.underlying = underlying
        self.from_lang = underlying.from_lang
        self.to_lang = underlying.to_lang
        self.cache = dict()

    def translate(self, input_text):
        new_cache = dict()
        paragraphs = self.split_into_paragraphs(input_text)
        translated_paragraphs = []
        for paragraph in paragraphs:
            translated_paragraph = self.cache.get(paragraph)
            if translated_paragraph == None:
                translated_paragraph = self.underlying.translate(paragraph)
            new_cache[paragraph] = translated_paragraph
            translated_paragraphs.append(translated_paragraph)
        self.cache = new_cache
        return self.combine_paragraphs(translated_paragraphs)


def apply_packaged_translation(pkg, input_text, translator): 
    """Applies the translation in pkg to translate input_text.

    Args:
        pkg (Package): The package that provides the translation.
        input_text (str): The text to be translated.

    Returns:
        str: The translated text.

    """

    sp_model_path = str(pkg.package_path / 'sentencepiece.model')
    sp_processor = spm.SentencePieceProcessor(model_file=sp_model_path)
    stanza_pipeline = stanza.Pipeline(lang=pkg.from_code,
            dir=str(pkg.package_path / 'stanza'),
            processors='tokenize', use_gpu=False,
            logging_level='WARNING')
    stanza_sbd = stanza_pipeline(input_text)
    sentences = [sentence.text for sentence in stanza_sbd.sentences]
    tokenized = [sp_processor.encode(sentence, out_type=str) for sentence in sentences]
    translated_batches = translator.translate_batch(
            tokenized,
            replace_unknowns=True,
            max_batch_size=32,
            length_penalty=0.2)
    translated_tokens = []
    for translated_batch in translated_batches:
        translated_tokens += translated_batch[0]['tokens']
    detokenized = ''.join(translated_tokens)
    detokenized = detokenized.replace('▁', ' ')
    to_return = detokenized
    if len(to_return) > 0 and to_return[0] == ' ':
        # Remove space at the beginning of the translation added
        # by the tokenizer.
        to_return = to_return[1:]
    return to_return

def load_installed_languages():
    """Returns a list of Languages installed from packages"""
    
    packages = package.get_installed_packages()

    # Load languages and translations from packages
    language_of_code = dict()
    for pkg in packages:
        if pkg.from_code not in language_of_code:
            language_of_code[pkg.from_code] = Language(
                    pkg.from_code, pkg.from_name)
        if pkg.to_code not in language_of_code:
            language_of_code[pkg.to_code] = Language(
                    pkg.to_code, pkg.to_name)
        from_lang = language_of_code[pkg.from_code]
        to_lang = language_of_code[pkg.to_code]
        translation_to_add = CachedTranslation(PackageTranslation(
                from_lang, to_lang, pkg))
        from_lang.translations_from.append(translation_to_add)
        to_lang.translations_to.append(translation_to_add)

    languages = list(language_of_code.values())

    # Add translations so everything can translate to itself
    for language in languages:
        identity_translation = IdentityTranslation(language)
        language.translations_from.append(identity_translation)
        language.translations_to.append(identity_translation)

    # Pivot through intermediate languages to add translations
    # that don't already exist
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
                        composite_translation = CompositeTranslation(translation, translation_2)
                        language.translations_from.append(composite_translation)
                        translation_2.to_lang.translations_to.append(composite_translation)

    # Put English first if available so it shows up as the from language in the gui
    en_index = None
    for i, language in enumerate(languages):
        if language.code == 'en':
            en_index = i
            break
    english = None
    if en_index != None:
        english = languages.pop(en_index)
    languages.sort(key=lambda x: x.name)
    if english != None:
        languages = [english] + languages

    return languages

