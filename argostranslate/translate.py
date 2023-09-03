from __future__ import annotations

from typing import List

import ctranslate2
import sentencepiece as spm
import stanza
from ctranslate2 import Translator

from argostranslate import apis, fewshot, package, sbd, settings
from argostranslate.models import ILanguageModel
from argostranslate.package import Package
from argostranslate.utils import info


class Hypothesis:
    """Represents a translation hypothesis

    Attributes:
        value: The hypothetical translation value
        score: The score representing the quality of the translation
    """

    value: str
    score: float

    def __init__(self, value: str, score: float):
        self.value = value
        self.score = score

    def __lt__(self, other):
        return self.score < other.score

    def __repr__(self):
        return f"({repr(self.value)}, {self.score})"

    def __str__(self):
        return repr(self)


class ITranslation:
    """Represents a translation between two Languages

    Attributes:
        from_lang: The Language this Translation translates from.
        to_lang: The Language this Translation translates to.

    """

    from_lang: Language
    to_lang: Language

    def translate(self, input_text: str) -> str:
        """Translates a string from self.from_lang to self.to_lang

        Args:
            input_text: The text to be translated.

        Returns:
            input_text translated.

        """
        return self.hypotheses(input_text, num_hypotheses=1)[0].value

    def hypotheses(self, input_text: str, num_hypotheses: int = 4) -> list[Hypothesis]:
        """Translates a string from self.from_lang to self.to_lang

        Args:
            input_text: The text to be translated.
            num_hypotheses: Number of hypothetic results expected

        Returns:
            List of translation hypotheses

        """
        raise NotImplementedError()

    @staticmethod
    def split_into_paragraphs(input_text: str) -> list[str]:
        """Splits input_text into paragraphs and returns a list of paragraphs.

        Args:
            input_text: The text to be split.

        Returns:
            A list of paragraphs.

        """
        return input_text.split("\n")

    @staticmethod
    def combine_paragraphs(paragraphs: list[str]) -> str:
        """Combines a list of paragraphs together.

        Args:
            paragraphs: A list of paragraphs.

        Returns:
            list of n paragraphs combined into one string.

        """
        return "\n".join(paragraphs)

    def __repr__(self):
        return str(self.from_lang) + " -> " + str(self.to_lang)

    def __str__(self):
        return repr(self).replace("->", "→")


class Language:
    """Represents a language that can be translated from/to.

    Attributes:
        code: The code representing the language.
        name: The human readable name of the language.
        translations_from: A list of the translations
            that translate from this language.
        translations_to: A list of the translations
            that translate to this language

    """

    translations_from: list[ITranslation] = []
    translations_to: list[ITranslation] = []

    def __init__(self, code: str, name: str):
        self.code = code
        self.name = name
        self.translations_from = []
        self.translations_to = []

    def __str__(self):
        return self.name

    def get_translation(self, to: Language) -> ITranslation | None:
        """Gets a translation from this Language to another Language.

        Args:
            to: The Language to look for a Translation to.

        Returns:
            A valid Translation if there is one in translations_from
                else None.

        """
        valid_translations = list(
            filter(lambda x: x.to_lang.code == to.code, self.translations_from)
        )
        if len(valid_translations) > 0:
            return valid_translations[0]
        return None


class PackageTranslation(ITranslation):
    """A Translation that is installed with a package"""

    def __init__(self, from_lang: Language, to_lang: Language, pkg: Package):
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.pkg = pkg
        self.translator = None

    def hypotheses(self, input_text: str, num_hypotheses: int = 4) -> list[Hypothesis]:
        if self.translator is None:
            model_path = str(self.pkg.package_path / "model")
            self.translator = ctranslate2.Translator(model_path, device=settings.device)
        paragraphs = ITranslation.split_into_paragraphs(input_text)
        info("paragraphs:", paragraphs)
        translated_paragraphs = []
        for paragraph in paragraphs:
            translated_paragraphs.append(
                apply_packaged_translation(
                    self.pkg, paragraph, self.translator, num_hypotheses
                )
            )
        info("translated_paragraphs:", translated_paragraphs)

        # Construct new hypotheses using all paragraphs
        hypotheses_to_return = [Hypothesis("", 0) for i in range(num_hypotheses)]
        for i in range(num_hypotheses):
            for translated_paragraph in translated_paragraphs:
                value = ITranslation.combine_paragraphs(
                    [hypotheses_to_return[i].value, translated_paragraph[i].value]
                )
                score = hypotheses_to_return[i].score + translated_paragraph[i].score
                hypotheses_to_return[i] = Hypothesis(value, score)
            hypotheses_to_return[i].value = hypotheses_to_return[i].value.lstrip("\n")
        info("hypotheses_to_return:", hypotheses_to_return)
        return hypotheses_to_return


