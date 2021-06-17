class ILanguageModel:
    def infer(x):
        """Run language model on input x

        Args:
            x (str): Prompt to run inference on

        Returns: (str) Output of inference
        """
        raise NotImplementedError()
