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


# OpenAI API
# curl https://api.openai.com/v1/engines/davinci/completions \
# -H "Content-Type: application/json" \
# -H "Authorization: Bearer YOUR_API_KEY" \
# -d '{"prompt": "This is a test", "max_tokens": 5}'


def infer(prompt, api_key):
    """Connect to OpenAI API

    Args:
        prompt (str): The prompt to run inference on.
        api_key (str): OpenAI API key

    Returns: The generated text
    """
    url = "https://api.openai.com/v1/engines/davinci/completions"

    params = {"prompt": prompt, "max_tokens": 100}

    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + api_key}

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
