from __future__ import annotations

import argparse

from argostranslate import package
from argostranslate import settings
from argostranslate.package import AvailablePackage

"""
Example usage:
argospm install translate
argospm list
argospm remove translate
argospm search m2m
"""


def update_index(args):
    """Update the package index."""
    package.update_package_index()


def install_package(args):
    """Install package."""
    available_packages = package.get_available_packages()
    package_to_install = next(
        (
            available_package
            for available_package in available_packages
            if available_package.code == args.code
        ),
        None,
    )
    if package_to_install:
        package_to_install.install()
        print(str(package_to_install))
    else:
        print("Package not found")
        exit(1)


def search_packages(args):
    """Display packages from remote index."""
    available_packages = package.get_available_packages()
    query = args.query
    query = query.strip()
    results = filter(
        lambda available_package: (
            available_package.code is not None
            and available_package.code.casefold() == query.casefold()
        )
        or (
            available_package.name is not None
            and query.casefold() in available_package.name.casefold()
        ),
        available_packages,
    )
    for result in results:
        print(f"{repr(result)} - {str(result)}")


def list_packages(args):
    """List installed packages."""
    installed_packages = package.get_installed_packages()
    for installed_package in installed_packages:
        print(f"{repr(installed_package)} : {str(installed_package)}")


def remove_package(args):
    """Remove installed package."""
    installed_packages = package.get_installed_packages()
    package_to_remove = next(
        (
            installed_package
            for installed_package in installed_packages
            if installed_package.code == args.code
        ),
        None,
    )
    if package_to_remove:
        package.uninstall(package_to_remove)
    else:
        print("Package not found")
        exit(1)


def main():
    """Run argospm command line program"""
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(help="Available commands.")

    update_parser = subparser.add_parser("update", help="Update package index")
    update_parser.set_defaults(callback=update_index)

    search_parser = subparser.add_parser(
        "search", help="Search for packages in package index"
    )
    search_parser.add_argument("query", help="Search query")
    search_parser.set_defaults(callback=search_packages)

    install_parser = subparser.add_parser("install", help="Install package")
    install_parser.add_argument(
        "code",
        help='Package code, use "translate" to install default translation packages',
    )
    install_parser.set_defaults(callback=install_package)

    list_parser = subparser.add_parser("list", help="List installed packages")
    list_parser.set_defaults(callback=list_packages)

    remove_parser = subparser.add_parser("remove", help="Remove installed package")
    remove_parser.set_defaults(callback=remove_package)
    remove_parser.add_argument("code", help="Package code")

    args = parser.parse_args()
    args.callback(args)
