import json
import os
import pathlib
from enum import Enum
from pathlib import Path

"""
Argos Translate can be configured using either environment variables or json file

### Environment variables
```
export ARGOS_DEBUG="0"
export ARGOS_PACKAGE_INDEX="https://raw.githubusercontent.com/argosopentech/argospm-index/v2/"
export ARGOS_PACKAGES_DIR="/home/<username>/.local/share/argos-translate/packages/"
export ARGOS_DEVICE_TYPE="cpu"

```

### JSON 

# ~/.config/argos-translate/settings.json
```
{
    "ARGOS_DEBUG": "0",
    "ARGOS_PACKAGES_INDEX": "https://raw.githubusercontent.com/argosopentech/argospm-index/v2/",
    "ARGOS_PACKAGE_DIR": "/home/<username>/.local/share/argos-translate/packages/",
    "ARGOS_DEVICE_TYPE": "cpu"
}
```
"""

home_dir = Path.home()

data_dir = (
    Path(os.getenv("XDG_DATA_HOME", default=home_dir / ".local" / "share"))
    / "argos-translate"
)
os.makedirs(data_dir, exist_ok=True)

config_dir = (
    Path(os.getenv("XDG_CONFIG_HOME", default=home_dir / ".config")) / "argos-translate"
)
os.makedirs(config_dir, exist_ok=True)

cache_dir = (
    Path(os.getenv("XDG_CACHE_HOME", default=home_dir / ".local" / "cache"))
    / "argos-translate"
)
os.makedirs(cache_dir, exist_ok=True)

settings_file = config_dir / "settings.json"


settings_object = dict()
if settings_file.exists():
    with open(settings_file) as settings_file_data:
        settings_object = json.load(open(settings_file))


def get_setting(key, default=None):
    value_from_environment = os.getenv(key)
    value_from_file = settings_object.get(key)
    if value_from_environment is not None:
        return value_from_environment
    else:
        if value_from_file is not None:
            return value_from_file
        return default


is_debug = get_setting("ARGOS_DEBUG") in ["1", "TRUE", "True", "true", 1, True]

package_index = get_setting(
    "ARGOS_PACKAGE_INDEX",
    default="https://raw.githubusercontent.com/argosopentech/argospm-index/v2/index.json",
)

packages_dir = Path(get_setting("ARGOS_PACKAGES_DIR", default=data_dir / "packages"))
os.makedirs(packages_dir, exist_ok=True)


downloads_dir = cache_dir / "downloads"
os.makedirs(downloads_dir, exist_ok=True)


remote_package_index = package_index + "index.json"

local_package_index = data_dir / "index.json"

# Supported values: "cpu" and "cuda"
device = get_setting("ARGOS_DEVICE_TYPE", "cpu")


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
chunk_type = chunk_type_mapping[os.getenv("ARGOS_CHUNK_TYPE", "DEFAULT")]
if chunk_type == ChunkType.DEFAULT:
    chunk_type = ChunkType.ARGOSTRANSLATE


libretranslate_api_key = get_setting("LIBRETRANSLATE_API_KEY", None)
openai_api_key = get_setting("OPENAI_API_KEY", None)


argos_translate_about_text = (
    "Argos Translate is an open source neural machine "
    + "translation application created by Argos Open "
    + "Technologies, LLC (www.argosopentech.com). "
)

version_file = pathlib.Path(__file__).parent.resolve() / "__version__"
with open(version_file) as version_file_data:
    argos_version = version_file_data.read().strip()

# Fix Intel bug
# https://github.com/argosopentech/argos-translate/issues/40
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"
