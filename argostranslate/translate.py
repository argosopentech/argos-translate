from __future__ import annotations

import functools
from typing import List

import ctranslate2
import sentencepiece

import argostranslate
import argostranslate.chunk
import argostranslate.fewshot
import argostranslate.models
import argostranslate.package
import argostranslate.settings
from argostranslate.utils import error, info, warning


class Hypothesis:
    """Represents a translation hypothesis

    Attributes:
        value: The hypothetical translation value
        score: The score representing the quality of the translation. Higher scores represent higher confidence in correctness.
    """

    value: str
    score: float

    def __init__(self, value: str, score: float):
        self.value = value
        self.score = score

    def __lt__(self, other):
        return self.score < other.score

    def __eq__(self, other):
        return self.score == other.score and self.value == other.value

    def __repr__(self):
        return f"{self.score} : " + self.value

    def __str__(self):
        return self.__repr__()


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

    translators_from: List[Translator]
    translators_to: List[Translator]
    translations_from: List[ITranslation]
    translations_to: List[ITranslation]

    def __init__(self, code: str, name: str):
        self.code = code
        self.name = name
        self.translators_from = list()
        self.translators_to = list()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.code

    def __eq__(self, other):
        return self.code == other.code

    def get_translation(self, to: Language) -> ITranslation | None:
        """Gets a translation from this Language to another Language.

        Args:
            to: The Language to look for a Translation to.

        Returns:
            A valid Translation if there is one in translations_from
                else None.

        """
        for translator_from in self.translators_from:
            translation = translator_from.get_translation(self, to)
            if translation is not None:
                return translation
        return None

        # Pivot through intermediate languages to add translations
        # that don't already exist
        """
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

        # Add identity translations so everything can translate to itself
        for language in languages:
            identity_translation = IdentityTranslation(language)
            language.translations_from.append(identity_translation)
            language.translations_to.append(identity_translation)

        """


class ITranslation:
    """Represents a translation between two Languages

    Attributes:
        from_lang: The Language this Translation translates from.
        to_lang: The Language this Translation translates to.

    """

    from_lang: Language
    to_lang: Language

    def translate(self, from_text: str) -> str:
        """Translates a string from self.from_lang to self.to_lang

        Args:
            from_text: The text to be translated.

        Returns:
            from_text translated.

        """
        translation_result = self.hypotheses(from_text, num_hypotheses=1)[0].value
        info("translation_result", translation_result)
        return translation_result

    def hypotheses(self, from_text: str, num_hypotheses: int = 4) -> list[Hypothesis]:
        """Translates a string from self.from_lang to self.to_lang

        Args:
            from_text: The text to be translated.
            num_hypotheses: Number of hypothetic results expected

        Returns:
            List of translation hypotheses

        """
        raise NotImplementedError()

    def __repr__(self):
        return str(self.from_lang) + " -> " + str(self.to_lang)

    def __str__(self):
        return repr(self).replace("->", "→")


class IdentityTranslation(ITranslation):
    """A Translation that doesn't modify from_text."""

    def __init__(self, lang: Language):
        """Creates an IdentityTranslation.

        Args:
            lang: The Language this Translation translates
                from and to.

        """
        self.from_lang = lang
        self.to_lang = lang

    def hypotheses(self, from_text: str, num_hypotheses: int = 4):
        return [Hypothesis(from_text, 0) for i in range(num_hypotheses)]


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

    def hypotheses(self, from_text: str, num_hypotheses: int = 4) -> list[Hypothesis]:
        t1_hypotheses = self.t1.hypotheses(from_text, num_hypotheses)
        to_return = list()
        for t1_hypothesis in t1_hypotheses:
            t2_hypotheses = self.t2.hypotheses(t1_hypothesis.value, num_hypotheses)
            for t2_hypothesis in t2_hypotheses:
                to_return.append(
                    Hypothesis(
                        t2_hypothesis.value, t1_hypothesis.score + t2_hypothesis.score
                    )
                )
        to_return.sort(reverse=True, key=lambda x: x.score)
        return to_return[0:num_hypotheses]


class RemoteTranslation(ITranslation):
    """A translation provided by a remote LibreTranslate server"""

    from_lang: Language
    to_lang: Language

    def __init__(self, from_lang: Language, to_lang: Language, api):
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.api = api

    def hypotheses(self, from_text: str, num_hypotheses: int = 1) -> list[Hypothesis]:
        """LibreTranslate only supports single hypotheses.

        A list of length num_hypotheses will be returned with identical hypotheses.
        """
        result = self.api.translate(from_text, self.from_lang.code, self.to_lang.code)
        return [Hypothesis(result, 0)] * num_hypotheses


def get_chunk_package(from_code):
    packages = argostranslate.package.get_installed_packages()
    CHUNK_LANG_CODE = "chunk"
    AUTO_LANG_CODE = "auto"
    for package in packages:
        for package_target_language in package.target_languages:
            if package_target_language["code"] == CHUNK_LANG_CODE:
                for package_source_language in package.source_languages:
                    if package_source_language["code"] in [from_code, AUTO_LANG_CODE]:
                        info("get_chunk_package", from_code, package)
                        return package
    info("get_chunk_package", from_code, None)
    return None


