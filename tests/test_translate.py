from argostranslate import translate


class TestHypothesis:
    def test_less_than(self):
        test_cases = [
            [("this", 1.0), ("that", 2.0)],
            [("this and that", 5.0), ("another", 56.0)],
            [("im less", 0.2), ("I'm greater", 4.0)],
        ]
        for test_case in test_cases:
            first = translate.Hypothesis(*test_case[0])
            second = translate.Hypothesis(*test_case[1])
            assert first < second

    def test_string(self):
        test_cases = [
            {"input": ("this", 1.0), "output": "('this', 1.0)"},
            {"input": ("a word", 34.0), "output": "('a word', 34.0)"},
        ]
        for test_case in test_cases:
            assert str(test_case["input"]) == test_case["output"]
