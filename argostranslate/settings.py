from pathlib import Path
import os
from enum import Enum

TRUE_VALUES = ["1", "TRUE", "True", "true"]

debug = os.getenv("ARGOS_DEBUG") in TRUE_VALUES

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

package_data_dir = Path(os.getenv("ARGOS_PACKAGES_DIR", default=data_dir / "packages"))
os.makedirs(package_data_dir, exist_ok=True)

downloads_dir = cache_dir / "downloads"
os.makedirs(downloads_dir, exist_ok=True)

package_index = os.getenv(
    "ARGOS_PACKAGE_INDEX",
    default="https://www.argosopentech.com/argospm/index/",
)

remote_package_index = package_index + "index.json"

local_package_index = cache_dir / "index.json"


class ModelProvider(Enum):
    OPENNMT = 0
    LIBRETRANSLATE = 1
    OPENAI = 2


model_mapping = {
    "OPENNMT": ModelProvider.OPENNMT,
    "LIBRETRANSLATE": ModelProvider.LIBRETRANSLATE,
    "OPENAI": ModelProvider.OPENAI,
}
model_provider = model_mapping[os.getenv("ARGOS_MODEL_PROVIDER", default="OPENNMT")]

libretranslate_api_key = os.getenv("LIBRETRANSLATE_API_KEY", None)
openai_api_key = os.getenv("OPENAI_API_KEY", None)


package_dirs = [package_data_dir]

about_text = (
    "Argos Translate is an open source neural machine "
    + "translation application created by Argos Open "
    + "Technologies, LLC (www.argosopentech.com). "
)

# Fix Intel bug
# https://github.com/argosopentech/argos-translate/issues/40
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

# Supported values: cpu and cuda
device = os.environ.get("ARGOS_DEVICE_TYPE", "cpu")
