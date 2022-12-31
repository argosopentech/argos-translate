from difflib import SequenceMatcher

from argostranslate.utils import info


def chunk(q: str, chunk_translation):
    unchunked_input = q
    sentences = list()
    while len(unchunked_input.strip()) > 0:
        translated_chunk = chunk_translation(unchunked_input)
        info("applied_chunk_translation", translated_chunk)

        # Try to find translated_chunk as a substring of unchunked_input
        # TODO: Would binary search be meaningfully faster?
        best_substring_index = len(unchunked_input)
        best_substring_score = 0.5
        for i in range(len(translated_chunk) * 2):
            if i > len(unchunked_input):
                break
            canidate_unchunked_substring = unchunked_input[:i]
            sm = SequenceMatcher()
            sm.set_seqs(canidate_unchunked_substring, translated_chunk)
            score = sm.ratio()
            if best_substring_score is None or score > best_substring_score:
                best_substring_index = i
                best_substring_score = score

        if best_substring_index is not None:
            sentences.append(unchunked_input[:best_substring_index])
            unchunked_input = unchunked_input[best_substring_index:]
        else:
            sentences.append(unchunked_input)
            unchunked_input = ""

    info("chunked_sentences", sentences)
    return sentences
