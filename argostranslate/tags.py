from __future__ import annotations

import argostranslate.translate
from argostranslate.utils import info

"""
import argostranslate
from argostranslate.tags import translate_tags, Tag
from argostranslate import translate

installed_languages = translate.get_installed_languages()
translation = argostranslate.translate.get_translation_from_codes("en", "es")

t = Tag(['I went to ', Tag(['Paris']), ' last summer.'])

translated_tags = translate_tags(translation, t)
for translated_tag in translated_tags.children:
    print(str(translated_tag))
"""


class ITag:
    """Represents a tag tree

    Attributes:
        children: List of ITags and strs representing
                the children of the tag (empty list if no children)
        translateable: If translateable is False then a tag and its children
                should not be translated
    """

    translateable: bool
    children: list[ITag | str]

    def text(self) -> str:
        """The combined text of all of the children

        Returns:
            Combined text
        """
        raise NotImplementedError()

    def __str__(self) -> str:
        return f'{str(type(self))} "{str(self.children)}"'


class Tag(ITag):
    def __init__(self, children: list[ITag | str], translateable: bool = True):
        self.children = children
        self.translateable = translateable

    def text(self) -> str:
        def child_to_str(child: ITag | str) -> str:
            if isinstance(child, ITag):
                return child.text()
            else:
                return child

        return "".join([child_to_str(child) for child in self.children])


def depth(tag: ITag | str) -> int:
    """Returns the depth of an ITag or str.

    A str has depth 0, ITag([]) has depth 0, ITag(['str']) has depth 1.

    Args:
        tag: The ITag or string to get the depth of.
    """
    if isinstance(tag, str):
        return 0
    if len(tag.children) == 0:
        return 0
    return max([depth(t) for t in tag.children]) + 1


def is_same_structure(tag1: ITag | str, tag2: ITag | str) -> bool:
    """Checks if two tags have the same structure

    Args:
        tag1: The first tag to compare
        tag2: The second tag to compare

    Returns:
        True if the tags have the same structure, false otherwise
    """
    if isinstance(tag1, str) and isinstance(tag2, str):
        return True
    elif isinstance(tag1, str) or isinstance(tag2, str):
        return False
    elif len(tag1.children) != len(tag2.children):
        return False
    else:
        return all(
            [
                is_same_structure(tag1.children[i], tag2.children[i])
                for i in range(len(tag1.children))
            ]
        )


ARGOS_OPEN_TAG = "<argos-tag>"
ARGOS_CLOSE_TAG = "</argos-tag>"


def translate_tag_chunk(
    underlying_translation: argostranslate.ITranslation, tag: ITag
) -> ITag | None:
    """Translate a chunk of text in an ITag

    Is a helper function for translate_tags. Takes an ITag with depth 2 and translates it.
    """
    prompt = str()
    for child in tag.children:
        if isinstance(child, str):
            prompt += child
        else:
            prompt += f"{ARGOS_OPEN_TAG}{child.text()}{ARGOS_CLOSE_TAG}"
    translated_prompt = underlying_translation.translate(prompt)
    translated_tag = Tag(list())
    while len(translated_prompt) > 0:
        open_tag_index = translated_prompt.find(ARGOS_OPEN_TAG)
        if open_tag_index == -1:
            translated_tag.children.append(translated_prompt)
            translated_prompt = ""
            break
        elif open_tag_index > 0:
            translated_tag.children.append(translated_prompt[:open_tag_index])
            translated_prompt = translated_prompt[open_tag_index:]
        else:
            closing_tag_index = translated_prompt.find(ARGOS_CLOSE_TAG)
            tag_inner_text = translated_prompt[
                open_tag_index + len(ARGOS_OPEN_TAG) : closing_tag_index
            ]
            translated_tag.children.append(Tag([tag_inner_text]))
            translated_prompt = translated_prompt[
                closing_tag_index + len(ARGOS_CLOSE_TAG) :
            ]
    if not is_same_structure(tag, translated_tag):
        info("Tags have different structure after translation", tag, translated_tag)
        return None
    # Copy the translated_tag values into the original tag
    for i in range(len(tag.children)):
        if isinstance(tag.children[i], Tag):
            tag.children[i].children = translated_tag.children[i].children
        elif isinstance(tag.children[i], str):
            tag.children[i] = translated_tag.children[i]
    return tag


def translate_tags(
    underlying_translation: argostranslate.ITranslation, tag: ITag | str
) -> ITag | str:
    """Translate an ITag or str

    Recursively takes either an ITag or a str, modifies it in place, and returns the translated tag tree

    Args:
        underlying_translation: The translation to apply
        tag: The tag tree to translate

    Returns:
        The translated tag tree
    """
    if type(tag) is str:
        return tag
    elif tag.translateable is False:
        return tag
    elif depth(tag) == 2:
        translated_tag_chunk = translate_tag_chunk(underlying_translation, tag)
        if translated_tag_chunk is not None:
            return translated_tag_chunk
    tag.children = [
        translate_tags(underlying_translation, child) for child in tag.children
    ]

    return tag
