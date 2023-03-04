#!/bin/bash

# Format with black
black argostranslate tests setup.py

# Sort imports with isort
isort argostranslate tests setup.py

