# TODO: Use CTranslate2 text generation https://opennmt.net/CTranslate2/generation.html


class ILanguageModel:
    def infer(x):
        """Run language model on input x

        Args:
            x (str): Prompt to run inference on

        Returns: (str) Output of inference
        """
        raise NotImplementedError()
