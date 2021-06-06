import logging

from difflib import SequenceMatcher

import ctranslate2
import sentencepiece as spm
import stanza

from argostranslate import package, settings
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

    @staticmethod
    def split_into_paragraphs(input_text):
        """Splits input_text into paragraphs and returns a list of paragraphs.

        Args:
            input_text (str): The text to be split.

        Returns:
            [str]: A list of paragraphs.

        """
        return input_text.split("\n")

    @staticmethod
    def combine_paragraphs(paragraphs):
        """Combines a list of paragraphs together.

        Args:
            paragraphs ([str]): A list of paragraphs.

        Returns:
            [str]: list of n paragraphs combined into one string.

        """
        return "\n".join(paragraphs)

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
        valid_translations = list(
            filter(lambda x: x.to_lang.code == to.code, self.translations_from)
        )
        if len(valid_translations) > 0:
            return valid_translations[0]
        return None


class PackageTranslation(ITranslation):
    """Translation from a package"""

    def __init__(self, from_lang, to_lang, pkg):
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.pkg = pkg
        self.translator = None

    def hypotheses(self, input_text, num_hypotheses):
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
            underlying (ITranslation): The underlying translation to cache.

        """
        self.underlying = underlying
        self.from_lang = underlying.from_lang
        self.to_lang = underlying.to_lang
        self.cache = dict()

    def hypotheses(self, input_text, num_hypotheses=4):
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


DETECT_SENTENCE_BOUNDARIES_TOKEN = "<detect-sentence-boundaries>"
SENTENCE_BOUNDARY_TOKEN = "<sentence-boundary>"


def detect_sentence(input_text, sentence_guess_length=150):
    """Given input text, return the index after the end of the first sentence.

    Args:
        input_text (str): The text to detect the first sentence of.
        sentence_guess_length (int): Estimated number of chars > than most sentences.

    Returns:
        int: The index of the character after the end of the sentence.
                -1 if not found.
    """
    # TODO: Cache
    sbd_translation = get_sbd_translation()
    sentence_guess = input_text[:sentence_guess_length]
    info("sentence_guess:", sentence_guess)
    sbd_translated_guess = sbd_translation.translate(
        DETECT_SENTENCE_BOUNDARIES_TOKEN + sentence_guess
    )
    sbd_translated_guess_index = sbd_translated_guess.find(SENTENCE_BOUNDARY_TOKEN)
    if sbd_translated_guess_index != -1:
        sbd_translated_guess = sbd_translated_guess[:sbd_translated_guess_index]
        info("sbd_translated_guess:", sbd_translated_guess)
        best_index = None
        best_ratio = 0.0
        for i in range(len(input_text)):
            candidate_sentence = input_text[:i]
            sm = SequenceMatcher()
            sm.set_seqs(candidate_sentence, sbd_translated_guess)
            ratio = sm.ratio()
            if best_index is None or ratio > best_ratio:
                best_index = i
                best_ratio = ratio
        return best_index
    else:
        return -1


def apply_packaged_translation(pkg, input_text, translator, num_hypotheses=4):
    """Applies the translation in pkg to translate input_text.

    Args:
        pkg (Package): The package that provides the translation.
        input_text (str): The text to be translated.
        translator (ctranslate2.Translator): The CTranslate2 Translator
        num_hypotheses (int): The number of hypotheses to generate

    Returns:
        [Hypothesis]: A list of Hypothesis's for translating input_text

    """

    info("apply_packaged_translation")

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
        while start_index < len(input_text) - 1:
            detected_sentence_index = detect_sentence(input_text[start_index:])
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
    info("sentences:", sentences)

    # Tokenization
    sp_model_path = str(pkg.package_path / "sentencepiece.model")
    sp_processor = spm.SentencePieceProcessor(model_file=sp_model_path)
    tokenized = [sp_processor.encode(sentence, out_type=str) for sentence in sentences]
    info("tokenized:", tokenized)

    # Translation
    BATCH_SIZE = 32
    translated_batches = translator.translate_batch(
        tokenized,
        replace_unknowns=True,
        max_batch_size=BATCH_SIZE,
        beam_size=max(num_hypotheses, 4),
        num_hypotheses=num_hypotheses,
        length_penalty=0.2,
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


def get_installed_languages():
    """Returns a list of Languages installed from packages"""

    info("get_installed_languages")

    packages = package.get_installed_packages()

    # If stanza not available filter for sbd available
    if not settings.stanza_available:
        sbd_packages = list(filter(lambda x: x.type == "sbd", packages))
        sbd_available_codes = set()
        for sbd_package in sbd_packages:
            sbd_available_codes = sbd_available_codes.union(sbd_package.from_codes)
        packages = list(filter(lambda x: x.from_code in sbd_available_codes, packages))

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
        translation_to_add = CachedTranslation(
            PackageTranslation(from_lang, to_lang, pkg)
        )
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


def get_sbd_translation():
    packages = package.get_installed_packages()
    for pkg in packages:
        if pkg.type == "sbd":
            return PackageTranslation(None, None, pkg)
    return None


def load_installed_languages():
    """Deprecated 1.2, use get_installed_languages"""
    return get_installed_languages()
