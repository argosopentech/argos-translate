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
    

def main():
    commands = ['update', 'install', 'list', 'remove']

    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('command', help=', '.join(commands))
    parser.add_argument('argument', nargs='?', help='Argument for command')
    args = parser.parse_args()

    # Parse command
    command = args.command
    if command not in commands:
        print(f'Unrecognized command {args.command}')
        print(f'Valid commands {commands}')
        exit(1)

    if command == 'update':
        package.update_package_index()

    elif command == 'install':
        available_packages = package.get_available_packages()
        package_name = args.argument
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

    elif command == 'list':
        installed_packages = package.get_installed_packages()
        for installed_package in installed_packages:
            print(name_of_package(installed_package))

    elif command == 'remove':
        installed_packages = package.get_installed_packages()
        package_name = args.argument
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
