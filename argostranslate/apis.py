import json
import sys
from urllib import request, parse

from argostranslate.models import ILanguageModel, ITranslation


class LibreTranslateAPI:
    DEFAULT_URL = "https://translate.astian.org/"
    # TODO: Add constructor to set url

    def translate(self, q, source="en", target="es", url=None):
        """Connect to LibreTranslate API

        Args:
            q (str): The text to translate
            source (str): The source language code (ISO 639)
            target (str): The target language code (ISO 639)
            url (str): The url for the translate endpoint. None for default.

        Returns: The translated text
        """
        if url is None:
            url = LibreTranslateAPI.DEFAULT_URL + "translate"

        params = {"q": q, "source": source, "target": target}

        url_params = parse.urlencode(params)

        req = request.Request(url, data=url_params.encode())

        try:
            response = request.urlopen(req)
        except Exception as e:
            print(e, sys.stderr)
            return None

        try:
            response_str = response.read().decode()
        except Exception as e:
            print(e, sys.stderr)
            return None

        return json.loads(response_str)

    def languages(url=None):
        """Connect to LibreTranslate API

        Args:
            url (str): The url for the languages endpoint. None for default.

        Returns: The translated text
        """

        if url is None:
            url = LibreTranslateAPI.DEFAULT_URL + "languages"

        req = request.Request(url, method="POST")

        try:
            response = request.urlopen(req)
        except Exception as e:
            print(e, sys.stderr)
            return None

        try:
            response_str = response.read().decode()
        except Exception as e:
            print(e, sys.stderr)
            return None

        return json.loads(response_str)


class LibreTranslateTranslation(ITranslation):
    def __init__(self, from_lang, to_lang, api):
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.api = api

    def hypotheses(self, input_text, num_hypotheses=1):
        """LibreTranslate only supports single hypotheses.

        A list of length num_hypotheses will be returned with identical hypotheses.
        """
        result = self.api.translate(input_text, self.from_lang, self.to_lang)[
            "translatedText"
        ]
        return [result] * num_hypotheses


# OpenAI API
# curl https://api.openai.com/v1/engines/davinci/completions \
# -H "Content-Type: application/json" \
# -H "Authorization: Bearer YOUR_API_KEY" \
# -d '{"prompt": "This is a test", "max_tokens": 5}'


class OpenAILanguageModel(ILanguageModel):
    def infer(prompt, api_key):
        """Connect to OpenAI API

        Args:
            prompt (str): The prompt to run inference on.
            api_key (str): OpenAI API key

        Returns: The generated text
        """
        url = "https://api.openai.com/v1/engines/davinci/completions"

        params = {"prompt": prompt, "max_tokens": 100}

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key,
        }

        encoded_params = json.dumps(params).encode()

        req = request.Request(url, data=encoded_params, headers=headers, method="POST")

        try:
            response = request.urlopen(req)
        except Exception as e:
            print(e, sys.stderr)
            return None

        try:
            response_str = response.read().decode()
        except Exception as e:
            print(e, sys.stderr)
            return None

        return json.loads(response_str)
