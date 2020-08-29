# Argos-Translate

Open source offline translation app written in Python. Uses OpenNMT for translations and Tkinter for GUI.

Supports translations between:
- English
- Spanish

![Screenshot](/img/Screenshot.png)

## Installation
Argos Translate is being developed/tested to run on Linux in a Snap container. However since it is written in Python it should run with minimal modifications on other platforms.

### Snap installation
1. Install [snapd](https://snapcraft.io/docs/installing-snapd) if it isn't already installed.
2. Using snapd install snapcraft:
    sudo snap install snapcraft
3. Clone this repo:
    git clone https://github.com/argosopentech/argos-translate.git
    cd argos-translate
4. From the root directory of this project build the snap package:
    snapcraft
5. Install the snap package:
    sudo snap install --devmode argos-translate_<version information>.snap
6. Run Argos Translate!
    argos-translate

### Python installation
1. Clone this repo:
    git clone https://github.com/argosopentech/argos-translate.git
    cd argos-translate
2. Make a virtual environment to install it in (optional):
    virtualenv env
    source env/bin/activate
3. Install this package with pip:
    pip install .
4. This will just install the python code for the gui and running models. To get the models download [models.zip here](https://drive.google.com/drive/folders/11wxM3Ze7NCgOk_tdtRjwet10DmtvFu3i), unzip it, and run `argos-translate` from the same directory as the models/ directory. 

## Models
The models are a work in progress and are being trained using [this](https://github.com/argosopentech/onmt-models) training script. You can customize what directory your models are stored in in the top of argos_translate/translate.py or use the training script to train your own models.

Dual licensed under the [MIT License](https://github.com/argosopentech/argos-translate/blob/master/LICENSE) and [CC0](https://creativecommons.org/share-your-work/public-domain/cc0/).
