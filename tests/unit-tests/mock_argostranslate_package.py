import pathlib


class IPackage:
    def __str__(self) -> str:
        return "Mock Package"

    def __repr__(self) -> str:
        return "MockPackage"

    code: str = "mockpackage"


class AvailablePackage(IPackage):
    pass


class Package(IPackage):
    pass


mock_available_packages = [AvailablePackage()] * 3


def get_available_packages() -> list[AvailablePackage]:
    return mock_available_packages


mock_installed_packages = [Package() for i in range(3)]


def get_installed_packages(packages_dir: pathlib.Path | None = None) -> list[IPackage]:
    return mock_installed_packages
