import json
import sys
from urllib import request, parse


def translate(
    q, source="en", target="es", url="https://translate.astian.org/translate"
):
    """Connect to LibreTranslate API

    Args:
        q (str): The text to translate
        source (str): The source language code (ISO 639)
        target (str): The target language code (ISO 639)

    Returns: The translated text
    """
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
