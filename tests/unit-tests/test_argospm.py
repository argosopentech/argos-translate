import unittest.mock
from io import StringIO

import argostranslate.argospm

import mock_argostranslate_package


@unittest.mock.patch(
    "argostranslate.package.get_installed_packages",
    mock_argostranslate_package.get_installed_packages,
)
def test_argospm_list():
    with unittest.mock.patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        argostranslate.argospm.list_packages(None)
        expected_stdout = "MockPackage : Mock Package\n" * 3
        assert mock_stdout.getvalue() == expected_stdout

@unittest.mock.patch(
    "argostranslate.package.get_available_packages",
    mock_argostranslate_package.get_available_packages,
)
def test_argospm_search_packages():
    with unittest.mock.patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        class Args:
            query: str = "mockpackage"
        argostranslate.argospm.search_packages(Args())
        expected_stdout = "MockPackage - Mock Package\n" * 3
        assert mock_stdout.getvalue() == expected_stdout

