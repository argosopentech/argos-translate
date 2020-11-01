exit 1
# This script isn't currently runnable it just documents the process
# Remember to update version number

cd ..
snapcraft clean && SNAPCRAFT_BUILD_ENVIRONMENT_MEMORY=4G snapcraft

# Install and test snap

snapcraft login
snapcraft upload --release=stable mysnap_latest_amd64.snap

