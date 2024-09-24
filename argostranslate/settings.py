import json
import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict

"""
Argos Translate can be configured using either environment variables or json file

Configurations from environment variables supersede configurations from the JSON file.

### Environment variables
```
export ARGOS_DEBUG="0"
export ARGOS_PACKAGE_INDEX="https://raw.githubusercontent.com/argosopentech/argospm-index/main/"
export ARGOS_PACKAGES_DIR="/home/<username>/.local/share/argos-translate/packages/"
export ARGOS_DEVICE_TYPE="cpu"

```

### JSON 

# $HOME/.config/argos-translate/settings.json
```
{
    "ARGOS_DEBUG": "0",
    "ARGOS_PACKAGES_INDEX": "https://raw.githubusercontent.com/argosopentech/argospm-index/main/",
    "ARGOS_PACKAGE_DIR": "/home/<username>/.local/share/argos-translate/packages/",
    "ARGOS_DEVICE_TYPE": "cpu"
}
```
"""

"""
Importing argostranslate.settings will create the Argos Translate data directory (~/.local/share/argos-translate),
the Argos Translate config directory (~/.config/argos-translate),
and the Argos Translate cache directory (~/.local/cache/argos-translate) if they do not already exist.
"""

home_dir = Path.home()

if "SNAP" in os.environ:
    home_dir = Path(os.environ["SNAP_USER_DATA"])

data_dir = (
    Path(os.getenv("XDG_DATA_HOME", default=home_dir / ".local" / "share"))
    / "argos-translate"
)
os.makedirs(data_dir, exist_ok=True)

# ARGOS_TRANSLATE_PACKAGE_DIR deprecated 1.2.0
legacy_package_data_dir = Path(
    os.getenv("ARGOS_TRANSLATE_PACKAGE_DIR", default=data_dir / "packages")
)

config_dir = (
    Path(os.getenv("XDG_CONFIG_HOME", default=home_dir / ".config")) / "argos-translate"
)
os.makedirs(config_dir, exist_ok=True)

cache_dir = (
    Path(os.getenv("XDG_CACHE_HOME", default=home_dir / ".local" / "cache"))
    / "argos-translate"
)
os.makedirs(cache_dir, exist_ok=True)


downloads_dir = cache_dir / "downloads"
os.makedirs(downloads_dir, exist_ok=True)

settings_file = config_dir / "settings.json"


def load_settings_dict() -> Dict[str, Any]:
    settings_dict = dict()
    if settings_file.exists():
        try:
            with open(settings_file, "r") as settings_file_data:
                settings_dict = json.load(settings_file_data)
            assert isinstance(
                settings_dict, dict
            ), "settings.json should contain a dictionary"
        except FileNotFoundError as e:
            print(f"{settings_file} not found : FileNotFoundError {e}")
        except json.JSONDecodeError as e:
            print(f"Error decoding {settings_file}: JSONDecodeError {e}")
    return settings_dict


def get_setting(key: str, default=None):
    """Gets a setting from either environment variables or settings.json

    Settings from environment variables take precedence over settings.json

    Args:
        key (str): Key value
        default: The default setting value. Defaults to None.

    Returns:
        The setting value
    """
    value_from_environment = os.getenv(key)
    value_from_file = load_settings_dict().get(key)
    if value_from_environment is not None:
        return value_from_environment
    else:
        if value_from_file is not None:
            return value_from_file
        return default


def set_setting(key: str, value):
    """Sets a setting in the settings.json file.

    Args:
        key (str): The key to set.
        value: The value to set.
    """
    settings = load_settings_dict()
    settings[key] = value
    with open(settings_file, "w") as settings_file_data:
        json.dump(settings, settings_file_data, indent=4)


TRUE_VALUES = ["1", "TRUE", "True", "true", 1, True]


debug = get_setting("ARGOS_DEBUG") in TRUE_VALUES

dev_mode = get_setting("ARGOS_DEV_MODE") in TRUE_VALUES

package_index = get_setting(
    "ARGOS_PACKAGE_INDEX",
    default="https://raw.githubusercontent.com/argosopentech/argospm-index/main/",
)

package_data_dir = Path(
    get_setting("ARGOS_PACKAGES_DIR", default=data_dir / "packages")
)
os.makedirs(package_data_dir, exist_ok=True)


downloads_dir = cache_dir / "downloads"
os.makedirs(downloads_dir, exist_ok=True)

if not dev_mode:
    remote_repo = os.getenv(
        "ARGOS_PACKAGE_INDEX",
        default="https://raw.githubusercontent.com/argosopentech/argospm-index/main",
    )
else:
    remote_repo = os.getenv(
        "ARGOS_PACKAGE_INDEX",
        default="https://raw.githubusercontent.com/argosopentech/argospm-index-dev/main",
    )

remote_package_index = package_index + "index.json"

local_package_index = data_dir / "index.json"

experimental_enabled = os.getenv("ARGOS_EXPERIMENTAL_ENABLED") in TRUE_VALUES

stanza_available = os.getenv("ARGOS_STANZA_AVAILABLE") in (TRUE_VALUES + [None])

# Supported values: "cpu" and "cuda"
device = get_setting("ARGOS_DEVICE_TYPE", "cpu")

# https://opennmt.net/CTranslate2/python/ctranslate2.Translator.html
inter_threads = int(get_setting("ARGOS_INTER_THREADS", "1"))
intra_threads = int(get_setting("ARGOS_INTRA_THREADS", "0"))


class ModelProvider(Enum):
    OPENNMT = 0
    LIBRETRANSLATE = 1
    OPENAI = 2


model_mapping = {
    "OPENNMT": ModelProvider.OPENNMT,
    "LIBRETRANSLATE": ModelProvider.LIBRETRANSLATE,
    "OPENAI": ModelProvider.OPENAI,
}
model_provider = model_mapping[get_setting("ARGOS_MODEL_PROVIDER", default="OPENNMT")]


# Sentence boundary detection
class ChunkType(Enum):
    DEFAULT = 0
    ARGOSTRANSLATE = 1
    NONE = 2  # No sentence splitting


chunk_type_mapping = {
    "DEFAULT": ChunkType.DEFAULT,
    "ARGOSTRANSLATE": ChunkType.ARGOSTRANSLATE,
    "NONE": ChunkType.NONE,
}
chunk_type = chunk_type_mapping[get_setting("ARGOS_CHUNK_TYPE", default="DEFAULT")]
if chunk_type == ChunkType.DEFAULT:
    chunk_type = ChunkType.ARGOSTRANSLATE


libretranslate_api_key = get_setting("LIBRETRANSLATE_API_KEY", None)
openai_api_key = get_setting("OPENAI_API_KEY", None)


argos_translate_about_text = (
    "Argos Translate is an open source neural machine "
    + "translation application created by Argos Open "
    + "Technologies, LLC (www.argosopentech.com). "
)

# Fix Intel bug
# https://github.com/argosopentech/argos-translate/issues/40
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"
# Will search all of these directories for packages
package_dirs = [package_data_dir]
if "SNAP" in os.environ:
    # Packages bundled with snap
    snap_package_dir = Path(os.environ["SNAP"]) / "snap_custom" / "packages"
    if os.path.isdir(snap_package_dir):
        package_dirs.append(snap_package_dir)

    # Packages loaded from a content snap
    content_snap_packages = (
        Path(os.environ["SNAP"]) / "snap_custom" / "content_snap_packages"
    )
    if os.path.isdir(content_snap_packages):
        for package_dir in content_snap_packages.iterdir():
            if package_dir.is_dir():
                package_dirs.append(package_dir)
