import argostranslate.translate


class TranslationBehavior:
    def __init__(self, from_text: str, to_text: str):
        self.from_text = from_text
        self.to_text = to_text


class Translation(argostranslate.translate.ITranslation):
    def __init__(self, from_lang, to_lang):
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.translation_behaviors = list()

    def add_translation_behavior(self, from_text: str, to_text: str):
        self.translation_behaviors.append(TranslationBehavior(from_text, to_text))

    def translate(self, text: str) -> str:
        for behavior in self.translation_behaviors:
            if behavior.from_text == text:
                return behavior.to_text
        return text
