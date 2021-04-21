from argostranslate import package

import argparse

"""
Example usage:
argospm update
argospm install translate-en_es
argospm list
argospm remove translate-en_es
"""

def name_of_package(pkg):
    """The package name of IPackage

        Args:
            (package.IPackage) Package to get name of.
    """
    return 'translate-' + pkg.from_code + '_' + pkg.to_code


def update_index(args):
    """Update the package index."""
    package.update_package_index()


def install_package(args):
    """Install package."""
    available_packages = package.get_available_packages()
    package_name = args.name
    package_found = False
    for available_package in available_packages:
        name = name_of_package(available_package)
        if name == package_name:
            download_path = available_package.download()
            package.install_from_path(download_path)
            print(f'Installed package to path {download_path}')
            package_found = True
            break
    if not package_found:
        print('Package not found')


def list_packages(args):
    """List packages."""
    installed_packages = package.get_installed_packages()
    for installed_package in installed_packages:
        print(name_of_package(installed_package))


def remove_package(args):
    """Remove installed package."""
    installed_packages = package.get_installed_packages()
    package_name = args.name
    package_found = False
    for installed_package in installed_packages:
        name = name_of_package(installed_package)
        if name == package_name:
            installed_package.remove()
            print(f'Removed package {name}')
            package_found = True
            break
    if not package_found:
        print('Package not found')


def main():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(help='Available commands.')

    update_parser = subparser.add_parser(
        'update', help='Downloads remote package index.')
    update_parser.set_defaults(callback=update_index)

    install_parser = subparser.add_parser(
        'install', help='Install package.')
    install_parser.add_argument('name', help='Package name')
    install_parser.set_defaults(callback=install_package)

    list_parser = subparser.add_parser(
        'list', help='List installed packages.')
    list_parser.set_defaults(callback=list_packages)

    remove_parser = subparser.add_parser(
        'remove', help='Remove installed package.')
    remove_parser.set_defaults(callback=remove_package)
    remove_parser.add_argument('name', help='Package name')

    args = parser.parse_args()
    args.callback(args)