def chunk(from_text, from_code):
    if argostranslate.settings.chunk_type == argostranslate.settings.ChunkType.NONE:
        return [from_text]
    elif (
        argostranslate.settings.chunk_type
        == argostranslate.settings.ChunkType.ARGOSTRANSLATE
    ):
        chunk_package = get_chunk_package(from_code)
        if chunk_package is None:
            warning("Could not find chunk package", from_code)
            return [from_text]

        model_path = str(chunk_package.package_path / "model")
        ctranslate2_translator = ctranslate2.Translator(
            model_path, device=argostranslate.settings.device
        )
        sp_model_path = str(chunk_package.package_path / "sentencepiece.model")
        sp_processor = sentencepiece.SentencePieceProcessor(
            model_file=sp_model_path, out_type=str
        )

        def apply_chunk_translation(from_text, ctranslate2_translator, sp_processor):
            MAX_CHUNK_LENGTH = 300  # TODO: make this configurable
            from_text = from_text[:MAX_CHUNK_LENGTH]

            tokenized = sp_processor.encode(from_text)
            translation_results = ctranslate2_translator.translate_batch(
                [tokenized],
            )
            translated_tokens = translation_results[0].hypotheses[0]
            return sp_processor.decode(translated_tokens)

        chunk_translation = functools.partial(
            apply_chunk_translation,
            ctranslate2_translator=ctranslate2_translator,
            sp_processor=sp_processor,
        )

        sentences = argostranslate.chunk.chunk(from_text, chunk_translation)
        info("sentences", sentences)
        return sentences
    else:
        error("Unknown chunk type", argostranslate.settings.chunk_type)
        return [from_text]


class FewShotTranslation(ITranslation):
    """A translation performed with a few shot language model"""

    from_lang: Language
    to_lang: Language
    language_model: argostranslate.models.ILanguageModel

    def __init__(
        self,
        from_lang: Language,
        to_lang: Language,
        language_model: argostranslate.models.ILanguageModel,
    ):
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.language_model = language_model

    def hypotheses(self, from_text: str, num_hypotheses: int = 1) -> list[Hypothesis]:
        # TODO: Split into chunks
        prompt = argostranslate.fewshot.generate_prompt(
            from_text,
            self.from_lang.name,
            self.from_lang.code,
            self.to_lang.name,
            self.to_lang.code,
        )
        info("fewshot prompt", prompt)
        response = self.language_model.infer(prompt)
        info("fewshot response", response)
        if response is None:
            error("fewshot response is None")
            return [Hypothesis("", 0)] * num_hypotheses
        info("fewshot response", response)
        result = argostranslate.fewshot.parse_inference(response)
        info("fewshot result", result)
        return [Hypothesis(result, 0)] * num_hypotheses


class LocalTranslation(ITranslation):
    def __init__(self, translator, from_lang, to_lang):
        self.translator = translator
        self.from_lang = from_lang
        self.to_lang = to_lang

    def hypotheses(self, from_text, num_hypotheses=4):
        return self.translator.translate(
            from_text, self.from_lang.code, self.to_lang.code, num_hypotheses
        )


class Translator:
    def __init__(self, pkg: argostranslate.package.Package):
        # TODO: Cache to prevent memory leaks
        self.pkg = pkg
        self.source_languages = [
            Language(language["code"], language["name"])
            for language in self.pkg.source_languages
        ]
        self.target_languages = [
            Language(language["code"], language["name"])
            for language in self.pkg.target_languages
        ]
        self.model_path = self.pkg.package_path / "model"
        self.translator = ctranslate2.Translator(
            str(self.model_path), device=argostranslate.settings.device
        )
        self.sp_model_path = self.pkg.package_path / "sentencepiece.model"
        self.sp_processor = sentencepiece.SentencePieceProcessor(
            model_file=str(self.sp_model_path)
        )

    def tokenize(self, from_text: str) -> List[str]:
        tokenized = self.sp_processor.encode(from_text, out_type=str)
        info("tokenized", tokenized)
        return tokenized

    def detokenize(self, tokens: List[str]) -> str:
        return self.sp_processor.decode(tokens)

    def remove_target_prefix(self, translated_tokens):
        if self.pkg.target_prefix != "" and self.pkg.target_prefix is not None:
            if translated_tokens[0] == self.pkg.target_prefix:
                return translated_tokens[1:]
        return translated_tokens

    def translate(self, from_text, from_code, to_code, num_hypotheses):
        # Split sentences
        sentences = chunk(from_text, from_code)

        # Tokenize
        tokenized_sentences = [self.tokenize(sentence) for sentence in sentences]

        BATCH_SIZE = 32

        # TODO support BPE

        if self.pkg.target_prefix is not None and self.pkg.target_prefix != "":
            target_prefix = [[self.pkg.target_prefix]] * len(tokenized_sentences)
        else:
            target_prefix = list()

        # Translate
        translation_results = self.translator.translate_batch(
            tokenized_sentences,
            target_prefix=target_prefix,
            replace_unknowns=True,
            max_batch_size=BATCH_SIZE,
            beam_size=max(num_hypotheses, 4),
            num_hypotheses=num_hypotheses,
            length_penalty=0.2,
            return_scores=True,
        )
        info("translation_results", translation_results)

        # Build hypotheses
        hypotheses = list()
        for i in range(num_hypotheses):
            translated_tokens = list()
            cumulative_score = 0
            for translation_result in translation_results:
                translated_tokens += self.remove_target_prefix(
                    translation_result.hypotheses[i]
                )
                cumulative_score += translation_result.scores[i]
            hypothesis_value = self.detokenize(translated_tokens)
            hypothesis_score = cumulative_score / len(translation_results)
            hypothesis = Hypothesis(hypothesis_value, hypothesis_score)
            hypotheses.append(hypothesis)
        info("hypotheses", hypotheses)
        return hypotheses

    def get_translation(self, from_lang, to_lang):
        if from_lang not in self.source_languages:
            return None
        if to_lang not in self.target_languages:
            return None
        return LocalTranslation(self, from_lang, to_lang)


