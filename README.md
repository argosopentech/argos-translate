# Argos Translate
[Demo](https://libretranslate.com) | [Website](https://www.argosopentech.com) | [Docs](https://argos-translate.readthedocs.io) |  [Forum](https://community.libretranslate.com/c/argos-translate/5) | [Video intro](https://odysee.com/@argosopentech:7/Machine-Translation-in-Argos-Translate-2021:5) | [GitHub](https://github.com/argosopentech/argos-translate)

Open-source offline translation library written in Python

Argos Translate uses [OpenNMT](https://opennmt.net/) for translations, [SentencePiece](https://github.com/google/sentencepiece) for tokenization, [Stanza](https://github.com/stanfordnlp/stanza) for sentence boundary detection, and [PyQt](https://riverbankcomputing.com/software/pyqt/intro) for GUI. Argos Translate can be used as either a Python library, command-line, or GUI application. [LibreTranslate](https://libretranslate.com) is an API and web-app built on top of Argos Translate.

Argos Translate supports installing model files which are a zip archive with a ".argosmodel" extension with the data needed for translation.

Argos Translate also manages automatically pivoting through intermediate languages to translate between languages that don't have a direct translation between them installed. For example, if you have a es ➔ en and en ➔ fr translation installed you are able to translate from es ➔ fr as if you had that translation installed. This allows for translating between a wide variety of languages at the cost of some loss of translation quality.

### Supported languages
Arabic, Azerbaijani, Chinese, Czech, Dutch, English, Esperanto, Finnish, French, German, Greek, Hindi, Hungarian, Indonesian, Irish, Italian, Japanese, Korean, Persian, Polish, Portuguese, Russian, Slovak, Spanish, Swedish, Turkish, Ukrainian, Vietnamese

- [Request a language](https://github.com/argosopentech/argos-translate/discussions/91)

## [Models](https://www.argosopentech.com/argospm/index/)
- [Browse models](https://www.argosopentech.com/argospm/index/)
- [P2P download (IPFS and BitTorrent)](/p2p/README.md)
- [Training scripts](https://github.com/argosopentech/argos-train)
- [Google Drive download](https://drive.google.com/drive/folders/11wxM3Ze7NCgOk_tdtRjwet10DmtvFu3i)

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
from argostranslate import package, translate

# Download and install .argosmodel package
available_packages = package.get_available_packages()
available_package_en_es = list(filter(
	lambda x: x.from_code == "en" and x.to_code == "es",
	available_packages))[0]
download_path = available_package_en_es.download()
package.install_from_path(download_path)

installed_languages = translate.get_installed_languages()

# >>> [lang.code for lang in installed_languages]
# ['en', 'es']

translation_en_es = installed_languages[0].get_translation(installed_languages[1])
translatedText = translation_en_es.translate("Hello World!")

# >>> print(translatedText)
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

### GPU Acceleration

To enable GPU support, you need to set the `ARGOS_DEVICE_TYPE` env variable to `cuda` or `auto`.

```
$ ARGOS_DEVICE_TYPE=cuda argos-translate --from-lang en --to-lang es "Hello World"
Hola Mundo
```

The above env variable instructs [CTranslate2](https://github.com/OpenNMT/CTranslate2) to use cuda.
if you encounter any issues with GPU inference please reference the [CTranslate2 documentation](https://github.com/OpenNMT/CTranslate2#what-hardware-is-supported).


### [Install on Linux with Snapcraft](https://github.com/argosopentech/argos-translate-gui/blob/main/README.md#snapcraft)

### Run Argos Translate!

#### GUI
Run the GUI version of Argos Translate.

```
argos-translate-gui
```

When installing with snap a .desktop file should also be installed which will make Argos Translate available from the desktop menu.

Languages are chosen as drop down choices. More languages pairs can be installed.

The left text box translates into the right box.

Example workflow translating from Vietnamese into English:

1. Set the left drop down to `Vietnamese` and the right drop down to `English`.
1. Replace the default text `Text to translate from` in the left text box with some text in Vietnamese. A quick way to do this is to click in the left text box and press the keyboard shortcut `CTRL+a` to select all and then `CTRL+v` to paste.
1. Wait patiently.
1. When text appears in the right text box, read the translation!

If the output looks similar to the input, try changing the origin language as some languages appear similar if you are unfamiliar with them.

### [Command Line](https://argos-translate.readthedocs.io/en/latest/source/cli.html)

Run the command line version of Argos Translate.
```
argos-translate
```

Translate a string from English to Spanish.

Note: If you do not have the language pair that you are calling installed, you will get a `Traceback` error.

```
argos-translate --from-lang en --to-lang es "Hello World."
Hola Mundo
```

Translate longer text piped into `argos-translate`.

```
echo "Text to translate" | argos-translate --from-lang en --to-lang es
Texto para traducir
```

### HTML Translation
The [translate-html](https://github.com/argosopentech/translate-html) library is built on top of Argos Translate and [Beautiful Soup](https://beautiful-soup-4.readthedocs.io/en/latest/) and parses and translates HTML. The LibreTranslate API also has support for translating HTML.


### Files Translation
The [argos-translate-files](https://github.com/dingedi/argos-translate-files) library is built on top of Argos Translate and parses and translates files. The LibreTranslate API also has support for translating files.

## Uninstall

If you want to uninstall Argos Translate, you may choose the applicable method.

### Uninstall PYPI/pip package

If you installed Argos Translate via `pip` you can uninstall it using

``` shell
python3 -m pip uninstall argostranslate
```

You may choose to also delete temporary and cached files:

``` shell
rm -r ~/.local/cache/argos-translate
rm -r ~/.local/share/argos-translate
```

### Uninstall Snap

The following command will uninstall the snap package.

``` shell
sudo snap remove argos-translate argos-translate-base-langs
```

If you installed additional language packs, you might want to remove them as well, e.g.

``` shell
sudo snap remove argos-translate-de-en

```

## Adding language pair models from the graphical interface

Language pairs are on average 100MB each.

### Installing new pairs through the GUI

1. Open Argos Translate: `argos-translate-gui`
1. Click on the `Manage Packages` menu item.
1. Click on the `Download packages` button.
1. Click on the down arrow beside a language pair that you want to add.
1. Wait for the hourglass icon to change into a check mark icon.
1. Repeat the last two steps until you have all of the language pairs that you want.
1. Click on the `X` in the top right to close the `Download packages` window.
1. Click on the `X` in the top right to close the `Manage Packages` window.

Note: The `Download packages` screen does not seem to have a scroll bar so you will probably need to follow the next set of instructions to import new pairs through the GUI.

### Importing new pairs through the GUI

1. Download or make new pairs.  Model links can be downloaded from [this page](https://www.argosopentech.com/argospm/index/) or [this JSON file](https://raw.githubusercontent.com/argosopentech/argospm-index/main/index.json).
1. Open Argos Translate: `argos-translate-gui`
1. Click on the `Manage Packages` menu item.
1. Click on the `Install package file` button.
1. Navigate to where you downloaded the new language pairs, click on the `.argosmodel` file, and click on the `Open` button.
1. Repeat the last two steps until you have all of the language pairs that you want.
1. Click on the `X` in the top right to close the `Manage Packages` window.

### Importing new pairs through the CLI

1. Update list of available language pairs: `argospm update`
1. List all available language pairs: `argospm search`
1. Install new pair syntax: `argospm install *lang_pair_name*`

For example, install Turkish to English pair: `argospm install translate-tr_en`

Optionally, you could install all language pairs using BASH.

    for i in $(argospm search | sed 's/:.*$//g'); do argospm install $i ; done

### Removing a pair through the GUI

1. Open Argos Translate: `argos-translate-gui`
1. Click on the `Manage Packages` menu item.
1. Click on the trash can icon besides the pair you want to remove.
1. Click on the `X` in the top right to close the `Manage Packages` window.

### Removing a pair through the CLI

1. Remove the Turkish to English pair: `argospm remove translate-tr_en`

Optionally, you could remove all language pairs using BASH if you need to free space fast.

    for i in $(argospm list); do argospm remove $i ; done

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

Managed hosting for $1000/mo.

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
- Cheap Eth: 0x996133E61b81c300a37ACa9b24898685eB872b61

Paid supporters receive priority support.

You can also support the project by purchasing [DigitalOcean](https://www.digitalocean.com/) hosting with the [Argos Open Tech referral link](https://m.do.co/c/a1af57be6e3f) which helps to offset [CDN hosting costs](https://community.libretranslate.com/t/estimating-libretranslate-usage-from-cdn-traffic/78/7).

## License
Dual licensed under either the [MIT License](https://github.com/argosopentech/argos-translate/blob/master/LICENSE) or [CC0](https://creativecommons.org/share-your-work/public-domain/cc0/).
