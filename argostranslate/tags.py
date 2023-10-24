from __future__ import annotations

import difflib
import typing

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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ITag):
            return False
        if len(self.children) != len(other.children):
            return False
        return all(
            [self.children[i] == other.children[i] for i in range(len(self.children))]
        )

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

GOLDEN_RATIO = (1 + 5**0.5) / 2


def flatten_tag(tag: ITag) -> str:
    """Flattens an ITag into a string"""
    flat = str()
    for child in tag.children:
        if isinstance(child, str):
            flat += child
        else:
            flat += f"{ARGOS_OPEN_TAG}{child.text()}{ARGOS_CLOSE_TAG}"
    return flat


def unflatten_tag(flat_tag: str) -> ITag | None:
    """Unflattens a string into an depth=2 ITag

    Returns None if the string is not a valid flattened depth=2 tag
    """
    unflattened = Tag(list())
    while len(flat_tag) > 0:
        open_tag_index = flat_tag.find(ARGOS_OPEN_TAG)
        if open_tag_index == -1:
            unflattened.children.append(flat_tag)
            flat_tag = ""
            break
        elif open_tag_index > 0:
            unflattened.children.append(flat_tag[:open_tag_index])
            flat_tag = flat_tag[open_tag_index:]
        else:
            closing_tag_index = flat_tag.find(ARGOS_CLOSE_TAG)
            tag_inner_text = flat_tag[
                open_tag_index + len(ARGOS_OPEN_TAG) : closing_tag_index
            ]
            unflattened.children.append(Tag([tag_inner_text]))
            flat_tag = flat_tag[closing_tag_index + len(ARGOS_CLOSE_TAG) :]

    if depth(unflattened) != 2:
        return None

    return unflattened


def translate_tag_chunk(
    translation: argostranslate.translate.ITranslation, tag: ITag
) -> ITag | None:
    """Translate an ITag with depth(tag) == 2

    Args:
        translation: The translation to use to translate the tag
        tag: The tag to translate

    Returns:
        The translated tag, or None if the translation failed

    This function attempts to use context from nearby text to translate a tag with depth 2.

    If it fails to find a translation better than the default of translating each tag individually,
    None is returned.

    If successful, the tag is modified in place and returned. If None is returned, the tag is not modified.

    """
    assert depth(tag) == 2

    # Attempt translation with flattened tags
    # Example:
    # I have a <argos-tag>house</argos-tag>

    translated_prompt = translation.translate(flatten_tag(tag))
    translated_tag_attempt = unflatten_tag(translated_prompt)

    if translated_tag_attempt is None:
        return None

    if not is_same_structure(tag, translated_tag_attempt):
        info(
            "Tags have different structure after translation",
            tag,
            translated_tag_attempt,
        )
        return None

    # Check translation attempt is similar to translation without tags
    translated_without_tags = translation.translate(tag.text())
    similarity_between_attemted_translation_and_without_tags = difflib.SequenceMatcher(
        None, translated_tag_attempt.text(), translated_without_tags
    ).ratio()
    if similarity_between_attemted_translation_and_without_tags < 1 / GOLDEN_RATIO:
        return None

    # Copy the translated_tag values into the original tag
    for i in range(len(tag.children)):
        if isinstance(tag.children[i], Tag) and isinstance(
            translated_tag_attempt.children[i], Tag
        ):
            typing.cast(ITag, tag.children[i]).children = typing.cast(
                ITag, translated_tag_attempt.children[i]
            ).children
        elif isinstance(tag.children[i], str):
            tag.children[i] = translated_tag_attempt.children[i]
    return tag


def translate_tags(
    translation: argostranslate.translate.ITranslation, tag: ITag | str
) -> ITag | str:
    """Translate an ITag or str

    Recursively takes either an ITag or a str, modifies it in place, and returns the translated tag tree

    Args:
        translation: The translation to apply
        tag: The tag tree to translate

    Returns:
        The translated tag tree
    """
    if isinstance(tag, str):
        return translation.translate(tag)
    elif tag.translateable is False:
        return tag
    elif depth(tag) == 2:
        translated_tag_chunk = translate_tag_chunk(translation, tag)
        if translated_tag_chunk is not None:
            return translated_tag_chunk
    tag.children = [translate_tags(translation, child) for child in tag.children]

    return tag
