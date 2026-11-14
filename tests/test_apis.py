import json
from io import BytesIO
from unittest.mock import patch

from argostranslate.apis import LibreTranslateAPI


def _fake_response(payload):
    return BytesIO(json.dumps(payload).encode())


class TestLibreTranslateAPIRequestMethods:
    """LibreTranslate's `/languages` endpoint only accepts GET; `/translate`
    and `/detect` accept POST. `urllib.request.Request` defaults to POST
    whenever a `data` body is set, for every HTTP method except GET - so
    each call must set the right method explicitly rather than relying on
    the default, or the server rejects it with 405 METHOD NOT ALLOWED. See
    #449.
    """

    def test_languages_request_is_get(self):
        api = LibreTranslateAPI("https://example.org/")
        with patch("argostranslate.apis.request.urlopen") as urlopen:
            urlopen.return_value = _fake_response([{"code": "en", "name": "English"}])
            api.languages()
        req = urlopen.call_args[0][0]
        assert req.get_method() == "GET"

    def test_translate_request_is_post(self):
        api = LibreTranslateAPI("https://example.org/")
        with patch("argostranslate.apis.request.urlopen") as urlopen:
            urlopen.return_value = _fake_response({"translatedText": "hola"})
            api.translate("hello", "en", "es")
        req = urlopen.call_args[0][0]
        assert req.get_method() == "POST"

    def test_detect_request_is_post(self):
        api = LibreTranslateAPI("https://example.org/")
        with patch("argostranslate.apis.request.urlopen") as urlopen:
            urlopen.return_value = _fake_response(
                [{"confidence": 0.9, "language": "en"}]
            )
            api.detect("hello")
        req = urlopen.call_args[0][0]
        assert req.get_method() == "POST"
