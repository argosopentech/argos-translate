from pathlib import Path
import os

data_dir = Path.home() / '.argos-translate'

# Will search all of these directories for packages
package_dirs = [data_dir]
if 'SNAP' in os.environ:
    package_dirs.append(
            Path(os.environ['SNAP']) / 'packages')
