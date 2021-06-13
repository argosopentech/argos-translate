class ILanguageModel:
    def infer(x):
        """Run language model on input x

        Args:
            x (str): Prompt to run inference on

        Returns: (str) Output of inference
        """
        raise NotImplementedError()


class ITranslation:
    """Respresents a translation between two Languages

    Attributes:
        from_lang (Language): The Language this Translation translates from.
        to_lang (Language): The Language this Translation translates to.

    """

    def translate(self, input_text):
        """Translates a string from self.from_lang to self.to_lang

        Args:
            input_text (str): The text to be translated.

        Returns:
            str: input_text translated.

        """
        return self.hypotheses(input_text, num_hypotheses=1)[0].value

    def hypotheses(self, input_text, num_hypotheses=4):
        """Translates a string from self.from_lang to self.to_lang

        Args:
            input_text (str): The text to be translated.
            num_hypotheses (int): Number of hypothetic results expected

        Returns:
            [Hypothesis]: List of translation hypotheses

        """
        raise NotImplementedError()

    @staticmethod
    def split_into_paragraphs(input_text):
        """Splits input_text into paragraphs and returns a list of paragraphs.

        Args:
            input_text (str): The text to be split.

        Returns:
            [str]: A list of paragraphs.

        """
        return input_text.split("\n")

    @staticmethod
    def combine_paragraphs(paragraphs):
        """Combines a list of paragraphs together.

        Args:
            paragraphs ([str]): A list of paragraphs.

        Returns:
            [str]: list of n paragraphs combined into one string.

        """
        return "\n".join(paragraphs)

    def __repr__(self):
        return str(self.from_lang) + " -> " + str(self.to_lang)

    def __str__(self):
        return repr(self).replace("->", "→")
