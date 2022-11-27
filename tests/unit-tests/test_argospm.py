import unittest.mock

import argostranslate.argospm

import mock_argostranslate_package 

@unittest.mock.patch("argostranslate.package.get_installed_packages", mock_argostranslate_package.get_installed_packages)
def test_argospm_list():
    argostranslate.argospm.list_packages(None)