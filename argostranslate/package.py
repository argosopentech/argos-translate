from __future__ import annotations

import copy
import json
import shutil
import urllib.request
import zipfile
from pathlib import Path
from threading import Lock

from argostranslate import networking, settings
from argostranslate.utils import error, info

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
    download_path = available_package.download()
    package.install_from_path(download_path)
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
    along with a sentencepiece model named sentencepiece.model
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

    code: str
    package_path: Path
    package_version: str
    argos_version: str
    from_code: str
    from_name: str
    from_codes: list
    to_code: str
    to_codes: list
    to_name: str
    links: list
    type: str
    languages: list
    dependencies: list
    source_languages: list
    target_languages: list
    links: list[str]

    def load_metadata_from_json(self, metadata):
        """Loads package metadata from a JSON object.

        Args:
            metadata: A json object from json.load

        """
        self.code = metadata.get("code")
        self.package_version = metadata.get("package_version", "")
        self.argos_version = metadata.get("argos_version", "")
        self.from_code = metadata.get("from_code")
        self.from_name = metadata.get("from_name", "")
        self.from_codes = metadata.get("from_codes", list())
        self.to_code = metadata.get("to_code")
        self.to_codes = metadata.get("to_codes", list())
        self.to_name = metadata.get("to_name", "")
        self.links = metadata.get("links", list())
        self.type = metadata.get("type", "translate")
        self.languages = metadata.get("languages", list())
        self.dependencies = metadata.get("dependencies", list())
        self.source_languages = metadata.get("source_languages", list())
        self.target_languages = metadata.get("target_languages", list())

        # Add all package source and target languages to
        # source_languages and target_languages
        if self.from_code is not None or self.from_name is not None:
            from_lang = dict()
            if self.from_code is not None:
                from_lang["code"] = self.from_code
            if self.from_name is not None:
                from_lang["name"] = self.from_name
            self.source_languages.append(from_lang)
        if self.to_code is not None or self.to_name is not None:
            to_lang = dict()
            if self.to_code is not None:
                to_lang["code"] = self.to_code
            if self.to_name is not None:
                to_lang["name"] = self.to_name
            self.source_languages.append(to_lang)
        self.source_languages += copy.deepcopy(self.languages)
        self.target_languages += copy.deepcopy(self.languages)

    def get_readme(self) -> str:
        """Returns the text of the README.md in this package.

        Returns:
            The text of the package README.md, None
                if README.md can't be read

        """
        raise NotImplementedError()

    def get_description(self):
        raise NotImplementedError()

    def __eq__(self, other):
        return (
            self.package_version == other.package_version
            and self.argos_version == other.argos_version
            and self.from_code == other.from_code
            and self.from_name == other.from_name
            and self.to_code == other.to_code
            and self.to_name == other.to_name
        )

    def __repr__(self):
        if len(self.from_name) > 0 and len(self.to_name) > 0:
            return "{} -> {}".format(self.from_name, self.to_name)
        elif self.type:
            return self.type
        return ""

    def __str__(self):
        return repr(self).replace("->", "→")


class Package(IPackage):
    """An installed package"""

    def __init__(self, package_path: Path):
        """Create a new Package from path.

        Args:
            package_path: Path to installed package directory.

        """
        if type(package_path) == str:
            # Convert strings to pathlib.Path objects
            package_path = Path(package_path)
        self.package_path = package_path
        metadata_path = package_path / "metadata.json"
        if not metadata_path.exists():
            raise FileNotFoundError(
                "Error opening package at " + str(metadata_path) + " no metadata.json"
            )
        with open(metadata_path) as metadata_file:
            metadata = json.load(metadata_file)
            self.load_metadata_from_json(metadata)

    def update(self):
        """Update the package if a newer version is available."""
        for available_package in get_available_packages():
            if (
                available_package.from_code == self.from_code
                and available_package.to_code == self.to_code
            ):
                if available_package.package_version > self.package_version:
                    new_package_path = available_package.download()
                    uninstall(self)
                    install_from_path(new_package_path)

    def get_readme(self) -> str | None:
        """Returns the text of the README.md in this package.

        Returns:
            The text of the package README.md, None
                if README.md can't be read

        """
        readme_path = self.package_path / "README.md"
        if not readme_path.exists():
            return None
        with open(readme_path, "r") as readme_file:
            return readme_file.read()

    def get_description(self):
        return self.get_readme()


