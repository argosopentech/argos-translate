import unittest.mock

import pytest

import argostranslate.translate


def test_Hypothesis():
    hypothesis7 = argostranslate.translate.Hypothesis("7", -0.9)
    hypothesis7b = argostranslate.translate.Hypothesis("7", -0.9)
    hypothesis9 = argostranslate.translate.Hypothesis("9", -1.5)

    assert hypothesis9 < hypothesis7
    assert hypothesis7 > hypothesis9
    assert hypothesis9 != hypothesis7
    assert hypothesis7 == hypothesis7b

    assert repr(hypothesis7) == "-0.9 : 7"
    assert str(hypothesis7) == "-0.9 : 7"


def get_English():
    return argostranslate.translate.Language("en", "English")


def get_Spanish():
    return argostranslate.translate.Language("es", "Spanish")


def get_French():
    return argostranslate.translate.Language("fr", "French")


def test_Language():
    en = get_English()
    assert en.code == "en"
    assert en.name == "English"
    assert str(en) == "English"
    assert repr(en) == "en"


def test_IdentityTranslation():
    en = argostranslate.translate.Language("en", "English")
    i = argostranslate.translate.IdentityTranslation(en)
    assert i.translate("Hello World") == "Hello World"
    h = i.hypotheses("Hello World")[0]
    assert h.value == "Hello World"
    assert h.score == 0


def build_mock_translation(translation_dict, from_lang, to_lang):
    translation = argostranslate.translate.ITranslation()

    def mock_hypotheses(input_text: str, num_hypotheses: int = 1, **kwargs):
        return [argostranslate.translate.Hypothesis(translation_dict[input_text], -0.3)]

    translation.hypotheses = mock_hypotheses
    translation.from_lang = from_lang
    translation.to_lang = to_lang

    return translation


def get_translation_en_es():
    translation_dict = {
        "Hello World": "Hola Mundo",
    }
    translation_en_es = build_mock_translation(
        translation_dict, get_English(), get_Spanish()
    )
    return translation_en_es


def get_translation_es_en():
    translation_dict = {
        "Hola Mundo": "Hello World",
    }
    translation_en_es = build_mock_translation(
        translation_dict, get_English(), get_Spanish()
    )
    return translation_en_es


def get_translation_en_fr():
    translation_dict = {
        "Hello World": "Bonjour le monde",
    }
    translation_en_fr = build_mock_translation(
        translation_dict, get_English(), get_French()
    )
    return translation_en_fr


def test_CompositeTranslation():
    translation_es_en = get_translation_es_en()
    translation_en_fr = get_translation_en_fr()
    composite_translation = argostranslate.translate.CompositeTranslation(
        translation_es_en, translation_en_fr
    )
    assert composite_translation.translate("Hola Mundo") == "Bonjour le monde"
