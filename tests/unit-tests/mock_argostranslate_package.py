import pathlib


class Package:
    pass


mock_packages = [Package() for i in range(3)]


def get_installed_packages(packages_dir: pathlib.Path | None = None) -> list[Package]:
    return mock_packages
