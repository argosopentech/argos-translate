from __future__ import annotations

from difflib import SequenceMatcher
from typing import List

import spacy
import stanza

from argostranslate import package, settings
from argostranslate.networking import cache_spacy
from argostranslate.package import Package
from argostranslate.utils import info, warning


def get_stanza_processors(lang_code: str, resources: dict) -> str:
    """Get appropriate processors for a language, including MWT if available."""
    try:
        return "tokenize,mwt" if resources[lang_code].get("mwt") else "tokenize"
    except (KeyError, TypeError):
        return "tokenize"


# Cache SpaCy model once at module level
_cached_spacy_path: str | None = cache_spacy()


class ISentenceBoundaryDetectionModel:
    # https://github.com/argosopentech/sbd/blob/main/main.py
    pkg: Package

    def split_sentences(self, text: str) -> List[str]:
        raise NotImplementedError


# Spacy sentence boundary detection Sentencizer
# https://community.libretranslate.com/t/sentence-boundary-detection-for-machine-translation/606/3
# https://spacy.io/usage/linguistic-features/#sbd
# Download model:
# python -m spacy download xx_sent_ud_sm
class SpacySentencizerSmall(ISentenceBoundaryDetectionModel):
    def __init__(self, pkg: Package):
        """
        Packaging specific spacy when "xx_sent_ud_sm" doesn't cover the language improves performances over stanza.
        Please use small models ".._core/web_sm" for consistency.
        """
        self.pkg = pkg
        if pkg.packaged_sbd_path is not None and "spacy" in str(pkg.packaged_sbd_path):
            self.nlp = spacy.load(pkg.packaged_sbd_path, exclude=["parser"])
        # Case sbd is not packaged, use cached Spacy multilingual (xx_ud_sent_sm)
        else:
            if _cached_spacy_path is None:
                raise RuntimeError("SpaCy cache not initialized")
            self.nlp = spacy.load(_cached_spacy_path, exclude=["parser"])
        self.nlp.add_pipe("sentencizer")

    def split_sentences(self, text: str) -> List[str]:
        info(f"Splitting sentences using SBD Model: ({self.pkg.from_code}) {str(self)}")
        doc = self.nlp(text)
        return [sent.text for sent in doc.sents]

    def __str__(self):
        return "Using Spacy model."


class StanzaSentencizer(ISentenceBoundaryDetectionModel):
    LANGUAGE_CODE_MAPPING = {
        "zt": "zh-hant",
        "pb": "pt",
    }

    def _init_spacy_fallback(self):
        """Initialize SpaCy fallback using cached multilingual model."""
        if _cached_spacy_path is None:
            raise RuntimeError("SpaCy cache not initialized")
        self.nlp = spacy.load(_cached_spacy_path, exclude=["parser"])
        self.nlp.add_pipe("sentencizer")

    def __init__(self, pkg: Package):
        self.pkg = pkg
        try:
            stanza_lang_code = self.LANGUAGE_CODE_MAPPING.get(
                pkg.from_code, pkg.from_code
            )

            try:
                resources = stanza.resources.common.load_resources_json()
            except Exception:
                warning(f"Could not load Stanza resources for package {str(pkg)}")
                resources = {}

            self.stanza_pipeline = stanza.Pipeline(
                lang=stanza_lang_code,
                processors=get_stanza_processors(stanza_lang_code, resources),
                use_gpu=settings.device == "cuda",
                logging_level="WARNING",
                tokenize_pretokenized=False,
                download_method=stanza.DownloadMethod.REUSE_RESOURCES,
            )
            self.fallback_to_spacy = False
        except Exception as e:
            info(f"Stanza pipeline failed for language '{pkg.from_code}': {e}")
            info(
                f"Falling back to SpaCy sentence boundary detection for {pkg.from_code}"
            )
            self.stanza_pipeline = None
            self.fallback_to_spacy = True
            self._init_spacy_fallback()

    def split_sentences(self, text: str) -> List[str]:
        # TODO do Spacy SBD using a SpacySentencizerSmall object instead of duplicating code
        info(f"Splitting sentences using SBD Model: ({self.pkg.from_code}) {str(self)}")
        if self.fallback_to_spacy:
            doc = self.nlp(text)
            return [sent.text for sent in doc.sents]
        else:
            doc = self.stanza_pipeline(text)
            return [sent.text for sent in doc.sentences]

    def __str__(self):
        if self.fallback_to_spacy:
            return "StanzaSentencizer falling back to Spacy "
        else:
            return "StanzaSentencizer"


