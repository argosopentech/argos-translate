import builtins
import json
import os
import stat
import tempfile
from io import BytesIO
from pathlib import Path
from unittest.mock import Mock
from urllib.error import URLError

import pytest

from argostranslate import package, settings


@pytest.fixture
def local_index(tmp_path, monkeypatch):
    path = tmp_path / "index.json"
    path.write_bytes(b'[{"from_code":"en","to_code":"es"}]')
    monkeypatch.setattr(settings, "local_package_index", path)
    return path


def mock_download(monkeypatch, data):
    response = BytesIO(data)
    download = Mock(return_value=response)
    monkeypatch.setattr(package.urllib.request, "urlopen", download)
    return download, response


@pytest.mark.parametrize(
    "data",
    [
        b"<html>Bad gateway</html>",
        b"{}",
        b"null",
        b"[1]",
        b'[{"from_code":"en"},null]',
        b"\xff",
    ],
)
def test_invalid_download_preserves_readable_index(local_index, monkeypatch, data):
    previous = local_index.read_bytes()
    download, response = mock_download(monkeypatch, data)

    with pytest.raises(ValueError):
        package.update_package_index()

    assert local_index.read_bytes() == previous
    assert package.get_available_packages()[0].to_code == "es"
    assert set(local_index.parent.iterdir()) == {local_index}
    assert download.call_count == 1
    assert response.closed


def test_invalid_first_download_does_not_leave_an_index(local_index, monkeypatch):
    local_index.unlink()
    download, response = mock_download(monkeypatch, b"not JSON")

    with pytest.raises(ValueError):
        package.get_available_packages()

    assert not local_index.exists()
    assert not list(local_index.parent.iterdir())
    assert download.call_count == 1
    assert response.closed


@pytest.mark.parametrize("existing", [False, True])
@pytest.mark.parametrize(
    "metadata",
    [
        [],
        [
            {
                "from_code": "en",
                "to_code": "ja",
                "to_name": "日本語",
                "future_metadata": {"label": "café", "values": [1, None, True]},
            }
        ],
    ],
)
def test_successful_update_reloads_and_keeps_extensions(
    local_index, monkeypatch, existing, metadata
):
    if not existing:
        local_index.unlink()
    data = json.dumps(metadata, ensure_ascii=False, indent=2).encode("utf-8")
    download, response = mock_download(monkeypatch, data)

    package.update_package_index()

    assert local_index.read_bytes() == data
    assert json.loads(local_index.read_bytes()) == metadata
    available = package.get_available_packages()
    assert [pkg.to_name for pkg in available] == [pkg["to_name"] for pkg in metadata]
    assert set(local_index.parent.iterdir()) == {local_index}
    assert download.call_count == 1
    assert response.closed


@pytest.mark.parametrize("existing", [False, True])
def test_unicode_index_is_read_as_utf8(local_index, monkeypatch, existing):
    data = '[{"from_code":"en","to_code":"ja","to_name":"日本語"}]'.encode("utf-8")
    if existing:
        local_index.write_bytes(data)
    else:
        local_index.unlink()
    download, _ = mock_download(monkeypatch, data)

    def ascii_default_open(file, mode="r", *args, **kwargs):
        if "b" not in mode:
            kwargs.setdefault("encoding", "ascii")
        return builtins.open(file, mode, *args, **kwargs)

    monkeypatch.setattr(package, "open", ascii_default_open, raising=False)

    assert package.get_available_packages()[0].to_name == "日本語"
    assert download.call_count == (0 if existing else 1)


