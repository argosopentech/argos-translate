from pathlib import Path
from types import SimpleNamespace

import pytest

from argostranslate.tokenizer import SentencePieceTokenizer


@pytest.mark.parametrize("text", ["user_name@example.com", "some_file.py", "snake_case", "plain text"])
def test_sentencepiece_preserves_literal_underscores(text):
    tokenizer = SentencePieceTokenizer(Path("unused.model"))
    tokenizer.processor = SimpleNamespace(decode_pieces=lambda tokens: text)
    assert tokenizer.decode([]) == text
