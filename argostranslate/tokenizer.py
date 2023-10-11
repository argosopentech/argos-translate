import sentencepiece as spm
from pathlib import Path


class Tokenizer:
    def encode(self, sentence: str) -> list[str]:
        raise NotImplementedError()
    
    def decode(self, tokens: list[str]) -> str:
        raise NotImplementedError()

class SentencePieceTokenizer(Tokenizer):
    def __init__(self, model_file: Path):
        self.model_file = model_file
        self.processor = None

    def lazy_processor(self) -> spm.SentencePieceProcessor:
        if self.processor is None:
            self.processor = spm.SentencePieceProcessor(model_file=str(self.model_file))
        return self.processor

    def encode(self, sentence: str) -> list[str]:
        tokens = self.lazy_processor().encode(sentence, out_type=str)
        return tokens

    def decode(self, tokens: list[str]) -> str:
        detokenized = "".join(tokens)
        return detokenized.replace("▁", " ")


class BPETokenizer(Tokenizer):
    def __init__(self, model_file: Path, from_code: str, to_code: str):
        self.model_file = model_file
        self.from_code = from_code
        self.to_code = to_code
        self.tokenizer = None
        self.detokenizer = None
        self.bpe_source = None

    def lazy_load(self):
        if self.tokenizer is None:
            from sacremoses.tokenize import MosesTokenizer, MosesDetokenizer
            from sacremoses.normalize import MosesPunctNormalizer

            self.tokenizer = MosesTokenizer(self.from_code)
            self.detokenizer = MosesDetokenizer(self.to_code)
            self.normalizer = MosesPunctNormalizer(self.from_code)

            from argostranslate.apply_bpe import BPE
            with open(str(self.model_file), "r", encoding="utf-8") as f:
                self.bpe_source = BPE(f)

    def encode(self, sentence: str) -> list[str]:
        self.lazy_load()

        normalized = self.normalizer.normalize(sentence)
        tokenized = ' '.join(self.tokenizer.tokenize(normalized))
        segmented = self.bpe_source.segment_tokens(tokenized.strip('\r\n ').split(' '))
        return segmented
    
    def decode(self, tokens: list[str]) -> str:
        self.lazy_load()
        
        for i in range(len(tokens)):
            tokens[i] = tokens[i].replace('@@', '')
        return self.detokenizer.detokenize(tokens)
