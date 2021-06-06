from argostranslate import package
import pytest


class TestIPackage:
    def setup_method(self):
        self.ipackage = package.IPackage()
        self.test_metadata = {
            "package_version": 0.1,
            "argos_version": 0.2,
            "from_code": "en",
            "from_name": "English",
            "to_code": "es",
            "to_name": "Spanish",
            "links": ["https://example.com/en_es.argosmodel"],
        }

    def test_load_metadata_from_json(self):
        self.ipackage.load_metadata_from_json(self.test_metadata)

        for key, value in self.test_metadata.items():
            assert hasattr(self.ipackage, key)
            assert getattr(self.ipackage, key) == value

    def test_get_readme(self):
        with pytest.raises(NotImplementedError):
            self.ipackage.get_readme()

    def test_get_description(self):
        with pytest.raises(NotImplementedError):
            self.ipackage.get_description()

    def test_equal(self):

        package_one = package.IPackage()
        package_two = package.IPackage()

        package_one.load_metadata_from_json(self.test_metadata)
        package_two.load_metadata_from_json(self.test_metadata)

        # They both have the same metadata right now
        assert package_one == package_two

        # Change package version, now they are not the same
        package_one.package_version += 1
        assert package_one != package_two

    def test_string(self):
        test_package = package.IPackage()
        test_package.load_metadata_from_json(self.test_metadata)

        expected = f"{test_package.from_name} -> {test_package.to_name}"
        assert repr(test_package) == expected


class TestPackage:
    def setup_method(self):
        with pytest.raises(FileNotFoundError):
            self.package = package.Package("example/")

        self.package = package.Package("tests/data/package/")
        self.readme = "# This is the test package readme\n"

    def test_get_readme(self):
        with pytest.raises(FileNotFoundError):
            package_one = package.Package("example/")
            assert package_one.get_readme() == None

        with pytest.raises(FileNotFoundError):
            package_one = package.Package("path/to/nowhere")
            assert package_one.get_readme() == None

        assert self.package.get_readme() == self.readme

    def test_get_description(self):
        self.package.get_description() == self.readme
