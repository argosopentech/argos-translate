from __future__ import annotations

import argparse

from argostranslate import package, settings
from argostranslate.package import AvailablePackage

"""
Example usage:
argospm update
argospm install translate-en_es
argospm list
argospm remove translate-en_es
"""


def update_index(args):
    """Update the package index."""
    package.update_package_index()


def get_available_packages() -> list[AvailablePackage]:
    """Get available packages and update packages list if it is not done

    Returns:
        The list of available packages
    """
    try:
        available_packages = package.get_available_packages()
    except:
        update_index()
        available_packages = package.get_available_packages()

    return available_packages


def install_package_print_path(available_package: AvailablePackage):
    download_path = available_package.download()
    print(f"Downloaded package {download_path}")
    package.install_from_path(download_path)
    print(f"Installed package to {settings.package_data_dir}")


def install_all_packages():
    """Install all packages available to Argos Translate."""
    available_packages = get_available_packages()
    for available_package in available_packages:
        available_package.install()


def install_package(args):
    """Install package."""

    available_packages = get_available_packages()
    package_name = args.name

    if package_name == "translate":
        install_all_packages()
    else:
        for available_package in available_packages:
            name = package.argospm_package_name(available_package)
            if name == package_name:
                available_package.install()
                break
        else:
            print("Package not found")
            exit(1)


def search_packages(args):
    """Display packages from remote index."""

    available_packages = get_available_packages()
    for pkg in available_packages:
        if args.from_lang and args.from_lang != pkg.from_code:
            continue
        if args.to_lang and args.to_lang != pkg.to_code:
            continue
        print(
            f"{package.argospm_package_name(pkg)}: "
            + f"{pkg.from_code} -> {pkg.to_code}"
        )


def list_packages(args):
    """List packages."""
    installed_packages = package.get_installed_packages()
    for installed_package in installed_packages:
        print(package.argospm_package_name(installed_package))


def remove_package(args):
    """Remove installed package."""
    installed_packages = package.get_installed_packages()
    package_name = args.name
    for installed_package in installed_packages:
        name = package.argospm_package_name(installed_package)
        if name == package_name:
            package.uninstall(installed_package)
            print(f"Removed package {name}")
            break
    else:
        print("Package not found")
        exit(1)


def main():
    """Run argospm command line program"""
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(help="Available commands.")

    update_parser = subparser.add_parser(
        "update", help="Downloads remote package index."
    )
    update_parser.set_defaults(callback=update_index)

    search_parser = subparser.add_parser(
        "search", help="Search package from remote index."
    )
    search_parser.add_argument(
        "--from-lang",
        "-f",
        help="The code for the language to translate from (ISO 639-1)",
    )
    search_parser.add_argument(
        "--to-lang", "-t", help="The code for the language to translate to (ISO 639-1)"
    )
    search_parser.set_defaults(callback=search_packages)

    install_parser = subparser.add_parser("install", help="Install package.")
    install_parser.add_argument(
        "name", help='Package name, use "translate" to install all packages'
    )
    install_parser.set_defaults(callback=install_package)

    list_parser = subparser.add_parser("list", help="List installed packages.")
    list_parser.set_defaults(callback=list_packages)

    remove_parser = subparser.add_parser("remove", help="Remove installed package.")
    remove_parser.set_defaults(callback=remove_package)
    remove_parser.add_argument("name", help="Package name")

    args = parser.parse_args()
    args.callback(args)
