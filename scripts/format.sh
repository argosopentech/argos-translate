#!/bin/bash

# Format with black
black argostranslate
black setup.py

# Sort imports with isort
isort argostranslate
isort setup.py