@pytest.mark.parametrize("failure", ["write", "close"])
def test_io_failure_keeps_previous_index_and_removes_temporary_file(
    local_index, monkeypatch, failure
):
    previous = local_index.read_bytes()
    data = b'[{"from_code":"en","to_code":"fr"}]'
    download, _ = mock_download(monkeypatch, data)
    real_temporary_file = tempfile.NamedTemporaryFile

    class FailingWriter:
        def __init__(self, wrapped):
            self.wrapped = wrapped
            self.name = wrapped.name

        def __enter__(self):
            return self

        def write(self, contents):
            if failure == "write":
                self.wrapped.write(contents[:4])
                self.wrapped.flush()
                raise OSError("injected disk write failure")
            return self.wrapped.write(contents)

        def __exit__(self, exc_type, exc, traceback):
            self.wrapped.__exit__(exc_type, exc, traceback)
            if failure == "close" and exc_type is None:
                raise OSError("injected close failure")

    def failing_open(file, mode="r", *args, **kwargs):
        opened = builtins.open(file, mode, *args, **kwargs)
        return FailingWriter(opened) if "w" in mode else opened

    def failing_temporary_file(*args, **kwargs):
        return FailingWriter(real_temporary_file(*args, **kwargs))

    monkeypatch.setattr(package, "open", failing_open, raising=False)
    monkeypatch.setattr(tempfile, "NamedTemporaryFile", failing_temporary_file)

    with pytest.raises(OSError, match=f"injected.*{failure} failure"):
        package.update_package_index()

    assert local_index.read_bytes() == previous
    assert package.get_available_packages()[0].to_code == "es"
    assert set(local_index.parent.iterdir()) == {local_index}
    assert download.call_count == 1


def test_replace_failure_keeps_previous_index_and_cleans_up(local_index, monkeypatch):
    previous = local_index.read_bytes()
    data = b'[{"from_code":"en","to_code":"fr"}]'
    download, _ = mock_download(monkeypatch, data)

    def fail_replace(source, target):
        assert Path(target) == local_index
        assert source.parent == local_index.parent
        assert source.read_bytes() == data
        assert local_index.read_bytes() == previous
        raise PermissionError("index replacement denied")

    monkeypatch.setattr(Path, "replace", fail_replace)

    with pytest.raises(PermissionError, match="replacement denied"):
        package.update_package_index()

    assert local_index.read_bytes() == previous
    assert set(local_index.parent.iterdir()) == {local_index}
    assert download.call_count == 1


def test_publish_uses_a_closed_complete_file_in_the_same_directory(
    local_index, monkeypatch
):
    previous = local_index.read_bytes()
    data = b'[{"from_code":"en","to_code":"fr"}]'
    mock_download(monkeypatch, data)
    real_temporary_file = tempfile.NamedTemporaryFile
    real_replace = Path.replace
    temporary_files = []
    replacements = []

    def track_temporary_file(*args, **kwargs):
        created = real_temporary_file(*args, **kwargs)
        temporary_files.append(created)
        return created

    def inspect_replace(source, target):
        assert Path(target) == local_index
        assert source.parent == local_index.parent
        assert len(temporary_files) == 1
        assert temporary_files[0].closed
        assert source.read_bytes() == data
        assert local_index.read_bytes() == previous
        assert package.get_available_packages()[0].to_code == "es"
        replacements.append(source)
        return real_replace(source, target)

    monkeypatch.setattr(tempfile, "NamedTemporaryFile", track_temporary_file)
    monkeypatch.setattr(Path, "replace", inspect_replace)

    package.update_package_index()

    assert len(replacements) == 1
    assert package.get_available_packages()[0].to_code == "fr"
    assert set(local_index.parent.iterdir()) == {local_index}


@pytest.mark.skipif(os.name != "posix", reason="POSIX permission bits")
def test_update_preserves_existing_posix_permissions(local_index, monkeypatch):
    local_index.chmod(0o640)
    mock_download(monkeypatch, b"[]")

    package.update_package_index()

    assert stat.S_IMODE(local_index.stat().st_mode) == 0o640


def test_download_failure_keeps_old_index_and_bounded_retries(local_index, monkeypatch):
    previous = local_index.read_bytes()
    download = Mock(side_effect=URLError("offline"))
    monkeypatch.setattr(package.urllib.request, "urlopen", download)

    with pytest.raises(URLError, match="offline"):
        package.update_package_index()

    assert local_index.read_bytes() == previous
    assert download.call_count == 4
    assert set(local_index.parent.iterdir()) == {local_index}
