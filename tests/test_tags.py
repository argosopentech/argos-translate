import pytest

from argostranslate import tags


class DictionaryTranslation:
    def __init__(self, translations):
        self.translations = translations
        self.calls = []

    def translate(self, text):
        self.calls.append(text)
        return self.translations[text]


@pytest.mark.parametrize("position", [0, 1, 2])
def test_empty_text_child_keeps_its_position(position):
    empty = tags.Tag([""])
    children = ["left", "right"]
    children.insert(position, empty)
    tree = tags.Tag(children)
    translation = DictionaryTranslation(
        {"left": "izquierda", "right": "derecha", "": "", "leftright": "contexto"}
    )

    result = tags.translate_tags(translation, tree)

    expected = ["izquierda", "derecha"]
    expected.insert(position, empty)
    assert result.children == expected
    assert empty.children == [""]
    assert "leftright" not in translation.calls


def test_empty_child_translation_falls_back_without_moving_the_tag():
    child = tags.Tag(["omit"])
    tree = tags.Tag(["left", child, "right"])
    translation = DictionaryTranslation(
        {
            "left": "izquierda",
            "right": "derecha",
            "omit": "",
            "leftomitright": "contexto",
        }
    )

    result = tags.translate_tags(translation, tree)

    assert result.children == ["izquierda", child, "derecha"]
    assert child.children == [""]


@pytest.mark.parametrize(
    "tree, expected",
    [
        ("text", 0),
        (tags.Tag([]), 0),
        (tags.Tag(["text"]), 1),
        (tags.Tag(["before", tags.Tag(["inside"])]), 2),
        (tags.Tag([tags.Tag([tags.Tag(["inside"])])]), 3),
    ],
)
def test_depth_counts_tag_levels(tree, expected):
    assert tags.depth(tree) == expected


def test_tag_injection_uses_sentence_translation_and_translates_child():
    translation = DictionaryTranslation(
        {
            "a red car": "une voiture rouge",
            "red": "rouge",
            "a ": "un ",
            " car": " vehicule",
        }
    )
    adjective = tags.Tag(["red"])
    tree = tags.Tag(["a ", adjective, " car"])

    assert tags.translate_tags(translation, tree) is tree
    assert tree.children == ["une voiture ", adjective]
    assert adjective.children == ["rouge"]
    assert tree.text() == "une voiture rouge"
    assert translation.calls == ["a red car", "red"]


def test_failed_injection_falls_back_to_translating_children():
    translation = DictionaryTranslation(
        {
            "a red car": "un vehicule ecarlate",
            "red": "rouge",
            "a ": "une ",
            " car": " voiture",
        }
    )
    adjective = tags.Tag(["red"])
    tree = tags.Tag(["a ", adjective, " car"])

    tags.translate_tags(translation, tree)

    assert tree.children == ["une ", adjective, " voiture"]
    assert adjective.children == ["rouge"]


def test_adjacent_injected_tags_are_not_overlapping():
    translation = DictionaryTranslation(
        {"redcar": "rougevoiture", "red": "rouge", "car": "voiture"}
    )
    first, second = tags.Tag(["red"]), tags.Tag(["car"])
    tree = tags.Tag([first, second])

    assert tags.inject_tags_inference(translation, tree) is tree
    assert tree.children == [first, second]
    assert tree.text() == "rougevoiture"


def test_failed_injection_does_not_partially_mutate_tree():
    translation = DictionaryTranslation(
        {"red car": "rouge automobile", "red": "rouge", "car": "voiture"}
    )
    first, second = tags.Tag(["red"]), tags.Tag(["car"])
    tree = tags.Tag([first, " ", second])

    assert tags.inject_tags_inference(translation, tree) is None
    assert tree.children == [first, " ", second]
    assert first.children == ["red"]
    assert second.children == ["car"]


def test_protected_child_is_not_included_in_sentence_translation():
    translation = DictionaryTranslation({"a ": "une ", " car": " voiture"})
    protected = tags.Tag(["red"], translateable=False)
    tree = tags.Tag(["a ", protected, " car"])

    tags.translate_tags(translation, tree)

    assert tree.text() == "une red voiture"
    assert tree.children[1] is protected
    assert translation.calls == ["a ", " car"]


def test_empty_nested_tag_is_preserved_during_fallback():
    translation = DictionaryTranslation(
        {"a ": "une ", "red": "rouge", " car": " voiture"}
    )
    empty = tags.Tag([])
    adjective = tags.Tag(["red", empty])
    tree = tags.Tag(["a ", adjective, " car"])

    tags.translate_tags(translation, tree)

    assert tree.text() == "une rouge voiture"
    assert adjective.children == ["rouge", empty]
