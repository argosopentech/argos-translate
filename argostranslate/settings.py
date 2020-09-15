from pathlib import Path
import os

data_dir = Path.home() / '.argos-translate'
package_data_dir = data_dir / 'packages'

# Will search all of these directories for packages
package_dirs = [package_data_dir]
if 'SNAP' in os.environ:
    package_dirs.append(
            Path(os.environ['SNAP']) / 'packages')
if 'ARGOS_TRANSLATE_PACKAGE_DIR' in os.environ:
    package_dirs.append(Path(os.environ[
            'ARGOS_TRANSLATE_PACKAGE_DIR']))