class IdentityTranslation(ITranslation):
    """A Translation that doesn't modify input_text."""

    def __init__(self, lang: Language):
        """Creates an IdentityTranslation.

        Args:
            lang: The Language this Translation translates
                from and to.

        """
        self.from_lang = lang
        self.to_lang = lang

    def hypotheses(self, input_text: str, num_hypotheses: int = 4):
        return [Hypothesis(input_text, 0) for i in range(num_hypotheses)]


class CompositeTranslation(ITranslation):
    """A ITranslation that is performed by chaining two Translations

    Attributes:
        t1: The first Translation to apply.
        t2: The second Translation to apply.

    """

    t1: ITranslation
    t2: ITranslation
    from_lang: Language
    to_lang: Language

    def __init__(self, t1: ITranslation, t2: ITranslation):
        """Creates a CompositeTranslation.

        Args:
            t1: The first Translation to apply.
            t2: The second Translation to apply.
        """
        self.t1 = t1
        self.t2 = t2
        self.from_lang = t1.from_lang
        self.to_lang = t2.to_lang

    def hypotheses(self, input_text: str, num_hypotheses: int = 4) -> list[Hypothesis]:
        t1_hypotheses = self.t1.hypotheses(input_text, num_hypotheses)

        # Combine hypotheses
        # O(n^2)
        to_return = []
        for t1_hypothesis in t1_hypotheses:
            t2_hypotheses = self.t2.hypotheses(t1_hypothesis.value, num_hypotheses)
            for t2_hypothesis in t2_hypotheses:
                to_return.append(
                    Hypothesis(
                        t2_hypothesis.value, t1_hypothesis.score + t2_hypothesis.score
                    )
                )
        to_return.sort(reverse=True)
        return to_return[0:num_hypotheses]


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

    underlying: ITranslation
    from_lang: Language
    to_lang: Language
    cache: dict

    def __init__(self, underlying: ITranslation):
        """Creates a CachedTranslation.

        Args:
            underlying: The underlying translation to cache.
        """
        self.underlying = underlying
        self.from_lang = underlying.from_lang
        self.to_lang = underlying.to_lang
        self.cache = dict()

    def hypotheses(self, input_text: str, num_hypotheses: int = 4) -> list[Hypothesis]:
        new_cache = dict()  # 'text': ['t1'...('tN')]
        paragraphs = ITranslation.split_into_paragraphs(input_text)
        translated_paragraphs = []
        for paragraph in paragraphs:
            translated_paragraph = self.cache.get(paragraph)
            # If len() of our cached items are different than `num_hypotheses` it means that
            # the search parameter is changed by caller, so we can't re-use cache, and should update it.
            if (
                translated_paragraph is None
                or len(translated_paragraph) != num_hypotheses
            ):
                translated_paragraph = self.underlying.hypotheses(
                    paragraph, num_hypotheses
                )
            new_cache[paragraph] = translated_paragraph
            translated_paragraphs.append(translated_paragraph)
        self.cache = new_cache

        # Construct hypotheses
        hypotheses_to_return = [Hypothesis("", 0) for i in range(num_hypotheses)]
        for i in range(num_hypotheses):
            for j in range(len(translated_paragraphs)):
                value = ITranslation.combine_paragraphs(
                    [hypotheses_to_return[i].value, translated_paragraphs[j][i].value]
                )
                score = (
                    hypotheses_to_return[i].score + translated_paragraphs[j][i].score
                )
                hypotheses_to_return[i] = Hypothesis(value, score)
            hypotheses_to_return[i].value = hypotheses_to_return[i].value.lstrip("\n")
        return hypotheses_to_return


class RemoteTranslation(ITranslation):
    """A translation provided by a remote LibreTranslate server"""

    from_lang: Language
    to_lang: Language

    def __init__(self, from_lang: Language, to_lang: Language, api):
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.api = api

    def hypotheses(self, input_text: str, num_hypotheses: int = 1) -> list[Hypothesis]:
        """LibreTranslate only supports single hypotheses.

        A list of length num_hypotheses will be returned with identical hypotheses.
        """
        result = self.api.translate(input_text, self.from_lang.code, self.to_lang.code)
        return [Hypothesis(result, 0)] * num_hypotheses


# Backwards compatibility, renamed in 1.8
LibreTranslateTranslation = RemoteTranslation


