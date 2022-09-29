import logging

import ctranslate2
import sentencepiece as spm
import stanza

from argostranslate import package, settings, models, apis, fewshot, chunk
from argostranslate.utils import info, error


class Hypothesis:
    """Represents a translation hypothesis

    Attributes:
        value (str): The hypothetical translation value
        score (float): The score representing the quality of the translation
    """

    def __init__(self, value, score):
        self.value = value
        self.score = score

    def __lt__(self, other):
        return self.score < other.score

    def __repr__(self):
        return f"({repr(self.value)}, {self.score})"

    def __str__(self):
        return repr(self)


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
        return self.hypotheses(input_text, num_hypotheses=1)[0].value

    def hypotheses(self, input_text, num_hypotheses=4):
        """Translates a string from self.from_lang to self.to_lang

        Args:
            input_text (str): The text to be translated.
            num_hypotheses (int): Number of hypothetic results expected

        Returns:
            [Hypothesis]: List of translation hypotheses

        """
        raise NotImplementedError()

    def __repr__(self):
        return str(self.from_lang) + " -> " + str(self.to_lang)

    def __str__(self):
        return repr(self).replace("->", "→")


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
        self.translators_from = list()
        self.translators_to = list()

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.code == other.code

    def get_translation(self, to):
        """Gets a translation from this Language to another Language.

        Args:
            to (Language): The Language to look for a Translation to.

        Returns:
            ITranslation: A valid Translation if there is one in translations_from
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

    def hypotheses(self, input_text, num_hypotheses):
        return [Hypothesis(input_text, 0) for i in range(num_hypotheses)]


class CompositeTranslation(ITranslation):
    """A ITranslation that is performed by chaining two Translations

    Attributes:
        t1 (ITranslation): The first Translation to apply.
        t2 (ITranslation): The second Translation to apply.

    """

    def __init__(self, t1, t2):
        """Creates a CompositeTranslation.

        Args:
            t1 (ITranslation): The first Translation to apply.
            t2 (ITranslation): The second Translation to apply.

        """
        self.t1 = t1
        self.t2 = t2
        self.from_lang = t1.from_lang
        self.to_lang = t2.to_lang

    def hypotheses(self, input_text, num_hypotheses):
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
        to_return.sort()
        return to_return[0:num_hypotheses]


class RemoteTranslation(ITranslation):
    """A translation provided by a remote LibreTranslate server"""

    def __init__(self, from_lang, to_lang, api):
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.api = api

    def hypotheses(self, input_text, num_hypotheses=1):
        """LibreTranslate only supports single hypotheses.

        A list of length num_hypotheses will be returned with identical hypotheses.
        """
        result = self.api.translate(input_text, self.from_lang.code, self.to_lang.code)
        return [Hypothesis(result, 0)] * num_hypotheses


class FewShotTranslation(ITranslation):
    """A translation performed with a few shot language model"""

    def __init__(self, from_lang, to_lang, language_model):
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.language_model = language_model

    def hypotheses(self, input_text, num_hypotheses=1):
        sentences = chunk.chunk(input_text)

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


def apply_packaged_translation(pkg, input_text, translator, num_hypotheses=4):
    """Applies the translation in pkg to translate input_text.

    Args:
        pkg (Package): The package that provides the translation.
        input_text (str): The text to be translated.
        translator (ctranslate2.Translator): The CTranslate2 Translator
        num_hypotheses (int): The number of hypotheses to generate

    Returns:
        [Hypothesis]: A list of Hypotheses for translating input_text

    """

    info("apply_packaged_translation", input_text)

    # Translation
    info("translated_batches", translated_batches)


# TODO: Rename "LocalTranslation"?
class PackageTranslation(ITranslation):
    """A Translation that is installed with a package"""

    def __init__(self, pkg):
        self.pkg = pkg
        self.translator = None

    def hypotheses(self, input_text, num_hypotheses):
        if self.translator is None:
            model_path = str(self.pkg.package_path / "model")
            self.translator = ctranslate2.Translator(model_path, device=settings.device)
        return apply_packaged_translation(
            self.pkg, input_text, self.translator, num_hypotheses
        )


class LocalTranslation(ITranslation):
    def __init__(self, translator, from_lang, to_lang):
        self.translator = translator
        self.from_lang = from_lang
        self.to_lang = to_lang

    def hypotheses(self, input_text, num_hypotheses=4):
        return self.translator.translate(
            input_text, self.from_lang.code, self.to_lang.code, num_hypotheses
        )


class Translator:
    def __init__(self, pkg):
        self.pkg = pkg
        self.source_languages = [
            Language(language["code"], language["name"])
            for language in self.pkg.source_languages
        ]
        self.target_languages = [
            Language(language["code"], language["name"])
            for language in self.pkg.target_languages
        ]
        model_path = str(self.pkg.package_path / "model")
        self.translator = ctranslate2.Translator(model_path, device=settings.device)
        sp_model_path = str(self.pkg.package_path / "sentencepiece.model")
        self.sp_processor = spm.SentencePieceProcessor(model_file=sp_model_path)

    def chunk(self, input_text):
        # Sentence boundary detection chunking
        sentences = chunk.chunk(input_text, lambda x: x)
        info("sentences", sentences)
        return sentences

    def tokenize(self, input_text):
        tokenized = self.sp_processor.encode(input_text, out_type=str)
        info("tokenized", tokenized)
        return tokenized

    def detokenize(self, tokens):
        return self.sp_processor.decode(tokens)

    def add_source_prefix(self, tokenized_sentence, from_code):
        source_code_token = f"__{from_code}__"
        return [source_code_token] + tokenized_sentence

    def remove_target_prefix(self, translated_tokens, target_code_token):
        if translated_tokens[0] == target_code_token:
            return translated_tokens[1:]
        else:
            return translated_tokens

    def translate(self, input_text, from_code, to_code, num_hypotheses):
        # Split sentences
        sentences = self.chunk(input_text)

        # Tokenize
        tokenized_sentences = [self.tokenize(sentence) for sentence in sentences]

        # Add source prefix
        target_code_token = f"__{to_code}__"
        tokenized_sentences = [
            self.add_source_prefix(tokenized_sentence, from_code)
            for tokenized_sentence in tokenized_sentences
        ]

        # Translate
        translation_results = self.translator.translate_batch(
            tokenized_sentences,
            target_prefix=[[target_code_token]] * len(tokenized_sentences),
            replace_unknowns=True,
            max_batch_size=2024,
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
                translated_tokens += translation_result.hypotheses[i]
                translated_tokens = self.remove_target_prefix(
                    translated_tokens, target_code_token
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


def get_installed_languages():
    """Returns a list of Languages installed from packages"""

    info("get_installed_languages")

    if settings.model_provider == settings.ModelProvider.OPENNMT:
        packages = package.get_installed_packages()

        # Filter for translate packages
        packages = list(filter(lambda x: x.type == "translate", packages))

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

    elif settings.model_provider == settings.ModelProvider.LIBRETRANSLATE:
        # TODO: Add API key and custom URL support
        libretranslate_api = apis.LibreTranslateAPI()
        supported_languages = (
            libretranslate_api.languages()
        )  # [{"code":"en", "name":"English"}]
        languages = [Language(l["code"], l["name"]) for l in supported_languages]
        for from_lang in languages:
            for to_lang in languages:
                translation = REMOTE(from_lang, to_lang, libretranslate_api)
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


def get_language_from_code(code):
    """Gets a language object from a code

    An exception will be thrown if an installed language with this
    code can not be found.

    Args:
        code (str): The ISO 639 code of the language

    Returns:
        translate.Language: The language object
    """
    return list(filter(lambda x: x.code == code, get_installed_languages()))[0]


def get_translation_from_codes(from_code, to_code):
    """Gets a translation object from codes for from and to languages

    An exception will be thrown if an installed translation between the from lang
    and to lang can not be found.

    Args:
        from_code (str): The ISO 639 code of the source language
        to_code (str): The ISO 639 code of the target language

    Returns:
        translate.ITranslation: The translation object
    """
    from_lang = get_language_from_code(from_code)
    to_lang = get_language_from_code(to_code)
    return from_lang.get_translation(to_lang)


def translate(q, from_code, to_code):
    """Translate a string of text

    Args:
        q (str): The text to translate
        from_code (str): The ISO 639 code of the source language
        to_code (str): The ISO 639 code of the target language

    Returns:
        str: The translated text
    """
    translation = get_translation_from_codes(from_code, to_code)
    return translation.translate(q)


# TODO: Add translate_json function
