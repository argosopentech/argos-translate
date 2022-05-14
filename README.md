# Argos Translate
[Demo](https://libretranslate.com) | [Website](https://www.argosopentech.com) | [Docs](https://argos-translate.readthedocs.io) |  [Forum](https://community.libretranslate.com/c/argos-translate/5) | [Video intro](https://odysee.com/@argosopentech:7/Machine-Translation-in-Argos-Translate-2021:5) | [GitHub](https://github.com/argosopentech/argos-translate)

Open-source offline translation library written in Python

Argos Translate uses [OpenNMT](https://opennmt.net/) for translations, [SentencePiece](https://github.com/google/sentencepiece) for tokenization, [Stanza](https://github.com/stanfordnlp/stanza) for sentence boundary detection, and [PyQt](https://riverbankcomputing.com/software/pyqt/intro) for GUI. Argos Translate can be used as either a Python library, command-line, or GUI application. [LibreTranslate](https://libretranslate.com) is an API and web-app built on top of Argos Translate.

Argos Translate supports installing language model packages which are zip archives with a ".argosmodel" extension with the data needed for translation.

Argos Translate also manages automatically pivoting through intermediate languages to translate between languages that don't have a direct translation between them installed. For example, if you have a es → en and en → fr translation installed you are able to translate from es → fr as if you had that translation installed. This allows for translating between a wide variety of languages at the cost of some loss of translation quality.

### Supported languages
Arabic, Azerbaijani, Chinese, Czech, Danish, Dutch, English, Esperanto, Finnish, French, German, Greek, Hindi, Hungarian, Indonesian, Irish, Italian, Japanese, Korean, Persian, Polish, Portuguese, Russian, Slovak, Spanish, Swedish, Turkish, Ukrainian, Vietnamese

- [Request a language](https://github.com/argosopentech/argos-translate/discussions/91)

## Installation
### Install from PyPI
Argos Translate is available from [PyPI](https://pypi.org/project/argostranslate/) and can be easily installed or updated with [pip](https://pip.pypa.io/en/stable/installation/).

```
pip3 install argostranslate
```

Install [GUI](https://github.com/argosopentech/argos-translate-gui):
```
pip3 install argostranslategui

```

### Installation for macOS

1. Download the latest [macOS release.](https://github.com/argosopentech/argos-translate/releases/)
2. Extract the archive.
3. Copy the `.app` file to the Applications directory.

### Python source installation

Download a copy of this repo and install with pip.

```
git clone https://github.com/argosopentech/argos-translate.git
cd argos-translate
pip install -e .
```

## Examples
### [Python](https://argos-translate.readthedocs.io/en/latest/py-modindex.html)

```python
import argostranslate.package, argostranslate.translate

from_code = "en"
to_code = "es"

# Download and install Argos Translate package
available_packages = argostranslate.package.get_available_packages()
available_package = list(
    filter(
        lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
    )
)[0]
download_path = available_package.download()
argostranslate.package.install_from_path(download_path)

# Translate
installed_languages = argostranslate.translate.get_installed_languages()
from_lang = list(filter(
	lambda x: x.code == from_code,
	installed_languages))[0]
to_lang = list(filter(
	lambda x: x.code == to_code,
	installed_languages))[0]
translation = from_lang.get_translation(to_lang)
translatedText = translation.translate("Hello World!")
print(translatedText)
# '¡Hola Mundo!'
```

### [LibreTranslate](https://github.com/LibreTranslate/LibreTranslate) Web App ([Demo](https://libretranslate.com/))
![Web App Screenshot](img/WebAppScreenshot.png)

### [LibreTranslate](https://github.com/uav4geo/LibreTranslate) API

```javascript
const res = await fetch("https://translate.argosopentech.com/translate", {
	method: "POST",
	body: JSON.stringify({
		q: "Hello!",
		source: "en",
		target: "es"
	}),
	headers: {
		"Content-Type": "application/json"}
	});

console.log(await res.json());

{
    "translatedText": "¡Hola!"
}
```

#### Graphical user interface
The GUI code is in a [separate repository](https://github.com/argosopentech/argos-translate-gui).

![Screenshot](/img/Screenshot.png)
![Screenshot2](/img/Screenshot2.png)
![Argos Translate macOS Screenshot](/img/ArgosTranslateMacOSScreenshot.png)


## [Packages](https://www.argosopentech.com/argospm/index/)
- [Browse](https://www.argosopentech.com/argospm/index/)
- [P2P download (IPFS and BitTorrent)](/p2p/README.md)
- [Training scripts](https://github.com/argosopentech/argos-train)
- [Google Drive download](https://drive.google.com/drive/folders/11wxM3Ze7NCgOk_tdtRjwet10DmtvFu3i)


### GPU Acceleration

To enable GPU support, you need to set the `ARGOS_DEVICE_TYPE` env variable to `cuda` or `auto`.

```
$ ARGOS_DEVICE_TYPE=cuda argos-translate --from-lang en --to-lang es "Hello World"
Hola Mundo
```

The above env variable instructs [CTranslate2](https://github.com/OpenNMT/CTranslate2) to use cuda.
if you encounter any issues with GPU inference please reference the [CTranslate2 documentation](https://github.com/OpenNMT/CTranslate2#what-hardware-is-supported).

### HTML Translation
The [translate-html](https://github.com/argosopentech/translate-html) library is built on top of Argos Translate and [Beautiful Soup](https://beautiful-soup-4.readthedocs.io/en/latest/) and parses and translates HTML. The LibreTranslate API also has support for translating HTML.


### Files Translation
The [argos-translate-files](https://github.com/dingedi/argos-translate-files) library is built on top of Argos Translate and parses and translates files. The LibreTranslate API also has support for translating files.

## Uninstall

``` shell
python3 -m pip uninstall argostranslate
```

You may choose to also delete temporary and cached files:

``` shell
rm -r ~/.local/cache/argos-translate
rm -r ~/.local/share/argos-translate
```

## Related Projects
- [LibreTranslate-py](https://github.com/argosopentech/LibreTranslate-py) - Python bindings for LibreTranslate
- [machinetranslation.io](https://www.machinetranslation.io/) - [OpenNMT](https://opennmt.net/) based translation and articles on machine translation
- [LibreTranslate-rs](https://github.com/grantshandy/libretranslate-rs) - LibreTranslate Rust bindings
- [LibreTranslate Go](https://github.com/SnakeSel/libretranslate) - LibreTranslate Golang bindings
- [LibreTranslator](https://gitlab.com/BeowuIf/libretranslator) - LibreTranslate Android app
- [Lexicon](https://github.com/dothq/lexicon) - Translation API.

## Contributing
[![Awesome Humane Tech](https://raw.githubusercontent.com/humanetech-community/awesome-humane-tech/main/humane-tech-badge.svg?sanitize=true)](https://github.com/humanetech-community/awesome-humane-tech)

Contributions are welcome! Available issues are on the [GitHub issues page](https://github.com/argosopentech/argos-translate/issues). Contributions of code, data, and pre-trained models can all be accepted.

## Support
For support please use the [LibreTranslate Forum](https://community.libretranslate.com/c/argos-translate/5) or [GitHub Issues](https://github.com/argosopentech/argos-translate/issues).

For questions about [CTranslate2](https://github.com/OpenNMT/CTranslate2) or general machine translation research the [OpenNMT Forum](https://forum.opennmt.net/) is a good resource.

## Services
Custom models trained on your own data are available for $1000/each (negotiable).

Managed LibreTranslate hosting is available for $1000/mo.

## Donate
If you find this software useful donations are appreciated.
- [GitHub Sponsor](https://github.com/sponsors/argosopentech)
- [PayPal](https://www.paypal.com/biz/fund?id=MCCFG437JP9PJ)
- Bitcoin: 16UJrmSEGojFPaqjTGpuSMNhNRSsnspFJT
- Ethereum: argosopentech.eth
- Litecoin: MCwu7RRWeCRJdsv2bXGj2nnL1xYxDBvwW5
- Bitcoin cash: qzqklgjpgutdqqlhcasmdd2hkqcelw426sxzk5qtne
- Filecoin: f1nrnpmjxn27amidyiqrzq5mxihdo2trh2oijw2sq
- Basic Attention Token: 0x8a16f26D277f924B04FCA5ECec64b76B5410A06c

Paid supporters receive priority support.

You can also support the project by purchasing [DigitalOcean](https://www.digitalocean.com/) hosting with the [Argos Open Tech referral link](https://m.do.co/c/a1af57be6e3f) which helps to offset [CDN hosting costs](https://community.libretranslate.com/t/estimating-libretranslate-usage-from-cdn-traffic/78/7).

## License
Dual licensed under either the [MIT License](https://github.com/argosopentech/argos-translate/blob/master/LICENSE) or [Creative Commons CC0](https://creativecommons.org/share-your-work/public-domain/cc0/).
