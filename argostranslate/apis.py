import json
import sys
from urllib import request, parse

from argostranslate.models import ILanguageModel


class LibreTranslateAPI:
    """Connect to the LibreTranslate API"""

    """Example usage:
    from argostranslate.apis import LibreTranslateAPI
    lt = LibreTranslateAPI("https://translate.astian.org/")
    print(lt.detect("Hello World"))
    print(lt.languages())
    print(lt.translate("LibreTranslate is awesome!", "en", "es"))
    """

    DEFAULT_URL = "https://translate.astian.org/"

    def __init__(self, url=None, api_key=None):
        """Create a LibreTranslate API connection.

        Args:
            url (str): The url of the LibreTranslate endpoint.
            api_key (str): The API key.
        """

        self.url = self.DEFAULT_URL if url is None else url
        self.api_key = api_key

        # Add trailing slash
        assert len(self.url) > 0
        if self.url[-1] != "/":
            self.url += "/"

    def translate(self, q, source="en", target="es"):
        """Translate string

        Args:
            q (str): The text to translate
            source (str): The source language code (ISO 639)
            target (str): The target language code (ISO 639)

        Returns: The translated text
        """

        url = self.url + "translate"

        params = {"q": q, "source": source, "target": target}

        if self.api_key is not None:
            params["api_key"] = self.api_key

        url_params = parse.urlencode(params)

        req = request.Request(url, data=url_params.encode())

        response = request.urlopen(req)

        response_str = response.read().decode()

        return json.loads(response_str)["translatedText"]

    def languages(self):
        """Retrieve list of supported languages.

        Returns: A list of available languages ex. [{"code":"en", "name":"English"}]
        """

        url = self.url + "languages"

        params = dict()

        if self.api_key is not None:
            params["api_key"] = self.api_key

        url_params = parse.urlencode(params)

        req = request.Request(url, data=url_params.encode())

        response = request.urlopen(req)

        response_str = response.read().decode()

        return json.loads(response_str)

    def detect(self, q):
        """Detect the language of a single text.

        Args:
            q (str): Text to detect

        Returns: The detected languages ex. [{"confidence": 0.6, "language": "en"}]
        """

        url = self.url + "detect"

        params = {"q": q}

        if self.api_key is not None:
            params["api_key"] = self.api_key

        url_params = parse.urlencode(params)

        req = request.Request(url, data=url_params.encode())

        response = request.urlopen(req)

        response_str = response.read().decode()

        return json.loads(response_str)


# OpenAI API
# curl https://api.openai.com/v1/engines/davinci/completions \
# -H "Content-Type: application/json" \
# -H "Authorization: Bearer YOUR_API_KEY" \
# -d '{"prompt": "This is a test", "max_tokens": 5}'


class OpenAIAPI(ILanguageModel):
    def __init__(self, api_key):
        """Create an API connection.

        Args:
            api_key (str): The API key for the OpenAI API
        """
        self.api_key = api_key

    def infer(self, prompt):
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
            "Authorization": "Bearer " + self.api_key,
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

        return json.loads(response_str)["choices"][0]["text"]
