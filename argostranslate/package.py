from __future__ import annotations

import copy
import json
import pathlib
import shutil
import urllib.request
import uuid
import zipfile
from pathlib import Path
from threading import Lock

import packaging.version

import argostranslate.networking
import argostranslate.settings
from argostranslate.tokenizer import BPETokenizer, SentencePieceTokenizer
from argostranslate.utils import error, info, warning

# TODO: Upgrade packages

"""
## `package` module example usage
```
from argostranslate import package

# Update package definitions from remote
package.update_package_index()

# Load available packages from local package index
available_packages = package.get_available_packages()

# Download and install all available packages
for available_package in available_packages:
    available_package.install()
```
"""

# Threading logic
# Hold lock while installing or uninstalling packages
package_lock = Lock()


class IPackage:
    """A package, can be either installed locally or available from a remote package index.

    Attributes:
        package_path: The path to the installed package. None if not installed.

        package_version: The version of the package.

        argos_version: The version of Argos Translate the package is intended for.

        from_code: The code of the language the package translates from.

        from_name: Human readable name of the language the package translates from.

        to_code: The code of the language the package translates to.

        to_name: Human readable name of the language the package translates to.

        links: A list of links to download the package


    Packages are a zip archive of a directory with metadata.json
    in its root the .argosmodel file extension. By default a
    OpenNMT CTranslate2 directory named model/ is expected in the root directory
    along with a sentencepiece model named sentencepiece.model or a bpe.model
    for tokenizing and Stanza data for sentence boundary detection.
    Packages may also optionally have a README.md in the root.

    from_code and to_code should be ISO 639 codes if applicable.

    Example metadata.json
    {
        "package_version": "1.0",
        "argos_version": "1.0",
        "from_code": "en",
        "from_name": "English",
        "to_code": "es",
        "to_name": "Spanish",
        "links": ["https://example.com/en_es.argosmodel"]
    }
    """

    code: str | None
    type: str | None
    name: str | None
    package_path: Path | None
    package_version: str | None
    argos_version: str | None
    links: list[str]
    dependencies: list
    languages: list
    source_languages: list
    target_languages: list
    from_code: str | None
    from_name: str | None
    to_code: str | None
    to_name: str | None

    def set_metadata(self, metadata: dict):
        """Loads package metadata from a JSON object.

        Args:
            metadata: A json object from json.load

        """
        info("Load metadata from package json", metadata)

        self.code = metadata.get("code")
        self.type = metadata.get("type")
        self.name = metadata.get("name")
        self.package_version = metadata.get("package_version")
        self.argos_version = metadata.get("argos_version")
        self.links = metadata.get("links", list())
        self.dependencies = metadata.get("dependencies", list())
        self.languages = metadata.get("languages", list())
        self.source_languages = metadata.get("source_languages", list())
        self.target_languages = metadata.get("target_languages", list())
        self.from_code = metadata.get("from_code")
        self.from_name = metadata.get("from_name")
        self.to_code = metadata.get("to_code")
        self.to_name = metadata.get("to_name")
        self.target_prefix = metadata.get("target_prefix", "")

        if (
            self.code is None
            and self.from_code is not None
            and self.to_code is not None
        ):
            self.code = f"translate-{self.from_code}_{self.to_code}"

        self.source_languages += copy.deepcopy(self.languages)
        self.target_languages += copy.deepcopy(self.languages)
        if self.from_code is not None:
            from_lang = dict()
            from_lang["code"] = self.from_code
            if self.from_name is not None:
                from_lang["name"] = self.from_name
            self.languages.append(from_lang)
            self.source_languages.append(from_lang)
        if self.to_code is not None:
            to_lang = dict()
            to_lang["code"] = self.to_code
            if self.to_name is not None:
                to_lang["name"] = self.to_name
            self.languages.append(to_lang)
            self.target_languages.append(to_lang)

        """Languages must have a code"""
        self.source_languages = list(
            filter(lambda lang: lang.get("code") is not None, self.source_languages)
        )
        self.target_languages = list(
            filter(lambda lang: lang.get("code") is not None, self.target_languages)
        )

    def load_metadata_from_json(self, metadata):
        """Deprecated use set_metadata instead"""
        self.set_metadata(metadata)

    def get_readme(self):
        """Returns the text of the README.md in this package.

        Returns:
            The text of the package README.md, None
                if README.md can't be read

        """
        raise NotImplementedError()

    def get_description(self):
        raise NotImplementedError()

    def __eq__(self, other):
        return self.code == other.code

    def __str__(self):
        if self.name is not None:
            return self.name
        if self.code is not None:
            return self.code
        if self.type is not None:
            return self.type
        return "Argos Translate Package"

    def __repr__(self):
        if self.code is not None:
            return self.code
        return str(self)


def update_package_index():
    """Downloads remote package index"""
    package_index_data = argostranslate.networking.get(
        argostranslate.settings.remote_package_index
    )
    with package_lock:
        with open(argostranslate.settings.local_package_index, "wb") as f:
            f.write(package_index_data)


