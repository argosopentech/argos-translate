from difflib import SequenceMatcher

from argostranslate import package, settings
from argostranslate.utils import info, error

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


def get_sbd_package():
    packages = package.get_installed_packages()
    for pkg in packages:
        if pkg.type == "sbd":
            return pkg
    return None


def generate_fewshot_sbd_prompt(input_text, sentence_guess_length=150):
    sentence_guess = input_text[:sentence_guess_length]
    to_return = fewshot_prompt + "<detect-sentence-boundaries> " + sentence_guess
    info("generate_fewshot_sbd_prompt", to_return)
    return to_return


def parse_fewshot_response(response_text):
    response = response_text.split(FEWSHOT_BOUNDARY_TOKEN)
    info("parse_fewshot_response", response)
    if len(response) < 2:
        return None
    response = response[-2].split("\n")
    if len(response) < 2:
        return None
    return response[-1]


def process_seq2seq_sbd(input_text, sbd_translated_guess):
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


def detect_sentence(input_text, sbd_translation, sentence_guess_length=150):
    """Given input text, return the index after the end of the first sentence.

    Args:
        input_text (str): The text to detect the first sentence of.
        sbd_translation (translate.ITranslation): An ITranslation for detecting sentences.
        sentence_guess_length (int): Estimated number of chars > than most sentences.

    Returns:
        int: The index of the character after the end of the sentence.
                -1 if not found.
    """
    # TODO: Cache
    sentence_guess = input_text[:sentence_guess_length]
    info("sentence_guess:", sentence_guess)
    sbd_translated_guess = sbd_translation.translate(
        DETECT_SENTENCE_BOUNDARIES_TOKEN + sentence_guess
    )
    return process_seq2seq_sbd(input_text, sbd_translated_guess)
