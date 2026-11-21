import argostranslate
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
        assert self.package.get_description() == self.readme


def test_missing_index_download_failure_has_bounded_retries(tmp_path, monkeypatch):
    from urllib.error import URLError
    from unittest.mock import Mock
    from argostranslate import argospm, settings

    monkeypatch.setattr(settings, "local_package_index", tmp_path / "index.json")
    download = Mock(side_effect=URLError("offline"))
    monkeypatch.setattr(package.urllib.request, "urlopen", download)
    with pytest.raises(URLError, match="offline"):
        argospm.get_available_packages()
    assert download.call_count == 4


@pytest.mark.parametrize("failures", [1, 3])
def test_missing_index_download_recovers_after_retries(tmp_path, monkeypatch, failures):
    from io import BytesIO
    from urllib.error import URLError
    from unittest.mock import Mock
    from argostranslate import settings

    monkeypatch.setattr(settings, "local_package_index", tmp_path / "index.json")
    response = BytesIO(b'[{"from_code": "en", "to_code": "es"}]')
    download = Mock(side_effect=[URLError("offline")] * failures + [response])
    monkeypatch.setattr(package.urllib.request, "urlopen", download)
    assert package.get_available_packages()[0].to_code == "es"
    assert download.call_count == failures + 1
    assert response.closed


def test_index_response_read_failure_is_retried(tmp_path, monkeypatch):
    from http.client import IncompleteRead
    from io import BytesIO
    from unittest.mock import MagicMock, Mock
    from argostranslate import settings

    index_path = tmp_path / "index.json"
    monkeypatch.setattr(settings, "local_package_index", index_path)
    failed_response = MagicMock()
    failed_response.__enter__.return_value = failed_response
    failed_response.read.side_effect = IncompleteRead(b"partial")
    download = Mock(side_effect=[failed_response, BytesIO(b"[]")])
    monkeypatch.setattr(package.urllib.request, "urlopen", download)
    package.update_package_index()
    assert index_path.read_bytes() == b"[]"
    assert download.call_count == 2
    failed_response.__exit__.assert_called_once()


def test_missing_index_is_downloaded_once(tmp_path, monkeypatch):
    from io import BytesIO
    from unittest.mock import Mock
    from argostranslate import settings

    monkeypatch.setattr(settings, "local_package_index", tmp_path / "index.json")
    download = Mock(return_value=BytesIO(b'[{"from_code": "en", "to_code": "es"}]'))
    monkeypatch.setattr(package.urllib.request, "urlopen", download)
    assert package.get_available_packages()[0].to_code == "es"
    assert package.get_available_packages()[0].from_code == "en"
    assert download.call_count == 1


def test_missing_index_after_update_does_not_recurse(tmp_path, monkeypatch):
    from unittest.mock import Mock
    from argostranslate import settings

    monkeypatch.setattr(settings, "local_package_index", tmp_path / "index.json")
    update = Mock()
    monkeypatch.setattr(package, "update_package_index", update)
    with pytest.raises(FileNotFoundError):
        package.get_available_packages()
    assert update.call_count == 1


@pytest.mark.parametrize("as_string", [False, True])
def test_get_installed_packages_explicit_directory(as_string, monkeypatch):
    from pathlib import Path
    from argostranslate import settings

    monkeypatch.setattr(settings, "package_dirs", [])
    directory = Path("tests/data")
    packages = package.get_installed_packages(str(directory) if as_string else directory)
    assert len(packages) == 1
    assert packages[0].package_path == directory / "package"


def test_get_installed_packages_uses_configured_directories(tmp_path, monkeypatch):
    from pathlib import Path
    from argostranslate import settings

    monkeypatch.setattr(settings, "package_dirs", [tmp_path, Path("tests/data")])
    assert len(package.get_installed_packages()) == 1
    assert package.get_installed_packages(tmp_path) == []


def test_metadata_keeps_source_and_target_languages_separate():
    pkg = package.IPackage()
    pkg.load_metadata_from_json({
        "from_code": "en", "from_name": "English",
        "to_code": "es", "to_name": "Spanish",
    })
    assert pkg.source_languages == [{"code": "en", "name": "English"}]
    assert pkg.target_languages == [{"code": "es", "name": "Spanish"}]


def test_metadata_language_lists_are_not_mutated_or_duplicated():
    import copy

    metadata = {
        "from_code": "en", "from_name": "English",
        "to_code": "es", "to_name": "Spanish",
        "source_languages": [{"code": "de"}],
        "target_languages": [{"code": "fr"}],
        "languages": [{"code": "it"}],
    }
    original = copy.deepcopy(metadata)
    pkg = package.IPackage()
    for _ in range(2):
        pkg.load_metadata_from_json(metadata)
        assert pkg.source_languages == [
            {"code": "de"}, {"code": "en", "name": "English"}, {"code": "it"},
        ]
        assert pkg.target_languages == [
            {"code": "fr"}, {"code": "es", "name": "Spanish"}, {"code": "it"},
        ]
        assert metadata == original


def test_metadata_without_pair_does_not_add_empty_languages():
    pkg = package.IPackage()
    pkg.load_metadata_from_json({"languages": [{"code": "en"}]})
    assert pkg.source_languages == [{"code": "en"}]
    assert pkg.target_languages == [{"code": "en"}]


@pytest.mark.parametrize("suffix", ["", "/", "///"])
def test_package_index_base_url_accepts_optional_trailing_slash(tmp_path, monkeypatch, suffix):
    import runpy
    from argostranslate import settings

    for directory in ("DATA", "CONFIG", "CACHE"):
        monkeypatch.setenv(f"XDG_{directory}_HOME", str(tmp_path / directory))
    monkeypatch.setenv("ARGOS_PACKAGE_INDEX", "https://example.com/models" + suffix)
    loaded = runpy.run_path(settings.__file__)
    assert loaded["remote_package_index"] == "https://example.com/models/index.json"
