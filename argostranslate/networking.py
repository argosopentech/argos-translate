import urllib.request
import random

from argostranslate.utils import info, error


def get_protocol(url):
    """Gets the protocol of a URL string

    For example if url is "https://www.argosopentech.com" "https" is returned.
    If the protocol can't be determined None is returned

    Args:
        url (str): The URL to get the protocol of

    Returns:
        str: The string representation of the protocol or None
    """
    protocol_end_index = url.find(":")
    if protocol_end_index > 0:
        return url[:protocol_end_index]
    return None


supported_protocols = set(["http", "https"])


def get(url, retry_count=3):
    """Downoads data from a url and returns it

    Args:
        url (str): The url to download (http, https)
        retry_count (int): The number of retries to attempt if the initial download fails.
                If retry_count is 0 the download will only be attempted once.

    Returns:
        bytes: The downloaded data, None is returned if the download fails
    """
    if get_protocol(url) not in supported_protocols:
        return None
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


def get_from(urls, retry_count=3):
    """Downloads data from a list of urls and returns it

    Args:
        urls (list(str)): The urls to download (http, https)
        retry_count (int): The number of retries to attempt if the initial download fails.
                If retry_count is 0 the download will only be attempted once.

    Returns:
        bytes: The downloaded data, None is returned if the download fails
    """
    for url in random.sample(urls, len(urls)):
        attempt = get(url, retry_count)
        if attempt is not None:
            return attempt
    return None
