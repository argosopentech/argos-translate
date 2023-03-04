import argostranslate.tags


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
