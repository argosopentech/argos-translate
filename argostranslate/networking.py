from __future__ import annotations

import random
import urllib.request

from spacy.cli import download as spacy_download
from spacy import load as spacy_load
from os import makedirs
from pathlib import Path
from argostranslate.utils import error, info
from argostranslate import settings


USER_AGENT = "ArgosTranslate"


def get_protocol(url: str) -> str | None:
    """Gets the protocol of a URL string

    For example if url is "https://www.argosopentech.com" "https" is returned.
    If the protocol can't be determined None is returned

    Args:
        url: The URL to get the protocol of

    Returns:
        The string representation of the protocol or None
    """
    protocol_end_index = url.find(":")
    if protocol_end_index > 0:
        return url[:protocol_end_index]
    return None


supported_protocols = {"http", "https"}


def get(url: str, retry_count: int = 3) -> bytes | None:
    """Downloads data from an url and returns it

    Args:
        url: The url to download (http, https)
        retry_count: The number of retries to attempt if the initial download fails.
                If retry_count is 0 the download will only be attempted once.

    Returns:
        The downloaded data, None is returned if the download fails
    """
    if get_protocol(url) not in supported_protocols:
        return None
    info(f"Get {url}")
    download_attempts_count = 0
    while download_attempts_count <= retry_count:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": USER_AGENT},
            )
            response = urllib.request.urlopen(req)
            data = response.read()
            info(f"Got {url}")
            return data
        except Exception as err:
            download_attempts_count += 1
            error(err)
    return None


def get_from(urls: list[str], retry_count: int = 3) -> bytes | None:
    """Downloads data from a list of urls and returns it

    Args:
        urls: The urls to download (http, https)
        retry_count: The number of retries to attempt if the initial download fails.
                If retry_count is 0 the download will only be attempted once.

    Returns:
        The downloaded data, None is returned if the download fails
    """
    for url in random.sample(urls, len(urls)):
        attempt = get(url, retry_count)
        if attempt is not None:
            return attempt
    return None

def get_spacy():
    """ Downloads spacy multilingual model and saves it the cache directory for further use"""
    spacy_cache = Path(settings.cache_dir / "spacy")
    makedirs(spacy_cache, exist_ok=True)
    info("Downloading spacy model")
    spacy_model = Path(spacy_cache / "senter" / "model")
    if not spacy_model.exists():
        while True:
            try:
                spacy_download("xx_sent_ud_sm")
                nlp = spacy_load("xx_sent_ud_sm", exclude=["parser"])
                nlp.to_disk(spacy_cache)
                return spacy_cache
            except Exception as e:
                print(f'{str(e)}.')
                return None
    else: return spacy_cache
