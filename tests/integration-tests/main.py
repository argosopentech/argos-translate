#!/bin/env python3

import argostranslate.package

available_packages = argostranslate.package.get_available_packages()
assert len(available_packages) > 0

print("Completed Argos Translate regression test")