###############################################
#### Few Shot Sentence Boundary Detection ####
###############################################

# The Few Shot SBD code mostly isn't used currently

fewshot_prompt = """<detect-sentence-boundaries> I walked down to the river. Then I went to the
I walked down to the river. <sentence-boundary>
----------
<detect-sentence-boundaries> Argos Translate is machine translation software. It is also
Argos Translate is machine translation software. <sentence-boundary>
----------
<detect-sentence-boundaries> Argos Translate is written in Python and uses OpenAI. It also supports
Argos Translate is written in Python and uses OpenAI. <sentence-boundary>
----------
"""

DETECT_SENTENCE_BOUNDARIES_TOKEN = "<detect-sentence-boundaries>"
SENTENCE_BOUNDARY_TOKEN = "<sentence-boundary>"
FEWSHOT_BOUNDARY_TOKEN = "-" * 10


def get_sbd_package() -> Package | None:
    packages = package.get_installed_packages()
    for pkg in packages:
        if pkg.type == "sbd":
            return pkg
    return None


def generate_fewshot_sbd_prompt(
    input_text: str, sentence_guess_length: int = 150
) -> str:
    sentence_guess = input_text[:sentence_guess_length]
    to_return = fewshot_prompt + "<detect-sentence-boundaries> " + sentence_guess
    info("generate_fewshot_sbd_prompt", to_return)
    return to_return


def parse_fewshot_response(response_text: str) -> str | None:
    response = response_text.split(FEWSHOT_BOUNDARY_TOKEN)
    info("parse_fewshot_response", response)
    if len(response) < 2:
        return None
    response = response[-2].split("\n")
    if len(response) < 2:
        return None
    return response[-1]


def process_seq2seq_sbd(input_text: str, sbd_translated_guess: str) -> int:
    sbd_translated_guess_index = sbd_translated_guess.find(SENTENCE_BOUNDARY_TOKEN)
    if sbd_translated_guess_index != -1:
        sbd_translated_guess = sbd_translated_guess[:sbd_translated_guess_index]
        info("sbd_translated_guess:", sbd_translated_guess)
        best_index = 0
        best_ratio = 0.0
        for i in range(len(input_text)):
            candidate_sentence = input_text[:i]
            sm = SequenceMatcher()
            sm.set_seqs(candidate_sentence, sbd_translated_guess)
            ratio = sm.ratio()
            if i == 0 or ratio > best_ratio:
                best_index = i
                best_ratio = ratio
        return best_index
    else:
        return -1


def detect_sentence(
    input_text: str, sbd_translation, sentence_guess_length: int = 150
) -> int:
    """Given input text, return the index after the end of the first sentence.

    Args:
        input_text: The text to detect the first sentence of.
        sbd_translation: An ITranslation for detecting sentences.
        sentence_guess_length: Estimated number of chars > than most sentences.

    Returns:
        The index of the character after the end of the sentence.
                -1 if not found.
    """
    # TODO: Cache
    sentence_guess = input_text[:sentence_guess_length]
    info("sentence_guess:", sentence_guess)
    sbd_translated_guess = sbd_translation.translate(
        DETECT_SENTENCE_BOUNDARIES_TOKEN + sentence_guess
    )
    return process_seq2seq_sbd(input_text, sbd_translated_guess)
