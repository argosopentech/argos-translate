import argostranslate.tags

import mock_argostranslate_translate


def test_Tag():
    tag = argostranslate.tags.Tag(["Hello", " ", "World"])
    assert tag.text() == "Hello World"


def test_mulilevel_Tag():
    tag = argostranslate.tags.Tag(
        [
            "I went to ",
            argostranslate.tags.Tag(["Paris"]),
            " last summer.",
        ]
    )
    assert tag.text() == "I went to Paris last summer."


def get_Translation() -> argostranslate.translate.ITranslation:
    translation = mock_argostranslate_translate.Translation("en", "es")
    translation.add_translation_behavior("Hello", "Hola")
    return translation


def test_translate_tags_str():
    translation = get_Translation()
    translated_tag = argostranslate.tags.translate_tags(translation, "Hello")
    assert translated_tag == "Hola"


def test_translate_tags_depth_1():
    translation = get_Translation()
    tag = argostranslate.tags.Tag(["Hello"])
    translated_tag = argostranslate.tags.translate_tags(translation, tag)
    assert translated_tag == argostranslate.tags.Tag(["Hola"])


def test_translate_tag_chunk():
    source_text = "I have a house"
    target_text = "Tengo una casa"

    from_tag = argostranslate.tags.Tag(
        ["I have a ", argostranslate.tags.Tag(["house"], ".")]
    )
    to_tag = argostranslate.tags.Tag(
        ["Tengo una ", argostranslate.tags.Tag(["casa"], ".")]
    )

    translation = mock_argostranslate_translate.Translation("en", "es")
    translation.add_translation_behavior(source_text, target_text)
    translation.add_translation_behavior("I have a ", "Tengo una ")
    translation.add_translation_behavior("house", "casa")
    translation.add_translation_behavior(".", ".")
    translation.add_translation_behavior(
        "I have a <argos-tag>house</argos-tag>", "Tengo una <argos-tag>casa</argos-tag>"
    )

    translated_tag = argostranslate.tags.translate_tag_chunk(translation, from_tag)

    assert translated_tag == to_tag