def get_available_packages():
    """Returns a list of AvailablePackages from the package index."""
    if not argostranslate.settings.local_package_index.exists():
        update_package_index()
    with open(argostranslate.settings.local_package_index) as index_file:
        index = json.load(index_file)
        available_packages = list()
        for metadata in index:
            package = AvailablePackage(metadata)
            available_packages.append(package)
        info("get_available_packages", available_packages)
        return available_packages


def install_from_path(path: pathlib.Path):
    """Install a package file (zip archive ending in .argosmodel).

    Args:
        path (pathlib): The path to the .argosmodel file to install.

    """
    with package_lock:
        if not zipfile.is_zipfile(path):
            raise Exception("Not a valid Argos Model (must be a zip archive)")
        with zipfile.ZipFile(path, "r") as zip:
            zip.extractall(path=argostranslate.settings.packages_dir)
            info("Installed package from path", path)


class AvailablePackage(IPackage):
    """A package available for download and installation"""

    def __init__(self, metadata):
        """Creates a new AvailablePackage from a metadata object"""
        self.set_metadata(metadata)

    def get_dependencies(self):
        return list(
            filter(
                lambda available_package: available_package.code in self.dependencies,
                get_available_packages(),
            )
        )

    def download(self):
        """Downloads the AvailablePackage and returns its path"""
        if len(self.links) == 0:
            return None
        filename = f"{self.code}-{str(uuid.uuid4())}.argosmodel"
        filepath = argostranslate.settings.downloads_dir / filename
        data = argostranslate.networking.get_from(self.links)
        if data is not None:
            with open(filepath, "wb") as f:
                f.write(data)
            return filepath
        return None

    def install(self):
        for dependency in self.get_dependencies():
            dependency.install()
        download_path = self.download()
        if download_path is not None:
            install_from_path(download_path)
            download_path.unlink()

    def get_description(self):
        return self.name


class Package(IPackage):
    """An installed package"""

    package_path: Path

    def __init__(self, package_path: Path):
        """Create a new Package from path.

        Args:
            package_path: Path to installed package directory.

        """
        self.package_path = package_path
        metadata_path = package_path / "metadata.json"
        if not metadata_path.exists():
            raise FileNotFoundError(
                "Error opening package at " + str(metadata_path) + " no metadata.json"
            )
        with open(metadata_path) as metadata_file:
            metadata = json.load(metadata_file)
            self.set_metadata(metadata)
        if (
            self.argos_version is not None
            and self.argos_version > argostranslate.settings.argos_version
        ):
            warning(
                f"Package version {self.argos_version} is newer than Argos Translate version {argostranslate.settings.argos_version}"
            )
            self.set_metadata(metadata)

        sp_model_path = package_path / "sentencepiece.model"
        bpe_model_path = package_path / "bpe.model"

        if sp_model_path.exists():
            self.tokenizer = SentencePieceTokenizer(sp_model_path)
        elif bpe_model_path.exists():
            self.tokenizer = BPETokenizer(bpe_model_path, self.from_code, self.to_code)

    def update(self):
        """Update the package if a newer version is available."""
        for available_package in get_available_packages():
            if (
                available_package.from_code == self.from_code
                and available_package.to_code == self.to_code
            ):
                if packaging.version.parse(
                    available_package.package_version
                ) > packaging.version.parse(self.package_version):
                    new_package_path = available_package.download()
                    uninstall(self)
                    install_from_path(new_package_path)

    def get_readme(self) -> str | None:
        """Returns the text of the README.md in this package.

        Returns:
            The text of the package README.md, None
                if README.md can't be read

        """
        if self.package_path is None:
            return None
        readme_path = self.package_path / "README.md"
        if not readme_path.exists():
            return None
        with open(readme_path, "r") as readme_file:
            return readme_file.read()

    def get_description(self):
        return self.get_readme()


def get_installed_packages(packages_dir: Path | None = None) -> list[Package]:
    """Return a list of installed Packages

    Looks for packages in <home>/.argos-translate/local/share/packages by
    default. Will also look in the directory specified
    in the ARGOS_TRANSLATE_PACKAGE_DIR environment variable
    if it is set.

    Args:
        path: Path to look for installed package directories in.
            Defaults to the path in argostranslate.settings.

    """
    if packages_dir is None:
        packages_dir = argostranslate.settings.packages_dir
    with package_lock:
        installed_packages = list()
        for path in packages_dir.iterdir():
            if path.is_dir():
                installed_packages.append(Package(path))
        info("get_installed_packages", installed_packages)
        return installed_packages


def uninstall(pkg):
    """Uninstalls a package.

    Args:
        pkg (Package): The package to uninstall

    """
    with package_lock:
        info("Uninstalled package", pkg)
        shutil.rmtree(pkg.package_path)