class FewShotTranslation(ITranslation):
    """A translation performed with a few shot language model"""

    from_lang: Language
    to_lang: Language
    language_model: ILanguageModel

    def __init__(
        self, from_lang: Language, to_lang: Language, language_model: ILanguageModel
    ):
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.language_model = language_model

    def hypotheses(self, input_text: str, num_hypotheses: int = 1) -> list[Hypothesis]:
        # Split into sentences
        DEFAULT_SENTENCE_LENGTH = 250
        sentences = []
        start_index = 0
        while start_index < len(input_text) - 1:
            prompt = sbd.generate_fewshot_sbd_prompt(input_text[start_index:])
            response = sbd.parse_fewshot_response(self.language_model.infer(prompt))
            detected_sentence_index = sbd.process_seq2seq_sbd(
                input_text[start_index:], response
            )
            if detected_sentence_index == -1:
                # Couldn't find sentence boundary
                sbd_index = start_index + DEFAULT_SENTENCE_LENGTH
            else:
                sbd_index = start_index + detected_sentence_index
            sentences.append(input_text[start_index:sbd_index])
            info("start_index", start_index)
            info("sbd_index", sbd_index)
            info(input_text[start_index:sbd_index])
            start_index = sbd_index

        to_return = ""
        for sentence in sentences:
            prompt = fewshot.generate_prompt(
                sentence,
                self.from_lang.name,
                self.from_lang.code,
                self.to_lang.name,
                self.to_lang.code,
            )
            info("fewshot prompt", prompt)
            response = self.language_model.infer(prompt)
            info("fewshot response", response)
            result = fewshot.parse_inference(response)
            info("fewshot result", result)
            to_return += result
        return [Hypothesis(to_return, 0)] * num_hypotheses


def apply_packaged_translation(
    pkg: Package, input_text: str, translator: Translator, num_hypotheses: int = 4
) -> list[Hypothesis]:
    """Applies the translation in pkg to translate input_text.

    Args:
        pkg: The package that provides the translation.
        input_text: The text to be translated.
        translator: The CTranslate2 Translator
        num_hypotheses: The number of hypotheses to generate

    Returns:
        A list of Hypothesis's for translating input_text

    """

    info("apply_packaged_translation", input_text)

    # Sentence boundary detection
    if pkg.type == "sbd":
        sentences = [input_text]
    elif settings.stanza_available:
        stanza_pipeline = stanza.Pipeline(
            lang=pkg.from_code,
            dir=str(pkg.package_path / "stanza"),
            processors="tokenize",
            use_gpu=settings.device == "cuda",
            logging_level="WARNING",
        )
        stanza_sbd = stanza_pipeline(input_text)
        sentences = [sentence.text for sentence in stanza_sbd.sentences]
    else:
        DEFAULT_SENTENCE_LENGTH = 250
        sentences = []
        start_index = 0

        # Get sbd translation
        sbd_package = sbd.get_sbd_package()
        assert sbd_package is not None
        sbd_translation = PackageTranslation(None, None, sbd_package)

        while start_index < len(input_text) - 1:
            detected_sentence_index = sbd.detect_sentence(
                input_text[start_index:], sbd_translation
            )
            if detected_sentence_index == -1:
                # Couldn't find sentence boundary
                sbd_index = start_index + DEFAULT_SENTENCE_LENGTH
            else:
                sbd_index = start_index + detected_sentence_index
            sentences.append(input_text[start_index:sbd_index])
            info("start_index", start_index)
            info("sbd_index", sbd_index)
            info(input_text[start_index:sbd_index])
            start_index = sbd_index
    info("sentences", sentences)

    # Tokenization
    sp_model_path = str(pkg.package_path / "sentencepiece.model")
    sp_processor = spm.SentencePieceProcessor(model_file=sp_model_path)
    tokenized = [sp_processor.encode(sentence, out_type=str) for sentence in sentences]
    info("tokenized", tokenized)

    # Translation
    BATCH_SIZE = 32
    translated_batches = translator.translate_batch(
        tokenized,
        replace_unknowns=True,
        max_batch_size=BATCH_SIZE,
        beam_size=max(num_hypotheses, 4),
        num_hypotheses=num_hypotheses,
        length_penalty=0.2,
        return_scores=True,
    )
    info("translated_batches", translated_batches)

    # Build hypotheses
    value_hypotheses = []
    for i in range(num_hypotheses):
        translated_tokens = []
        cumulative_score = 0
        for translated_batch in translated_batches:
            translated_tokens += translated_batch[i]["tokens"]
            cumulative_score += translated_batch[i]["score"]
        detokenized = "".join(translated_tokens)
        detokenized = detokenized.replace("▁", " ")
        value = detokenized
        if len(value) > 0 and value[0] == " ":
            # Remove space at the beginning of the translation added
            # by the tokenizer.
            value = value[1:]
        hypothesis = Hypothesis(value, cumulative_score)
        value_hypotheses.append(hypothesis)
    info("value_hypotheses:", value_hypotheses)
    return value_hypotheses


class InstalledTranslate:
    """
    Global storage of instances of the CachedTranslation class by unique keys.
    To avoid creating unnecessary objects in memory.
    """

    package_key: str
    cached_translation: CachedTranslation


installed_translates: List[InstalledTranslate] = []


