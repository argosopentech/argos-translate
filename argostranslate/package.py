import zipfile
import os
import json
import shutil

from argostranslate import settings

class Package:
    """An installed package.

    Attributes:
        package_path (Path): The path to the installed package.
        package_version (str): The version of the package.
        argos_version (str): The version of Argos Translate the package is intended for.
        from_code (str): The code of the language the package translates from.
        from_name (str): Human readable name of the language the package translates from.
        to_code (str): The code of the language the package translates to.
        to_name (str): Human readable name of the language the package translates to.

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
        "to_name": "Spanish"
    }

    """

    def __init__(self, package_path):
        """Create a new Package.

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
            self.package_version = metadata.get('package_version')
            self.argos_version = metadata.get('argos_version')
            self.from_code = metadata.get('from_code')
            self.from_name = metadata.get('from_name')
            self.to_code = metadata.get('to_code')
            self.to_name = metadata.get('to_name')

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


def check_data_dirs():
    """Checks that data and package dir is set up correctly.

    Checks that the data directory in settings.py exist
    and creates it if it doesn't.
    
    """
    if not os.path.exists(settings.data_dir):
        os.makedirs(settings.data_dir)
    if not os.path.exists(settings.package_data_dir):
        os.makedirs(settings.package_data_dir)

def install_from_path(path):
    """Install a package (zip archive ending in .argosmodel).

    Args:
        path (str): The path to the .argosmodel file to install.

    """
    if not zipfile.is_zipfile(path):
        raise Error('Not a valid Argos Model (must be a zip archive)')
    check_data_dirs()
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
    check_data_dirs()
    to_return = []
    packages_path = settings.package_dirs if path == None else path
    for directory in packages_path:
        for path in directory.iterdir():
            if path.is_dir():
                to_return.append(Package(path))
    return to_return

