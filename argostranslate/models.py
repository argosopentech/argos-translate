class ILanguageModel:
    def infer(x: str) -> str:
        """Run language model on input x

        Args:
            x: Prompt to run inference on

        Returns: Output of inference
        """
        raise NotImplementedError()
