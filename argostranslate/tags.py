from argostranslate import translate
from argostranslate.utils import info, error

"""
import argostranslate
from argostranslate.tags import *
from argostranslate import package, translate

installed_languages = translate.get_installed_languages()
translation_en_es = installed_languages[0].get_translation(installed_languages[1])

t = Tag(['I went to ', Tag(['Paris']), ' last summer.'])

translated_tags = translate_tags(translation_en_es, t).children()
for translated_tag in translated_tags:
    print(str(translated_tag))

"""


class ITag:
    """Represents a tag tree"""

    def children(self):
        """List of ITags and strs representing the children of the tag (empty list if no children)

        Returns:
            [ITag or str]: Children
        """
        raise NotImplementedError()

    def text(self):
        """The combined text of all of the children

        Returns:
            str: Combined text
        """
        raise NotImplementedError()

    def __str__(self):
        return f'{ str(type(self)) } "{ str(self.text()) }"'


class Tag(ITag):
    """Represents a tag with children"""

    def __init__(self, children):
        self._children = children

    def children(self):
        return self._children

    def text(self):
        return "".join(
            [
                (child.text() if type(child) != str else child)
                for child in self.children()
            ]
        )


MAX_SEQUENCE_LENGTH = 200


def is_tag_literal(tag):
    if type(tag) is str:
        return False
    elif len(tag.children()) == 1 and type(tag.children()[0]) is str:
        return True
    return False


def translate_children(underlying_translation, tag):
    # Translate children seperatly
    for i in range(len(tag._children)):
        child = tag.children()[i]
        translation = translate_tags(underlying_translation, tag.children()[i])
        if type(child) is str and type(translation) is str:
            if len(child) > 0 and child[0] == " ":
                if not (len(translation) > 0 and translation[0] == " "):
                    translation = " " + translation
            if len(child) > 0 and child[-1] == " ":
                if not (len(translation) > 0 and translation[-1] == " "):
                    translation = translation + " "
        tag.children()[i] = translation
    return tag


def is_small_tree(tag, depth=0):
    depth += 1
    if depth > 3:
        return False
    if type(tag) is str:
        return True
    if len(tag.children()) > 5:
        return False
    for child in tag.children():
        if not is_small_tree(tag, depth):
            return False
    return True


def translate_tags(underlying_translation, tag):
    """Recursively takes either an ITag or a str and returns a translated tag tree

    Args:
        tag (ITag or str): The tag tree to translate

    Returns:
        ITag or str: A translated tag tree in the same form
    """
    info("translate_tags", tag)

    if type(tag) == str:
        return underlying_translation.translate(tag)

    if not is_small_tree(tag):
        return translate_children(underlying_translation, tag)

    text = tag.text()

    translated_text = underlying_translation.translate(text)

    if is_tag_literal(tag):
        tag._text = translated_text
        return tag

    children = tag.children()

    composite_tag_children = (
        children is not None
        and len(list(filter(lambda x: isinstance(x, Tag), children))) > 0
    )
    if len(text) > MAX_SEQUENCE_LENGTH or composite_tag_children:
        return translate_children(underlying_translation, tag)

    class InjectionTag:
        def __init__(self, text, tag):
            self.text = text
            self.tag = tag

    injection_tags = []
    for child in children:
        if is_tag_literal(child):
            injection_tag = InjectionTag(
                underlying_translation.translate(child.text()), child
            )
            injection_tags.append(injection_tag)

    for injection_tag in injection_tags:
        injection_index = translated_text.find(injection_tag.text)
        if injection_index != -1:
            injection_tag.injection_index = injection_index
        else:
            info(
                "translate_tags",
                "injection_tag.text not found",
                translated_text,
                injection_tag.text,
            )
            return translate_children(underlying_translation, tag)

    # Check for overlap
    injection_tags.sort(key=lambda x: x.injection_index)
    for i in range(len(injection_tags) - 1):
        injection_tag = injection_tags[i]
        next_injection_tag = injection_tags[i + 1]
        if (
            injection_tag.injection_index + len(injection_tag.text)
            >= next_injection_tag.injection_index
        ):
            info(
                "translate_tags",
                "injection_tags_overlap",
                injection_tag,
                next_injection_tag,
            )
            return translate_children(underlying_translation, tag)

    to_return = []
    i = 0
    for injection_tag in injection_tags:
        if i < injection_tag.injection_index:
            to_return.append(translated_text[i : injection_tag.injection_index])
        to_return.append(injection_tag.tag)
        i = injection_tag.injection_index + len(injection_tag.text)
    if i < len(translated_text):
        to_return.append(translated_text[i:])

    tag._children = to_return
    return tag
