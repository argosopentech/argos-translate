import pathlib
import unittest.mock

import argostranslate.translate


class TestTranslate:
    def test_Hypothesis(self):
        hypothesis7 = argostranslate.translate.Hypothesis("7", -0.9)
        hypothesis7b = argostranslate.translate.Hypothesis("7", -0.9)
        hypothesis9 = argostranslate.translate.Hypothesis("9", -1.5)

        assert hypothesis9 < hypothesis7
        assert hypothesis7 > hypothesis9
        assert hypothesis9 != hypothesis7
        assert hypothesis7 == hypothesis7b

        assert repr(hypothesis7) == "-0.9 : 7"
        assert str(hypothesis7) == "-0.9 : 7"

    def get_mock_English(self):
        return argostranslate.translate.Language("en", "English")

    def get_mock_Spanish(self):
        return argostranslate.translate.Language("es", "Spanish")

    def get_French(self):
        return argostranslate.translate.Language("fr", "French")

    def test_Language(self):
        en = self.get_mock_English()
        assert en.code == "en"
        assert en.name == "English"
        assert str(en) == "English"
        assert repr(en) == "en"

    def test_IdentityTranslation(self):
        en = self.get_mock_English()
        i = argostranslate.translate.IdentityTranslation(en)
        assert i.translate("Hello World") == "Hello World"
        h = i.hypotheses("Hello World")[0]
        assert h.value == "Hello World"
        assert h.score == 0

    def build_mock_translation(self, translation_dict, from_lang, to_lang):
        translation = argostranslate.translate.ITranslation()

        def mock_hypotheses(input_text: str, num_hypotheses: int = 1, **kwargs):
            return [
                argostranslate.translate.Hypothesis(translation_dict[input_text], -0.3)
            ]

        translation.hypotheses = mock_hypotheses
        translation.from_lang = from_lang
        translation.to_lang = to_lang

        return translation

    def get_translation_en_es(self):
        translation_dict = {
            "Hello World": "Hola Mundo",
        }
        translation_en_es = self.build_mock_translation(
            translation_dict, self.get_mock_English(), self.get_mock_Spanish()
        )
        return translation_en_es

    def get_translation_es_en(self):
        translation_dict = {
            "Hola Mundo": "Hello World",
        }
        translation_en_es = self.build_mock_translation(
            translation_dict, self.get_mock_English(), self.get_mock_Spanish()
        )
        return translation_en_es

    def get_translation_en_fr(self):
        translation_dict = {
            "Hello World": "Bonjour le monde",
        }
        translation_en_fr = self.build_mock_translation(
            translation_dict, self.get_mock_English(), self.get_French()
        )
        return translation_en_fr

    def test_CompositeTranslation(self):
        translation_es_en = self.get_translation_es_en()
        translation_en_fr = self.get_translation_en_fr()
        composite_translation = argostranslate.translate.CompositeTranslation(
            translation_es_en, translation_en_fr
        )
        assert composite_translation.translate("Hola Mundo") == "Bonjour le monde"

    def get_mock_Package(self):
        """Create a mock argostranslate.package.Package"""
        package = unittest.mock.Mock(spec=argostranslate.package.Package)
        package.package_path = pathlib.Path("test_package_path")
        package.source_languages = [{"code": "en", "name": "English"}]
        package.target_languages = [{"code": "es", "name": "Spanish"}]
        return package

    @unittest.mock.patch("argostranslate.settings.device", "cuda")
    @unittest.mock.patch("sentencepiece.SentencePieceProcessor")
    @unittest.mock.patch("ctranslate2.Translator")
    def test_Translator__init__(
        self,
        mock_ctranslate2_Translator,
        mock_sentencepiece_SentencePieceProcessor,
    ):
        translator = argostranslate.translate.Translator(self.get_mock_Package())
        assert translator.pkg.package_path == pathlib.Path("test_package_path")
        assert translator.source_languages == [self.get_mock_English()]
        assert translator.target_languages == [self.get_mock_Spanish()]
        model_path = pathlib.Path("test_package_path/model")
        assert translator.model_path == model_path
        assert mock_ctranslate2_Translator.call_count == 1
        mock_ctranslate2_Translator.assert_called_with(str(model_path), device="cuda")
        sp_model_path = pathlib.Path("test_package_path/sentencepiece.model")
        assert translator.sp_model_path == sp_model_path
        mock_sentencepiece_SentencePieceProcessor.assert_called_with(
            model_file=str(sp_model_path)
        )

    @unittest.mock.patch("argostranslate.settings.device", "cuda")
    @unittest.mock.patch("sentencepiece.SentencePieceProcessor")
    @unittest.mock.patch("ctranslate2.Translator")
    def test_Translator_tokenize(
        self,
        mock_ctranslate2_Translator,
        mock_sentencepiece_SentencePieceProcessor,
    ):
        translator = argostranslate.translate.Translator(self.get_mock_Package())
        translator.sp_processor = unittest.mock.Mock()
        translator.sp_processor.encode.return_value = ["Hello", "_World"]
        assert translator.tokenize("Hello World") == ["Hello", "_World"]
        translator.sp_processor.encode.assert_called_with("Hello World", out_type=str)

    @unittest.mock.patch("argostranslate.settings.device", "cuda")
    @unittest.mock.patch("sentencepiece.SentencePieceProcessor")
    @unittest.mock.patch("ctranslate2.Translator")
    def test_Translator_detokenize(
        self,
        mock_ctranslate2_Translator,
        mock_sentencepiece_SentencePieceProcessor,
    ):
        translator = argostranslate.translate.Translator(self.get_mock_Package())
        translator.sp_processor = unittest.mock.Mock()
        translator.sp_processor.decode.return_value = ["Hello World"]
        assert translator.detokenize(["Hello", "_World"]) == ["Hello World"]
        translator.sp_processor.decode.assert_called_with(["Hello", "_World"])


class TestChunk:
    chunk_text = (
        "This is the first sentence. This is the second sentence in this statement. "
    )

    @unittest.mock.patch(
        "argostranslate.settings.chunk_type", argostranslate.settings.ChunkType.NONE
    )
    def test_chunk_none(self):
        assert argostranslate.translate.chunk(self.chunk_text, "en") == [
            self.chunk_text
        ]
