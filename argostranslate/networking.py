import urllib.request

from argostranslate.utils import info, error


def get(url, retry_count=3):
    """Downoads data from a url and returns it

    Args:
        url (str): The url to download (http, https)
        retry_count (int): The number of retries to attempt if the initial download fails.
                If retry_count is 0 the download will only be attempted once.

    Returns:
        bytes: The downloaded data, None is returned if the download fails
    """
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
