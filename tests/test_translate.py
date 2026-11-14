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


def test_package_changes_rebuild_models_and_pivot_routes(tmp_path, monkeypatch):
    import json
    import zipfile
    from argostranslate import package, settings

    monkeypatch.setattr(settings, "package_data_dir", tmp_path / "packages")
    settings.package_data_dir.mkdir()
    monkeypatch.setattr(settings, "package_dirs", [settings.package_data_dir])
    monkeypatch.setattr(settings, "model_provider", settings.ModelProvider.OPENNMT)

    class VersionTranslation(translate.ITranslation):
        def __init__(self, source, target, pkg):
            self.from_lang, self.to_lang, self.pkg = source, target, pkg

        def hypotheses(self, text, num_hypotheses=4):
            return [translate.Hypothesis(self.pkg.package_version, 0)
                    for _ in range(num_hypotheses)]

    monkeypatch.setattr(translate, "PackageTranslation", VersionTranslation)

    def install(source, target, version):
        archive = tmp_path / "model.argosmodel"
        with zipfile.ZipFile(archive, "w") as model:
            model.writestr(f"{source}_{target}/metadata.json", json.dumps({
                "from_code": source, "from_name": source,
                "to_code": target, "to_name": target,
                "package_version": version,
            }))
        package.install_from_path(archive)

    translate.get_installed_languages.cache_clear()
    try:
        install("en", "es", "1")
        assert translate.translate("hello", "en", "es") == "1"
        install("en", "es", "2")
        assert translate.translate("hello", "en", "es") == "2"
        install("es", "fr", "1")
        assert translate.get_translation_from_codes("en", "fr") is not None
        languages = translate.get_installed_languages()
        for language in languages:
            for translation in language.translations_from:
                assert translation.from_lang is language
                assert translation.to_lang in languages
        package.uninstall(package.Package(settings.package_data_dir / "es_fr"))
        assert translate.get_language_from_code("fr") is None
        assert [t.to_lang.code for t in translate.get_language_from_code("en").translations_from] == ["es", "en"]
    finally:
        translate.get_installed_languages.cache_clear()


@pytest.mark.parametrize("text", ["", "\n", "\n\nHello", "Hello\n", "Hello\n\nworld", "\nHello\n"])
@pytest.mark.parametrize("cached", [False, True])
def test_paragraph_assembly_preserves_newlines_and_scores(text, cached, monkeypatch):
    from types import SimpleNamespace

    lang = translate.Language("en", "English")
    translator = translate.PackageTranslation.__new__(translate.PackageTranslation)
    translator.from_lang = translator.to_lang = lang
    translator.pkg = SimpleNamespace()
    translator.translator = object()
    translator.sentencizer = object()

    def apply(pkg, paragraph, model, sentencizer, count):
        return [translate.Hypothesis(paragraph, -i) for i in range(count)]

    monkeypatch.setattr(translate, "apply_packaged_translation", apply)
    if cached:
        translator = translate.CachedTranslation(translator)
    for _ in range(2):
        hypotheses = translator.hypotheses(text, 2)
        assert [h.value for h in hypotheses] == [text, text]
        assert [h.score for h in hypotheses] == [0, -len(text.split("\n"))]
