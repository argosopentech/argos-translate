exit 1
# This isn't meant to be run for now
# It just documents the upload process

# Make sure to update the version number in setup.py

# Git tag version number
# git tag -a v1.0.0

# Run from root of project
rm -rf build dist
python setup.py sdist bdist_wheel
twine check dist/*
twine upload dist/*

