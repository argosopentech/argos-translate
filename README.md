# Argos Translate
[Demo](https://libretranslate.com) | [Website](https://www.argosopentech.com) | [Docs](https://argos-translate.readthedocs.io) |  [Forum](https://community.libretranslate.com/c/argos-translate/5) | [GitHub](https://github.com/argosopentech/argos-translate) | [PyPI](https://pypi.org/project/argostranslate/)

**Open-source offline translation library written in Python**

Argos Translate uses [OpenNMT](https://opennmt.net/) for translations and can be used as either a Python library, command-line, or GUI application. Argos Translate supports installing language model packages which are zip archives with a ".argosmodel" extension containing the data needed for translation. [LibreTranslate](https://libretranslate.com) is an API and web-app built on top of Argos Translate.

Argos Translate also manages automatically pivoting through intermediate languages to translate between languages that don't have a direct translation between them installed. For example, if you have a es → en and en → fr translation installed you are able to translate from es → fr as if you had that translation installed. This allows for translating between a wide variety of languages at the cost of some loss of translation quality.

### Supported languages
Arabic, Azerbaijani, Catalan, Chinese, Czech, Danish, Dutch, English, Esperanto, Finnish, French, German, Greek, Hebrew, Hindi, Hungarian, Indonesian, Irish, Italian, Japanese, Korean, Persian, Polish, Portuguese, Russian, Slovak, Spanish, Swedish, Turkish, Ukrainian

[Request a language](https://github.com/argosopentech/argos-translate/discussions/91)

## Installation
### Install with Python
Argos Translate is available from [PyPI](https://pypi.org/project/argostranslate/) and can be easily installed or updated with [pip](https://pip.pypa.io/en/stable/installation/).

```
pip install argostranslate
```

Install [GUI](https://github.com/argosopentech/argos-translate-gui):
```
pip install argostranslategui
```

### Installation for macOS

1. Download the latest [macOS release.](https://github.com/argosopentech/argos-translate/releases/)
2. Extract the archive.
3. Copy the `.app` file to the Applications directory.

### Python source installation into virtualenv

Download a copy of this repo and install with pip.

```
git clone https://github.com/argosopentech/argos-translate.git
cd argos-translate
virtualenv env
source env/bin/activate
pip install -e .
```

## Examples
### [Python](https://argos-translate.readthedocs.io/en/latest/py-modindex.html)

```python
import argostranslate.package
import argostranslate.translate

from_code = "en"
to_code = "es"

# Download and install Argos Translate package
argostranslate.package.update_package_index()
available_packages = argostranslate.package.get_available_packages()
package_to_install = next(
    filter(
        lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
    )
)
argostranslate.package.install_from_path(package_to_install.download())

# Translate
translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
print(translatedText)
# '¡Hola Mundo!'
```

### Command Line Interface
```
argospm update
argospm install translate-en_de
argos-translate --from en --to de "Hello World!"
# Hallo Welt!

```

Install all translation packages:
```
argospm install translate
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

The above env variable passes the device type to [CTranslate2](https://github.com/OpenNMT/CTranslate2).

### HTML Translation
The [translate-html](https://github.com/argosopentech/translate-html) library is built on top of Argos Translate and [Beautiful Soup](https://beautiful-soup-4.readthedocs.io/en/latest/) and parses and translates HTML. The LibreTranslate API also has support for translating HTML.


### Files Translation
The [argos-translate-files](https://github.com/LibreTranslate/argos-translate-files) library is built on top of Argos Translate and parses and translates files. The LibreTranslate API also has support for translating files.

## Uninstall

``` shell
pip uninstall argostranslate
```

You may choose to also delete temporary and cached files:

``` shell
rm -r ~/.local/cache/argos-translate
rm -r ~/.local/share/argos-translate
```

## Related Projects
- [LibreTranslate-py](https://github.com/argosopentech/LibreTranslate-py) - Python bindings for LibreTranslate
- [MetalTranslate](https://github.com/argosopentech/MetalTranslate) - Customizable translation in C++
- [DesktopTranslator](https://github.com/ymoslem/DesktopTranslator) - [OpenNMT](https://opennmt.net/) based translation application
- [LibreTranslate-rs](https://github.com/grantshandy/libretranslate-rs) - LibreTranslate Rust bindings
- [LibreTranslate Go](https://github.com/SnakeSel/libretranslate) - LibreTranslate Golang bindings
- [LibreTranslator](https://gitlab.com/BeowuIf/libretranslator) - LibreTranslate Android app
- [LiTranslate](https://community.libretranslate.com/t/litranslate-ios-app/333) - iOS LibreTranslate client

## Contributing
Contributions are welcome! Available issues are on the [GitHub issues page](https://github.com/argosopentech/argos-translate/issues). Contributions of code, data, and pre-trained models can all be accepted.

## Support
For support please use the [LibreTranslate Forum](https://community.libretranslate.com/c/argos-translate/5) or [GitHub Issues](https://github.com/argosopentech/argos-translate/issues).

For questions about [CTranslate2](https://github.com/OpenNMT/CTranslate2) or general machine translation research the [OpenNMT Forum](https://forum.opennmt.net/) is a good resource.

## Services
Custom models trained on your own data are available for $1000/language (negotiable).

[I am also available for hire](https://www.argosopentech.com/about/) to do support, consulting, or custom software development.

## Donate
If you find this software useful donations are appreciated.
- [GitHub Sponsor](https://github.com/sponsors/argosopentech)
- [PayPal](https://www.paypal.com/biz/fund?id=MCCFG437JP9PJ)
- Bitcoin: 16UJrmSEGojFPaqjTGpuSMNhNRSsnspFJT
- Ethereum: argosopentech.eth

Paid supporters receive priority support.

#### Hosting affiliate links
You can help support Argos Translate financially by purchasing hosting through these referral links:
- [Vast.ai](http://vast.ai/?ref=24817) - Cheap GPU rentals
- [DigitalOcean](https://m.do.co/c/a1af57be6e3f) - Best all around hosting
- [Sharktech](https://portal.sharktech.net/aff.php?aff=1181) - Cheap bandwith
- [Time4VPS](https://www.time4vps.com/?affid=6929) - Cheap storage

#### Argos Translate 2 beta
A beta version of Argos Translate 2 is available to install from source from the [v2 branch on GitHub](https://github.com/argosopentech/argos-translate/tree/v2). Argos Translate 2 has a [multilingual model architecture](https://community.libretranslate.com/t/multilingual-translation-with-ctranslate2-and-pre-trained-fairseq-models/178/), more extensive unit testing, and a more experimental orientation.

## Contributing
Contributions are welcome! Bug reports, pull requests, documentation writing, and feature ideas are all appreciated.

## License
Argos Translate is dual licensed under either the [MIT License](https://github.com/argosopentech/argos-translate/blob/master/LICENSE) or [Creative Commons CC0](https://creativecommons.org/share-your-work/public-domain/cc0/).
