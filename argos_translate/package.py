import zipfile
import os
import json

from argos_translate import settings

class Package:
    """A package is a an installable model.

    Packages are a zip archive of a directory with metadata.json
    in its root the .argosmodel file extension. By default a 
    OpenNMT CTranslate directory named model/ created using 
    ct2-opennmt-tf-converter is expected in the root directory
    along with a sentencepiece model named sentencepiece.model
    for tokenizing and NLTK punkt pickle named punkt.pickle.
    Packages may also optionally have a README.md in the root.

    from_code and to_code should be ISO 639-1 codes if applicable.

    Example metadata.json
    {
        "package_version": "1.0",
        "argos_version": "1.0",
        "from_code": "en",
        "from_name": "English",
        "to_code": "es",
        "to_name": "Spanish"
    }
    """

    def __init__(self, package_path):
        self.package_path = package_path
        metadata_path = package_path / 'metadata.json'
        if not metadata_path.exists():
            raise Exception('Error opening package at ' +
                    str(metadata_path) + ' no metadata.json')
        with open(metadata_path) as metadata_file:
            metadata = json.load(metadata_file)
            self.package_version = metadata.get('package_version')
            self.argos_version = metadata.get('argos_version')
            self.from_code = metadata.get('from_code')
            self.from_name = metadata.get('from_name')
            self.to_code = metadata.get('to_code')
            self.to_name = metadata.get('to_name')

def check_data_dir():
    """Checks that data dir is setup correctly.

    Checks that the data directory in settings.py exist
    and creates it if it doesn't"""

    if not os.path.exists(settings.data_dir):
        os.makedirs(settings.data_dir)

def install_from_path(path):
    """Install a package (zip archive ending in .argosmodel)."""

    if not zipfile.is_zipfile(path):
        raise Error('Not a valid Argos Model (must be a zip archive)')
    check_data_dir()
    with zipfile.ZipFile(path, 'r') as zip:
        zip.extractall(path=settings.data_dir)

def get_installed_packages():
    """Return a list of installed packages"""
    check_data_dir()
    to_return = []
    for directory in settings.package_dirs:
        for path in directory.iterdir():
            if path.is_dir():
                to_return.append(Package(path))
    return to_return

