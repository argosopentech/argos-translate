import logging
import copy
import zipfile
import json
import shutil
import urllib.request
from pathlib import Path
from threading import Lock
import uuid

from argostranslate import settings
from argostranslate import utils
from argostranslate import networking
from argostranslate.utils import info

# TODO: Handle dependencies
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
        package_path (Path): The path to the installed package. None if not installed.

        package_version (str): The version of the package.

        argos_version (str): The version of Argos Translate the package is intended for.

        from_code (str): The code of the language the package translates from.

        from_name (str): Human readable name of the language the package translates from.

        to_code (str): The code of the language the package translates to.

        to_name (str): Human readable name of the language the package translates to.

        links [list(str)]: A list of links to download the package


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

    def load_metadata_from_json(self, metadata):
        """Loads package metadata from a JSON object.

        Args:
            metadata: A json object from json.load

        """
        info("Load metadata from package json", metadata)

        self.code = metadata.get("code")
        self.name = metadata.get("name")
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

        # Filter out languages that don't have a code
        self.source_languages = list(
            filter(lambda lang: lang.get("code") is not None, self.source_languages)
        )
        self.target_languages = list(
            filter(lambda lang: lang.get("code") is not None, self.target_languages)
        )

    def get_readme(self):
        """Returns the text of the README.md in this package.

        Returns:
            (str): The text of the package README.md, None
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


class Package(IPackage):
    """An installed package"""

    def __init__(self, package_path):
        """Create a new Package from path.

        Args:
            package_path (pathlib.Path): Path to installed package directory.

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

    def get_readme(self):
        """Returns the text of the README.md in this package.

        Returns:
            (str): The text of the package README.md, None
                if README.md can't be read

        """
        readme_path = self.package_path / "README.md"
        if not readme_path.exists():
            return None
        with open(readme_path, "r") as readme_file:
            return readme_file.read()

    def get_description(self):
        return self.get_readme()


def install_from_path(path):
    """Install a package file (zip archive ending in .argosmodel).

    Args:
        path (pathlib): The path to the .argosmodel file to install.

    """
    with package_lock:
        if not zipfile.is_zipfile(path):
            raise Exception("Not a valid Argos Model (must be a zip archive)")
        with zipfile.ZipFile(path, "r") as zip:
            zip.extractall(path=settings.package_data_dir)
            info("Installed package from path", path)


class AvailablePackage(IPackage):
    """A package available for download and installation"""

    def __init__(self, metadata):
        """Creates a new AvailablePackage from a metadata object"""
        self.load_metadata_from_json(metadata)

    def download(self):
        """Downloads the AvailablePackage and returns its path"""

        package_slug = self.code if self.code is not None else uuid.uuid4()
        filename = package_slug + ".argosmodel"

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

    def get_description(self):
        return self.name


def uninstall(pkg):
    """Uninstalls a package.

    Args:
        pkg (Package): The package to uninstall

    """
    with package_lock:
        info("Uninstalled package", pkg)
        shutil.rmtree(pkg.package_path)


def get_installed_packages(path=None):
    """Return a list of installed Packages

    Looks for packages in <home>/.argos-translate/local/share/packages by
    default. Will also look in the directory specified
    in the ARGOS_TRANSLATE_PACKAGE_DIR environment variable
    if it is set.

    Args:
        path (pathlib.Path): Path to look for installed package directories in.
            Defaults to the path in settings module.

    """
    with package_lock:
        installed_packages = []
        packages_path = settings.package_dirs if path is None else path
        for directory in packages_path:
            for path in directory.iterdir():
                if path.is_dir():
                    installed_packages.append(Package(path))
        info("get_installed_packages", installed_packages)
        return installed_packages


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


def get_available_packages():
    """Returns a list of AvailablePackages from the package index."""

    try:
        with open(settings.local_package_index) as index_file:
            index = json.load(index_file)
            available_packages = list()
            for metadata in index:
                package = AvailablePackage(metadata)
                available_packages.append(package)

            info("get_available_packages", available_packages)
            return available_packages
    except FileNotFoundError:
        update_package_index()
        return get_available_packages()