def get_installed_languages() -> list[Language]:
    """Returns a list of Languages installed from packages"""

    if (
        argostranslate.settings.model_provider
        == argostranslate.settings.ModelProvider.OPENNMT
    ):
        packages = argostranslate.package.get_installed_packages()

        packages = list(filter(lambda x: x.type != "chunk", packages))

        # Load languages and translations from packages
        language_of_code = dict()
        for pkg in packages:
            translator = Translator(pkg)
            for source_language in pkg.source_languages:
                if source_language["code"] not in language_of_code:
                    language_of_code[source_language["code"]] = Language(
                        source_language["code"], source_language["name"]
                    )
                    language_of_code[source_language["code"]].translators_from.append(
                        translator
                    )
            for target_language in pkg.target_languages:
                if target_language["code"] not in language_of_code:
                    language_of_code[target_language["code"]] = Language(
                        target_language["code"], target_language["name"]
                    )
                    language_of_code[target_language["code"]].translators_to.append(
                        translator
                    )

        languages = list(language_of_code.values())
    elif (
        argostranslate.settings.model_provider
        == argostranslate.settings.ModelProvider.LIBRETRANSLATE
    ):
        # TODO: Add API key and custom URL support
        libretranslate_api = argostranslate.apis.LibreTranslateAPI()
        supported_languages = (
            libretranslate_api.languages()
        )  # [{"code":"en", "name":"English"}]
        languages = [Language(l["code"], l["name"]) for l in supported_languages]
        for from_lang in languages:
            for to_lang in languages:
                remote_translation = RemoteTranslation(
                    from_lang, to_lang, libretranslate_api
                )
                from_lang.translations_from.append(remote_translation)
                to_lang.translations_to.append(remote_translation)
    elif (
        argostranslate.settings.model_provider
        == argostranslate.settings.ModelProvider.OPENAI
    ):
        language_model = argostranslate.apis.OpenAIAPI(
            argostranslate.settings.openai_api_key
        )
        # TODO
        languages = [Language("en", "English"), Language("es", "Spanish")]
        for from_lang in languages:
            for to_lang in languages:
                few_shot_translation = FewShotTranslation(
                    from_lang, to_lang, language_model
                )
                from_lang.translations_from.append(few_shot_translation)
                to_lang.translations_to.append(few_shot_translation)

    info("languages", languages)

    return languages


def get_language_from_code(code: str) -> Language | None:
    """Gets a language object from a code

    An exception will be thrown if an installed language with this
    code can not be found.

    Args:
        code: The ISO 639 code of the language

    Returns:
        The language object or None if no language is available
    """
    try:
        return next(
            filter(lambda language: language.code == code, get_installed_languages())
        )
    except StopIteration:
        warning(f"Language with code {code} not found")
        return None


def get_translation_from_codes(from_code: str, to_code: str) -> ITranslation | None:
    """Gets a translation object from codes for from and to languages

    An exception will be thrown if an installed translation between the from lang
    and to lang can not be found.

    Args:
        from_code: The ISO 639 code of the source language
        to_code: The ISO 639 code of the target language

    Returns:
        The translation object or None if no translation is available
    """
    from_lang = get_language_from_code(from_code)
    to_lang = get_language_from_code(to_code)
    if from_lang is None or to_lang is None:
        warning(f"Translation from {from_code} to {to_code} not found")
        return None
    return from_lang.get_translation(to_lang)


def translate(q: str, from_code: str, to_code: str) -> str | None:
    """Translate a string of text

    Args:
        q: The text to translate
        from_code: The ISO 639 code of the source language
        to_code: The ISO 639 code of the target language

    Returns:
        The translated text or None if no translation is available
    """
    translation = get_translation_from_codes(from_code, to_code)
    if translation is None:
        warning(
            f"Translation failed - Translation from {from_code} to {to_code} not found"
        )
        return None
    return translation.translate(q)


# TODO: Add translate_json function
