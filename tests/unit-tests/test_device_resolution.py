import pathlib
import unittest.mock

import argostranslate.package
import argostranslate.settings
import argostranslate.translate


class TestResolveDevice:
    def test_passthrough_cpu(self):
        assert argostranslate.translate._resolve_device("cpu") == "cpu"

    def test_passthrough_cuda(self):
        assert argostranslate.translate._resolve_device("cuda") == "cuda"

    def test_passthrough_mps(self):
        assert argostranslate.translate._resolve_device("mps") == "mps"

    def test_auto_selects_cuda_first(self):
        def compute_types(device):
            if device == "cuda":
                return {"float32", "int8"}
            raise RuntimeError("device not available")

        with unittest.mock.patch(
            "ctranslate2.get_supported_compute_types", side_effect=compute_types
        ):
            assert argostranslate.translate._resolve_device("auto") == "cuda"

    def test_auto_selects_mps_when_cuda_unavailable(self):
        def compute_types(device):
            if device == "cuda":
                raise RuntimeError("CUDA not available")
            if device == "mps":
                return {"float32"}
            raise RuntimeError("device not available")

        with unittest.mock.patch(
            "ctranslate2.get_supported_compute_types", side_effect=compute_types
        ):
            assert argostranslate.translate._resolve_device("auto") == "mps"

    def test_auto_falls_back_to_cpu_when_no_gpu(self):
        with unittest.mock.patch(
            "ctranslate2.get_supported_compute_types",
            side_effect=RuntimeError("no GPU"),
        ):
            assert argostranslate.translate._resolve_device("auto") == "cpu"

    def test_auto_falls_back_to_cpu_when_empty_compute_types(self):
        with unittest.mock.patch(
            "ctranslate2.get_supported_compute_types", return_value=set()
        ):
            assert argostranslate.translate._resolve_device("auto") == "cpu"


class TestTranslatorDevice:
    def get_mock_package(self):
        package = unittest.mock.Mock(spec=argostranslate.package.Package)
        package.package_path = pathlib.Path("test_package_path")
        package.source_languages = [{"code": "en", "name": "English"}]
        package.target_languages = [{"code": "es", "name": "Spanish"}]
        return package

    @unittest.mock.patch("argostranslate.settings.device", "mps")
    @unittest.mock.patch("sentencepiece.SentencePieceProcessor")
    @unittest.mock.patch("ctranslate2.Translator")
    def test_translator_init_mps(self, mock_translator, _mock_sp):
        argostranslate.translate.Translator(self.get_mock_package())
        mock_translator.assert_called_once_with(
            str(pathlib.Path("test_package_path/model")), device="mps"
        )

    @unittest.mock.patch("argostranslate.settings.device", "auto")
    @unittest.mock.patch("sentencepiece.SentencePieceProcessor")
    @unittest.mock.patch("ctranslate2.Translator")
    def test_translator_init_auto_uses_cuda_when_available(
        self, mock_translator, _mock_sp
    ):
        with unittest.mock.patch(
            "ctranslate2.get_supported_compute_types", return_value={"float32"}
        ):
            argostranslate.translate.Translator(self.get_mock_package())
        mock_translator.assert_called_once_with(
            str(pathlib.Path("test_package_path/model")), device="cuda"
        )

    @unittest.mock.patch("argostranslate.settings.device", "auto")
    @unittest.mock.patch("sentencepiece.SentencePieceProcessor")
    @unittest.mock.patch("ctranslate2.Translator")
    def test_translator_init_auto_falls_back_to_cpu(self, mock_translator, _mock_sp):
        with unittest.mock.patch(
            "ctranslate2.get_supported_compute_types",
            side_effect=RuntimeError("no GPU"),
        ):
            argostranslate.translate.Translator(self.get_mock_package())
        mock_translator.assert_called_once_with(
            str(pathlib.Path("test_package_path/model")), device="cpu"
        )

    def test_default_device_is_auto(self):
        assert argostranslate.settings.device == "auto"
