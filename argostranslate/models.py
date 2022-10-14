from __future__ import annotations


class ILanguageModel:
    def infer(self, x: str) -> str | None:
        """Run language model on input x

        Args:
            x: Prompt to run inference on

        Returns:
            Output of inference
        """
        raise NotImplementedError()