def get_installed_languages() -> list[Language]:
    """Returns a list of Languages installed from packages"""

    info("get_installed_languages")

    if settings.model_provider == settings.ModelProvider.OPENNMT:
        packages = package.get_installed_packages()

        # If stanza not available filter for sbd available
        if not settings.stanza_available:
            sbd_packages = list(filter(lambda x: x.type == "sbd", packages))
            sbd_available_codes = set()
            for sbd_package in sbd_packages:
                sbd_available_codes = sbd_available_codes.union(sbd_package.from_codes)
            packages = list(
                filter(lambda x: x.from_code in sbd_available_codes, packages)
            )

        # Filter for translate packages
        packages = list(filter(lambda x: x.type == "translate", packages))

        # Load languages and translations from packages
        language_of_code = dict()
        for pkg in packages:
            if pkg.from_code not in language_of_code:
                language_of_code[pkg.from_code] = Language(pkg.from_code, pkg.from_name)
            if pkg.to_code not in language_of_code:
                language_of_code[pkg.to_code] = Language(pkg.to_code, pkg.to_name)
            from_lang = language_of_code[pkg.from_code]
            to_lang = language_of_code[pkg.to_code]

            package_key = f"{pkg.from_code}-{pkg.to_code}"
            contain = list(
                filter(lambda x: x.package_key == package_key, installed_translates)
            )
            translation_to_add: CachedTranslation
            if len(contain) == 0:
                translation_to_add = CachedTranslation(
                    PackageTranslation(from_lang, to_lang, pkg)
                )
                saved_cache = InstalledTranslate()
                saved_cache.package_key = package_key
                saved_cache.cached_translation = translation_to_add
                installed_translates.append(saved_cache)
            else:
                translation_to_add = contain[0].cached_translation

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
                        if language.get_translation(translation_2.to_lang) is None:
                            # The language currently doesn't have a way to translate
                            # to this language
                            keep_adding_translations = True
                            composite_translation = CompositeTranslation(
                                translation, translation_2
                            )
                            language.translations_from.append(composite_translation)
                            translation_2.to_lang.translations_to.append(
                                composite_translation
                            )

    elif settings.model_provider == settings.ModelProvider.LIBRETRANSLATE:
        # TODO: Add API key and custom URL support
        libretranslate_api = apis.LibreTranslateAPI()
        supported_languages = (
            libretranslate_api.languages()
        )  # [{"code":"en", "name":"English"}]
        languages = [Language(l["code"], l["name"]) for l in supported_languages]
        for from_lang in languages:
            for to_lang in languages:
                translation = LibreTranslateTranslation(
                    from_lang, to_lang, libretranslate_api
                )
                from_lang.translations_from.append(translation)
                to_lang.translations_to.append(translation)

    elif settings.model_provider == settings.ModelProvider.OPENAI:
        language_model = apis.OpenAIAPI(settings.openai_api_key)
        # TODO
        languages = [Language("en", "English"), Language("es", "Spanish")]
        for from_lang in languages:
            for to_lang in languages:
                translation = FewShotTranslation(from_lang, to_lang, language_model)
                from_lang.translations_from.append(translation)
                to_lang.translations_to.append(translation)

    # Put English first if available so it shows up as the from language in the gui
    en_index = None
    for i, language in enumerate(languages):
        if language.code == "en":
            en_index = i
            break
    english = None
    if en_index is not None:
        english = languages.pop(en_index)
    languages.sort(key=lambda x: x.name)
    if english is not None:
        languages = [english] + languages

    return languages


def load_installed_languages() -> list[Language]:
    """Deprecated 1.2, use get_installed_languages"""
    return get_installed_languages()


def get_language_from_code(code: str) -> Language | None:
    """Gets a language object from a code

    An exception will be thrown if an installed language with this
    code can not be found.

    Args:
        code: The ISO 639 code of the language

    Returns:
        The language object
    """
    return next(filter(lambda x: x.code == code, get_installed_languages()), None)


def get_translation_from_codes(from_code: str, to_code: str) -> ITranslation:
    """Gets a translation object from codes for from and to languages

    An exception will be thrown if an installed translation between the from lang
    and to lang can not be found.

    Args:
        from_code: The ISO 639 code of the source language
        to_code: The ISO 639 code of the target language

    Returns:
        The translation object
    """
    from_lang = get_language_from_code(from_code)
    to_lang = get_language_from_code(to_code)
    return from_lang.get_translation(to_lang)


def translate(q: str, from_code: str, to_code: str) -> str:
    """Translate a string of text

    Args:
        q: The text to translate
        from_code: The ISO 639 code of the source language
        to_code: The ISO 639 code of the target language

    Returns:
        The translated text
    """
    translation = get_translation_from_codes(from_code, to_code)
    return translation.translate(q)
