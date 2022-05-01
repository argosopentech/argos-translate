import urllib.request

from argostranslate.utils import info, error


def get(url, retry_count=3):
    url = str(url)
    info(f"Downloading {url}")
    download_attempts_count = 0
    while download_attempts_count <= retry_count:
        try:
            response = urllib.request.urlopen(url)
            data = response.read()
            info(f"Got {url}")
            return data
        except Exception as err:
            download_attempts_count += 1
            error(err)
    return None
