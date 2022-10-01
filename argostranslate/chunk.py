from argostranslate.utils import info


def chunk(q: str, chunk_translation):
    info("applied_chunk_translation", chunk_translation(q))
    to_return = list()
    to_return.append(q)
    return to_return