def install_from_path(path: Path):
    """Install a package file (zip archive ending in .argosmodel).

    Args:
        path: The path to the .argosmodel file to install.

    """
    with package_lock:
        if not zipfile.is_zipfile(path):
            raise Exception("Not a valid Argos Model (must be a zip archive)")
        with zipfile.ZipFile(path, "r") as zipf:
            zipf.extractall(path=settings.package_data_dir)


class AvailablePackage(IPackage):
    """A package available for download and installation"""

    def __init__(self, metadata):
        """Creates a new AvailablePackage from a metadata object"""
        self.load_metadata_from_json(metadata)

    def download(self) -> Path:
        """Downloads the AvailablePackage and returns its path"""
        filename = argospm_package_name(self) + ".argosmodel"

        # Install sbd package if needed
        if self.type == "translate" and not settings.stanza_available:
            if (
                len(list(filter(lambda x: x.type == "sbd", get_installed_packages())))
                == 0
            ):
                # No sbd packages are installed, download all available
                sbd_packages = filter(
                    lambda x: x.type == "sbd", get_available_packages()
                )
                for sbd_package in sbd_packages:
                    download_path = sbd_package.download()
                    install_from_path(download_path)

        filepath = settings.downloads_dir / filename
        if not filepath.exists():
            data = networking.get_from(self.links)
            if data is None:
                raise Exception(f"Download failed for {str(self)}")
            with open(filepath, "wb") as f:
                f.write(data)
        return filepath

    def install(self):
        download_path = self.download()
        install_from_path(download_path)
        download_path.unlink()

    def get_description(self):
        return "{} → {}".format(self.from_name, self.to_name)


def uninstall(pkg: Package):
    """Uninstalls a package.

    Args:
        pkg: The package to uninstall

    """
    with package_lock:
        shutil.rmtree(pkg.package_path)


def get_installed_packages(path: Path = None) -> list[Package]:
    """Return a list of installed Packages

    Looks for packages in <home>/.argos-translate/local/share/packages by
    default. Will also look in the directory specified
    in the ARGOS_TRANSLATE_PACKAGE_DIR environment variable
    if it is set.

    Args:
        path: Path to look for installed package directories in.
            Defaults to the path in settings module.

    """
    with package_lock:
        to_return = []
        packages_path = settings.package_dirs if path is None else path
        for directory in packages_path:
            for path in directory.iterdir():
                if path.is_dir():
                    to_return.append(Package(path))
        return to_return


def update_package_index():
    """Downloads remote package index"""
    with package_lock:
        try:
            response = urllib.request.urlopen(settings.remote_package_index)
        except Exception as err:
            error(err)
            return
        data = response.read()
        with open(settings.local_package_index, "wb") as f:
            f.write(data)


def get_available_packages() -> list[Package]:
    """Returns a list of AvailablePackages from the package index."""

    try:
        with open(settings.local_package_index) as index_file:
            index = json.load(index_file)
            packages = []
            for metadata in index:
                package = AvailablePackage(metadata)
                packages.append(package)

            # If stanza not available filter for sbd available
            if not settings.stanza_available:
                installed_and_available_packages = packages + get_installed_packages()
                sbd_packages = list(
                    filter(lambda x: x.type == "sbd", installed_and_available_packages)
                )
                sbd_available_codes = set()
                for sbd_package in sbd_packages:
                    sbd_available_codes = sbd_available_codes.union(
                        sbd_package.from_codes
                    )
                packages = list(
                    filter(lambda x: x.from_code in sbd_available_codes, packages)
                )
                return packages + sbd_packages

            return packages
    except FileNotFoundError:
        raise Exception(
            "Local package index not found, use package.update_package_index() to load it"
        )


def argospm_package_name(pkg: IPackage) -> str:
    """Gets argospm name of an IPackage.

    Args:
        The package to get the name of.

    Returns:
        Package name for argospm
    """
    to_return = pkg.type
    if pkg.from_code and pkg.to_code:
        to_return += "-" + pkg.from_code + "_" + pkg.to_code
    return to_return


def load_available_packages() -> list[Package]:
    """Deprecated 1.2, use get_available_packages"""
    info(
        "Using deprecated function load_available_packages, use get_available_packages instead"
    )
    return get_available_packages()
