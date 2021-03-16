from pathlib import Path
import os
import sys
import shutil
import platform

debug = False
if 'DEBUG' in os.environ:
    debug = os.environ['DEBUG'] in ['1', 'TRUE', 'True', 'true']

home_dir = Path.home()
if 'SNAP' in os.environ:
    home_dir = Path(os.environ['SNAP_USER_DATA'])

data_dir = Path(os.getenv('XDG_DATA_HOME',
        default=home_dir / '.local' / 'share')) / 'argos-translate'
os.makedirs(data_dir, exist_ok=True)

package_data_dir = Path(os.getenv('ARGOS_TRANSLATE_PACKAGES_DIR',
        default=data_dir / 'packages'))
os.makedirs(package_data_dir, exist_ok=True)

cache_dir = Path(os.getenv('XDG_CACHE_HOME',
        default=home_dir / '.local' / 'cache')) / 'argos-translate'
os.makedirs(cache_dir, exist_ok=True)

remote_repo = os.getenv('ARGOS_REMOTE_REPO',
        default='https://raw.githubusercontent.com/argosopentech/argospm-index/main')
remote_package_index = remote_repo + '/index.json'

downloads_dir = cache_dir / 'downloads'
os.makedirs(downloads_dir, exist_ok=True)

# Legacy support to upgrade from argostranslate<1.1.0
legacy_package_data_dirs = [Path.home() / '.argos-translate' / 'packages']
if 'SNAP' in os.environ:
    legacy_package_data_dirs.append(
            Path(os.environ['SNAP_USER_DATA']) / '.argos-translate')
for legacy_package_data_dir in legacy_package_data_dirs: 
    if legacy_package_data_dir.is_dir():
        print('Moving Argos Translate data dir from {} to {}'.format(
            legacy_package_data_dir, package_data_dir))
        # dirs_exist_ok not available <= 3.8
        if sys.version_info[0] >= 3 and sys.version_info[1] >= 8:
            shutil.copytree(legacy_package_data_dir, package_data_dir, dirs_exist_ok=True)
        else:
            shutil.copytree(legacy_package_data_dir, package_data_dir)
        shutil.rmtree(legacy_package_data_dir)

# Will search all of these directories for packages
package_dirs = [package_data_dir]
if 'SNAP' in os.environ:
    # Packages bundled with snap
    snap_package_dir = Path(os.environ['SNAP']) / 'snap_custom' / 'packages'
    if os.path.isdir(snap_package_dir):
        package_dirs.append(snap_package_dir)

    # Packages loaded from a content snap
    content_snap_packages = Path(os.environ['SNAP']) / 'snap_custom' / 'content_snap_packages'
    if os.path.isdir(content_snap_packages):
        for package_dir in content_snap_packages.iterdir():
            if package_dir.is_dir():
                package_dirs.append(package_dir)

if 'ARGOS_TRANSLATE_PACKAGE_DIR' in os.environ:
    package_dirs.append(Path(os.environ[
            'ARGOS_TRANSLATE_PACKAGE_DIR']))

local_package_index = cache_dir / 'index.json'

about_text = """
Argos Translate is an open source neural machine
translation application created by Argos Open
Technologies, LLC (www.argosopentech.com). 
"""

# Fix Intel bug
# https://github.com/argosopentech/argos-translate/issues/40
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

