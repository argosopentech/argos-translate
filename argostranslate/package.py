import zipfile
import os
import json
import shutil

import requests

from argostranslate import settings

"""
## `package` module example usage
```
from argostranslate import package

# Update package definitions from remote
package.update_package_index()

# Load available packages from local package index
available_packages = package.load_available_packages()

# Download and install all available packages
for available_package in available_packages:
    download_path = available_package.download()
    package.install_from_path(download_path)
```
"""

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
    OpenNMT CTranslate directory named model/ created using 
    ct2-opennmt-tf-converter is expected in the root directory
    along with a sentencepiece model named sentencepiece.model
    for tokenizing and Stanza for sentence boundary detection. 
    Packages may also optionally have a README.md in the root.

    from_code and to_code should be ISO 639-1 codes if applicable.

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
        self.package_version = metadata.get('package_version')
        self.argos_version = metadata.get('argos_version')
        self.from_code = metadata.get('from_code')
        self.from_name = metadata.get('from_name')
        self.to_code = metadata.get('to_code')
        self.to_name = metadata.get('to_name')
        self.links = metadata.get('links')

    def get_readme(self):
        """Returns the text of the README.md in this package.

        Returns:
            (str): The text of the package README.md, None
                if README.md can't be read

        """
        readme_path = self.package_path / 'README.md'
        if not readme_path.is_file():
            return None
        with open(readme_path, 'r') as readme_file:
            return readme_file.read()
        return None

    def __str__(self):
        return "{} -> {}".format(self.from_name, self.to_name)

class Package(IPackage):
    """An installed package"""
    def __init__(self, package_path):
        """Create a new Package from path.

        Args:
            package_path (str): Path to installed package directory.

        """
        self.package_path = package_path
        metadata_path = package_path / 'metadata.json'
        if not metadata_path.exists():
            raise Exception('Error opening package at ' +
                    str(metadata_path) + ' no metadata.json')
        with open(metadata_path) as metadata_file:
            metadata = json.load(metadata_file)
            self.load_metadata_from_json(metadata)

class AvailablePackage(IPackage):
    """A package available for download"""
    def __init__(self, metadata):
        """Creates a new AvailablePackage from a metadata object"""
        self.load_metadata_from_json(metadata)

    def download(self):
        """Downloads the AvailablePackage and returns its path"""
        url = self.links[0]
        filename = self.from_code + '_' + self.to_code + '.argosmodel'
        filepath = settings.downloads_dir / filename
        r = requests.get(url, allow_redirects=True)
        open(filepath, 'wb').write(r.content)
        return filepath


def install_from_path(path):
    """Install a package (zip archive ending in .argosmodel).

    Args:
        path (str): The path to the .argosmodel file to install.

    """
    if not zipfile.is_zipfile(path):
        raise Error('Not a valid Argos Model (must be a zip archive)')
    with zipfile.ZipFile(path, 'r') as zip:
        zip.extractall(path=settings.package_data_dir)

def uninstall(pkg):
    """Uninstalls a package.

    Args:
        pkg (Package): The package to uninstall

    """
    shutil.rmtree(pkg.package_path)

def get_installed_packages(path=None):
    """Return a list of installed Packages

    Looks for packages in <home>/.argos-translate/packages by
    default. Will also look in the directory specified
    in the ARGOS_TRANSLATE_PACKAGE_DIR environment variable
    if it is set.

    Args:
        path (str): Path to look for installed package directories in.
            Defaults to the path in settings module.

    """
    to_return = []
    packages_path = settings.package_dirs if path == None else path
    for directory in packages_path:
        for path in directory.iterdir():
            if path.is_dir():
                to_return.append(Package(path))
    return to_return

def update_package_index():
    """Downloads remote package index"""
    r = requests.get(settings.remote_package_index, allow_redirects=True)
    open(settings.local_package_index, 'wb').write(r.content)

def load_available_packages():
    """Returns a list of AvailablePackages from the package index."""
    try:
        with open(settings.local_package_index) as index_file:
            index = json.load(index_file)
            to_return = []
            for metadata in index:
                package = AvailablePackage(metadata)
                to_return.append(package)
            return to_return
    except FileNotFoundError:
        raise Exception('Local package index not found,' +
                ' use package.update_package_index() to load it')

