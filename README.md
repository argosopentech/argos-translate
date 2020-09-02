# Argos Translate

Open source offline translation app written in Python. Uses OpenNMT for translations, NLTK Punkt for sentence boundary detection, and Tkinter for GUI.

Argos Translate supports installing model files which are a zip archive with an ".argosmodel" extension that contain an OpenNMT CTranslate model, a SentencePiece model, and metadata about the model. Pretrained models can be downloaded [here](https://drive.google.com/drive/folders/11wxM3Ze7NCgOk_tdtRjwet10DmtvFu3i). To install a model click "Install model" from the toolbar in the GUI and select your model file. By default models are stored in ~/.argos-translate, this can be changed in settings.py.

## Models
The models are a work in progress and are being trained using [this](https://github.com/argosopentech/onmt-models) training script. 

Currently there are models available to translate between:
- English
- Spanish

![Screenshot](/img/Screenshot.png)

## Installation
Argos Translate is being developed/tested to run on Linux. However since it is written in Python it should run with minimal modifications on other platforms.

### Python installation
1. Clone this repo:
```
git clone https://github.com/argosopentech/argos-translate.git
cd argos-translate
```
2. Make a virtual environment to install it in (optional):
```
virtualenv env
source env/bin/activate
```
3. Install this package with pip:
```
pip install .
```

### Snap installation
1. Install [snapd](https://snapcraft.io/docs/installing-snapd) if it isn't already installed.
2. Using snapd install snapcraft:
```
sudo snap install snapcraft
```
3. Clone this repo:
```
git clone https://github.com/argosopentech/argos-translate.git
cd argos-translate
```
4. From the root directory of this project build the snap package:
```
snapcraft
```
Any unzipped package files in package/ will be automatically included in the snap archive.
5. Install the snap package:
```
sudo snap install --devmode argos-translate_<version information>.snap
```
6. Run Argos Translate!
```
argos-translate
```

Dual licensed under the [MIT License](https://github.com/argosopentech/argos-translate/blob/master/LICENSE) and [CC0](https://creativecommons.org/share-your-work/public-domain/cc0/).
