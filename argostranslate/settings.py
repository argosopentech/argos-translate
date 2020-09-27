from pathlib import Path
import os

data_dir = Path.home() / '.argos-translate'
if 'SNAP' in os.environ:
    data_dir = Path(os.environ['SNAP_USER_DATA']) / '.argos-translate'
package_data_dir = data_dir / 'packages'

# Will search all of these directories for packages
package_dirs = [package_data_dir]
if 'SNAP' in os.environ:
    package_dirs.append(
            Path(os.environ['SNAP']) / 'packages')
if 'ARGOS_TRANSLATE_PACKAGE_DIR' in os.environ:
    package_dirs.append(Path(os.environ[
            'ARGOS_TRANSLATE_PACKAGE_DIR']))
about_text = """
Argos Translate is an open source neural machine
translation application created by Argos Open
Technologies, LLC (www.argosopentech.com). 
"""
