exit 1
# This isn't meant to be run for now
# It just documents the upload process

# Make sure to update the version number in setup.py

cd ..
rm -rf build dist
python setup.py sdist bdist_wheel
twine check dist/*
twine upload dist/*

