import pytest
from argostranslate import translate


class TestHypothesis:
    def test_less_than(self):
        test_cases = [
            [("this", 1.0), ("that", 2.0)],
            [("this and that", 5.0), ("another", 56.0)],
            [("im less", 0.2), ("I'm greater", 4.0)],
        ]
        for test_case in test_cases:
            first = translate.Hypothesis(*test_case[0])
            second = translate.Hypothesis(*test_case[1])
            assert first < second

    def test_string(self):
        test_cases = [
            {"input": ("this", 1.0), "output": "('this', 1.0)"},
            {"input": ("a word", 34.0), "output": "('a word', 34.0)"},
        ]
        for test_case in test_cases:
            string = str(translate.Hypothesis(*test_case["input"]))
            assert string == test_case["output"]

    def test_repr(self):
        test_cases = [
            {"input": ("this", 0.2), "output": "('this', 0.2)"},
            {"input": ("another thing", 3.0), "output": "('another thing', 3.0)"},
        ]
        for test_case in test_cases:
            current_repr = translate.Hypothesis(*test_case["input"]).__repr__()
            assert current_repr == test_case["output"]


class TestITranslation:
    def test_translate(self):
        with pytest.raises(NotImplementedError):
            translate.ITranslation().translate("some input")

    def test_hypotheses(self):
        with pytest.raises(NotImplementedError):
            translate.ITranslation().hypotheses("this is some text")

    def test_split_into_paragraphs(self):
        test_cases = [
            {"input": "first\nand second line", "output": ["first", "and second line"]},
            {"input": "this is\n on two lines", "output": ["this is", " on two lines"]},
        ]
        for test_case in test_cases:
            assert (
                translate.ITranslation.split_into_paragraphs(test_case["input"])
                == test_case["output"]
            )

    def test_combine_paragraphs(self):
        test_cases = [
            {
                "input": ["this and that", "along with this"],
                "output": "this and that\nalong with this",
            },
            {
                "input": ["one.", "and two."],
                "output": "one.\nand two.",
            },
        ]
        for test_case in test_cases:
            assert (
                translate.ITranslation.combine_paragraphs(test_case["input"])
                == test_case["output"]
            )

    def test_string(self):
        with pytest.raises(AttributeError):
            str(translate.ITranslation())

        # Add attributes manually
        translation = translate.ITranslation()
        translation.from_lang = "English"
        translation.to_lang = "Spanish"

        assert repr(translation) == "English -> Spanish"


class TestLanguage:
    def test_string(self):
        assert str(translate.Language("es", "Spanish")) == "Spanish"

    def test_get_translation(self):
        # No language test
        to = translate.Language("en", "English")
        assert translate.Language("es", "Spanish").get_translation(to) is None

        es = translate.Language("es", "Spanish")
        en = translate.Language("en", "English")
        en.to_lang = en
        # Add the language as supported (add it to translations_from)
        es.translations_from.append(en)
        assert es.get_translation(en) == en


class TestPackageTranslation:
    NotImplemented


class TestIdentityTranslation:
    def test_hypotheses(self):
        lang = translate.Language("es", "Spanish")
        identity_translation = translate.IdentityTranslation(lang)
        returned = identity_translation.hypotheses("this is some text", 1)
        for single_return in returned:
            assert isinstance(single_return, translate.Hypothesis)
            assert single_return.score == 0
            assert single_return.value == "this is some text"


class TestCompositeTranslation:
    def test_hypotheses(self):
        lang_one = translate.Language("en", "English")
        lang_two = translate.Language("es", "Spanish")

        t1 = translate.IdentityTranslation(lang_one)
        t2 = translate.IdentityTranslation(lang_two)

        composite = translate.CompositeTranslation(t1, t2)
        output = composite.hypotheses("This is some text", 1)
        assert len(output) == 1
        assert isinstance(output[0], translate.Hypothesis)
        assert output[0].score == 0
        assert output[0].value == "This is some text"


class TestCachedTranslation:
    NotImplemented
