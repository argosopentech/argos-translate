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


def get_translation_en_es():
    translation_en_es = argostranslate.translate.ITranslation()

    def en_es_hypotheses(input_text: str, num_hypotheses: int = 1, **kwargs):
        return [argostranslate.translate.Hypothesis("Hola Mundo", -0.3)]

    translation_en_es.hypotheses = en_es_hypotheses
    translation_en_es.from_lang = get_English()
    translation_en_es.to_lang = get_Spanish()
    return translation_en_es


def get_translation_es_en():
    translation_es_en = argostranslate.translate.ITranslation()

    def es_en_hypotheses(input_text: str, num_hypotheses: int = 1, **kwargs):
        return [argostranslate.translate.Hypothesis("Hello World", -0.3)]

    translation_es_en.hypotheses = es_en_hypotheses
    translation_es_en.from_lang = get_Spanish()
    translation_es_en.to_lang = get_English()
    return translation_es_en


def test_CompositeTranslation():
    translation_en_es = get_translation_en_es()
    translation_es_en = get_translation_es_en()
    composite_translation = argostranslate.translate.CompositeTranslation(
        translation_en_es, translation_es_en
    )

    assert composite_translation.translate("Hello World") == "Hello World"
