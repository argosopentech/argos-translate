"""Exercise the documented quickstart without downloading translation models."""
from pathlib import Path
import re
import textwrap
from types import SimpleNamespace
from unittest.mock import Mock

from argostranslate import package, translate

ROOT = Path(__file__).resolve().parents[1]


def test_readme_and_sphinx_quickstart(monkeypatch, capsys):
    readme = (ROOT / "README.md").read_text()
    example = re.search(r"```python\n(.*?)```", readme, re.S).group(1)
    guide = (ROOT / "docs/source/examples.rst").read_text()
    rst_example = guide.split(".. code-block:: python\n\n", 1)[1].split(
        "\n.. quickstart-end", 1
    )[0]
    assert example.strip() == textwrap.dedent(rst_example).strip()

    update = Mock()
    download = Mock(return_value=Path("example.argosmodel"))
    install = Mock()
    translated = Mock(return_value="¡Hola Mundo!")
    monkeypatch.setattr(package, "update_package_index", update)
    monkeypatch.setattr(package, "get_available_packages", lambda: [
        SimpleNamespace(from_code="de", to_code="en"),
        SimpleNamespace(from_code="en", to_code="es", download=download),
    ])
    monkeypatch.setattr(package, "install_from_path", install)
    monkeypatch.setattr(translate, "translate", translated)
    exec(compile(example, "README.md", "exec"), {})
    update.assert_called_once_with()
    download.assert_called_once_with()
    install.assert_called_once_with(Path("example.argosmodel"))
    translated.assert_called_once_with("Hello World", "en", "es")
    assert capsys.readouterr().out == "¡Hola Mundo!\n"
