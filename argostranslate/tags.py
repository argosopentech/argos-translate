from argostranslate import translate
from argostranslate.utils import info, error

"""
import argostranslate
from argostranslate.tags import *
from argostranslate import package, translate

installed_languages = translate.get_installed_languages()
translation_en_es = installed_languages[0].get_translation(installed_languages[1])

tag_translation = TagTranslation(translation_en_es)
t = Tag(['I went to ', TagLiteral('Paris'), ' last summer.'])

translated_tags = tag_translation.translate_tag(t).children()
for translated_tag in translated_tags:
    print(str(translated_tag))

"""


class ITag:
    def children(self):
        """List of ITags and strs"""
        raise NotImplmentedError()

    def text(self):
        raise NotImplmentedError()

    def __str__(self):
        return f'{ str(type(self)) } "{ str(self.text()) }"'


class TagLiteral(ITag):
    def __init__(self, text):
        self._text = text

    def children(self):
        return None

    def text(self):
        return self._text


class Tag(ITag):
    def __init__(self, children):
        self._children = children

    def children(self):
        return self._children

    def text(self):
        return "".join(
            [
                (child.text() if type(child) != str else child)
                for child in self._children
            ]
        )


class TagTranslation(translate.ITranslation):
    MAX_SEQUENCE_LENGTH = 200

    def __init__(self, underlying_translation):
        self.underlying_translation = underlying_translation

    def translate_tag(self, tag):
        """Takes an ITag or str and returns an ITag or str"""
        info("translate_tag", tag)

        if type(tag) == str:
            return self.underlying_translation.translate(tag)

        text = tag.text()
        children = tag.children()

        composite_tag_children = (
            children is not None
            and len(list(filter(lambda x: isinstance(x, Tag), children))) > 0
        )
        if len(text) > self.MAX_SEQUENCE_LENGTH or composite_tag_children:
            # Translate children seperatly
            return Tag([self.translate_tag(child) for child in children])

        translated_text = self.underlying_translation.translate(text)

        if isinstance(tag, TagLiteral):
            return TagLiteral(translated_text)

        class InjectionTag:
            def __init__(self, text):
                self.text = text

        injection_tags = []
        for child in children:
            if isinstance(child, TagLiteral):
                injection_tag = InjectionTag(
                    self.underlying_translation.translate(child.text())
                )
                injection_tags.append(injection_tag)

        for injection_tag in injection_tags:
            injection_index = translated_text.find(injection_tag.text)
            if injection_index != -1:
                injection_tag.injection_index = injection_index
            else:
                info(
                    "translate_tag",
                    "injection_tag.text not found",
                    translated_text,
                    injection_tag.text,
                )
                return Tag([self.translate_tag(child) for child in children])

        # TODO check for overlap

        injection_tags.sort(key=lambda x: x.injection_index)
        to_return = []
        i = 0
        for injection_tag in injection_tags:
            if i < injection_tag.injection_index:
                to_return.append(translated_text[i : injection_tag.injection_index])
            to_return.append(TagLiteral(injection_tag.text))
            i = injection_tag.injection_index + len(injection_tag.text)
        if i < len(translated_text):
            to_return.append(translated_text[i:])

        return Tag(to_return)
