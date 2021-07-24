from argostranslate import translate


class ITag:
    def children(self):
        """List of ITags and strs"""
        raise NotImplmentedError()

    def text(self):
        raise NotImplmentedError()


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

        if type(tag) == str:
            return self.underlying_translation.translate(tag)

        text = tag.text()
        children = tag.children()

        if (
            len(text) > self.MAX_SEQUENCE_LENGTH
            or len(list(filter(lambda x: isinstance(x, Tag), children))) > 0
        ):
            # Translate children seperatly
            return Tag([translate_tag(self, child) for child in children])

        translated_text = self.underlying_translation.translate(text)

        if isinstance(tag, TagLiteral):
            return TagLiteral(translated_text)

        class InjectionTag:
            def __init__(self, text):
                self.text = text

        injection_tags = []
        for child in children:
            print(child)
            if isinstance(tag, TagLiteral):
                print("PJDEBUG")
                injection_tag = InjectionTag(
                    self.underlying_translation.translate(child.text())
                )
                injection_tags.append(injection_tag)

        for injection_tag in injection_tags:
            injection_index = translated_text.find(child_translation)
            if injection_index != -1:
                injection_tag.injection_index = injection_index
            else:
                return Tag([translate_tag(self, child) for child in children])

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
