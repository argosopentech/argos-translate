from pathlib import Path
from threading import Lock
from typing import List

import sentencepiece as spm


class Tokenizer:
    def encode(self, sentence: str) -> List[str]:
        raise NotImplementedError()

    def decode(self, tokens: List[str]) -> str:
        raise NotImplementedError()


class SentencePieceTokenizer(Tokenizer):
    def __init__(self, model_file: Path):
        self.model_file = model_file
        self.processor = None
        self._init_lock = Lock()

    def lazy_processor(self) -> spm.SentencePieceProcessor:
        if self.processor is None:
            with self._init_lock:
                if self.processor is None:
                    self.processor = spm.SentencePieceProcessor(model_file=str(self.model_file))
        return self.processor

    def encode(self, sentence: str) -> List[str]:
        tokens = self.lazy_processor().encode(sentence, out_type=str)
        return tokens

    def decode(self, tokens: List[str]) -> str:
        """
        # Returns not decoded byte-fallback tokens, quite detrimental to Asian languages translations
        detokenized = "".join(tokens)
        return detokenized.replace("▁", " ")
        """
        # Replace the SentencePiece space marker while preserving literal underscores.
        return (
            self.lazy_processor()
            .decode_pieces(tokens)
            .replace("▁", " ")
        )


class BPETokenizer(Tokenizer):
    def __init__(self, model_file: Path, from_code: str, to_code: str):
        self.model_file = model_file
        self.from_code = from_code
        self.to_code = to_code
        self.tokenizer = None
        self.detokenizer = None
        self.bpe_source = None
        self.normalizer = None
        self._init_lock = Lock()

    def lazy_load(self):
        if self.tokenizer is None:
            with self._init_lock:
                if self.tokenizer is not None:
                    return
                from sacremoses.normalize import MosesPunctNormalizer
                from sacremoses.tokenize import MosesDetokenizer, MosesTokenizer
                from argostranslate.apply_bpe import BPE

                tokenizer = MosesTokenizer(self.from_code)
                detokenizer = MosesDetokenizer(self.to_code)
                normalizer = MosesPunctNormalizer(self.from_code)
                with open(str(self.model_file), "r", encoding="utf-8") as f:
                    bpe_source = BPE(f)

                self.detokenizer = detokenizer
                self.normalizer = normalizer
                self.bpe_source = bpe_source
                # Publish the ready marker only after every dependency is loaded.
                self.tokenizer = tokenizer

    def encode(self, sentence: str) -> List[str]:
        self.lazy_load()

        normalized = self.normalizer.normalize(sentence)
        tokenized = " ".join(self.tokenizer.tokenize(normalized))
        segmented = self.bpe_source.segment_tokens(tokenized.strip("\r\n ").split(" "))

        return segmented

    def decode(self, tokens: List[str]) -> str:
        self.lazy_load()

        return self.detokenizer.detokenize(
            " ".join(tokens).replace("@@ ", "").split(" ")
        )
