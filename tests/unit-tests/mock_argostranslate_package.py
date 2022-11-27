import pathlib


class Package:
    def __str__(self) -> str:
        return "Mock Package"

    def __repr__(self) -> str:
        return "MockPackage"


mock_packages = [Package() for i in range(3)]


def get_installed_packages(packages_dir: pathlib.Path | None = None) -> list[Package]:
    return mock_packages
