import pytest
from argostranslate import tokenizer as target
import io
import sentencepiece as spm


@pytest.fixture(scope="module")
def tokenizer(tmp_path_factory):
    root = tmp_path_factory.mktemp("spm")
    buffer = io.BytesIO()
    corpus = [
        "user_id file_name snake_case a__b _leading trailing_ ordinary words",
        "x_y_z hello world",
    ] * 20
    spm.SentencePieceTrainer.train(
        sentence_iterator=iter(corpus),
        model_writer=buffer,
        model_type="char",
        vocab_size=100,
        hard_vocab_limit=False,
        character_coverage=1.0,
        minloglevel=2,
    )
    path = root / "tiny.model"
    path.write_bytes(buffer.getvalue())
    return target.SentencePieceTokenizer(path)


@pytest.mark.parametrize(
    "text",
    ["user_id", "file_name", "snake_case", "a__b", "_leading", "trailing_", "x_y_z"],
)
def test_literal_underscores(tokenizer, text):
    tokens = tokenizer.encode(text)
    assert tokenizer.lazy_processor().decode_pieces(tokens) == text
    assert tokenizer.decode(tokens) == text


@pytest.mark.parametrize("text", ["hello world", "ordinary words", "", "user id"])
def test_controls(tokenizer, text):
    assert tokenizer.decode(tokenizer.encode(text)) == text
