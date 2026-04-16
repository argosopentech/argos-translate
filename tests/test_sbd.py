"""Tests for sbd module spacy import resilience (Python 3.14 compatibility)."""
import sys
import types
import builtins


def _make_stub(name):
    mod = types.ModuleType(name)
    sys.modules[name] = mod
    return mod


def test_spacy_broad_exception_guard(monkeypatch):
    """sbd.spacy must be None when spacy raises a non-ImportError on import.

    On Python 3.14, spacy raises SystemError due to Pydantic V1 incompatibility.
    The try/except in sbd.py must catch Exception (not just ImportError).
    """
    # Stub out heavy dependencies so sbd.py can be imported in this environment.
    stanza_stub = _make_stub("stanza")
    stanza_stub.Pipeline = object

    minisbd_stub = _make_stub("minisbd")
    minisbd_models_stub = _make_stub("minisbd.models")
    minisbd_models_stub.cache_dir = ""
    minisbd_models_stub.list_models = lambda: []
    minisbd_stub.SBDetect = object
    minisbd_stub.models = minisbd_models_stub

    pkg_stub = _make_stub("argostranslate.package")
    pkg_stub.get_installed_packages = lambda: []
    pkg_stub.Package = object

    settings_stub = _make_stub("argostranslate.settings")

    class ChunkType:
        SPACY = "spacy"

    settings_stub.ChunkType = ChunkType
    settings_stub.chunk_type = "stanza"
    settings_stub.data_dir = __import__("pathlib").Path("/tmp")
    settings_stub.device = "cpu"

    networking_stub = _make_stub("argostranslate.networking")
    networking_stub.cache_spacy = lambda: None

    utils_stub = _make_stub("argostranslate.utils")
    utils_stub.info = lambda *a, **kw: None
    utils_stub.warning = lambda *a, **kw: None

    apis_stub = _make_stub("argostranslate.apis")
    fewshot_stub = _make_stub("argostranslate.fewshot")

    # Simulate spacy failing with SystemError (as happens with Pydantic V1 + Python 3.14)
    original_import = builtins.__import__

    def patched_import(name, *args, **kwargs):
        if name == "spacy":
            raise SystemError("Pydantic V1 not compatible with Python 3.14+")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", patched_import)

    # Remove any cached sbd module
    for key in list(sys.modules.keys()):
        if "sbd" in key and "argostranslate" in key:
            del sys.modules[key]
    sys.modules.pop("spacy", None)

    import importlib
    sbd_mod = importlib.import_module("argostranslate.sbd")
    assert sbd_mod.spacy is None, (
        "sbd.spacy should be None when spacy raises SystemError on import"
    )
