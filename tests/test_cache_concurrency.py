"""Model-free regression tests for cache publication and lazy initialization."""

from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Barrier, Event
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from argostranslate import apply_bpe, package, sbd, settings, tokenizer, translate


class ObservedLock:
    """Let tests wait for lock attempts without relying on sleeps."""

    def __init__(self, lock):
        self.lock = lock
        self.attempts = Queue()

    def __enter__(self):
        self.attempts.put(True)
        return self.lock.__enter__()

    def __exit__(self, *args):
        return self.lock.__exit__(*args)


@pytest.mark.parametrize(
    "kind", ["translator", "sentencepiece", "minisbd", "stanza", "bpe"]
)
def test_concurrent_first_use_loads_once(kind, tmp_path, monkeypatch):
    started, release = Event(), Event()
    model = object()

    def construct(*args, **kwargs):
        started.set()
        assert release.wait(5)
        return model

    constructor = Mock(side_effect=construct)
    pkg = SimpleNamespace(package_path=tmp_path, from_code="en")
    if kind == "translator":
        monkeypatch.setattr(settings, "chunk_type", settings.ChunkType.NONE)
        obj = translate.PackageTranslation(None, None, pkg)
        monkeypatch.setattr(translate.ctranslate2, "Translator", constructor)
        monkeypatch.setattr(
            translate,
            "apply_packaged_translation",
            lambda *args: [translate.Hypothesis("ok", 0)],
        )
        invoke = lambda: obj.hypotheses("text", 1)
        loaded = lambda: obj.translator
    elif kind == "sentencepiece":
        obj = tokenizer.SentencePieceTokenizer(tmp_path / "model")
        monkeypatch.setattr(tokenizer.spm, "SentencePieceProcessor", constructor)
        invoke, loaded = obj.lazy_processor, lambda: obj.processor
    elif kind == "minisbd":
        monkeypatch.setattr(sbd.minisbd_models, "list_models", lambda: ["en"])
        obj = sbd.MiniSBDSentencizer(pkg)
        monkeypatch.setattr(sbd, "SBDetect", constructor)
        invoke, loaded = obj.lazy_detector, lambda: obj.detector
    elif kind == "stanza":
        obj = sbd.StanzaSentencizer(pkg)
        monkeypatch.setattr(sbd, "stanza", SimpleNamespace(Pipeline=constructor))
        invoke, loaded = obj.lazy_pipeline, lambda: obj.stanza_pipeline
    else:
        model_path = tmp_path / "bpe.model"
        model_path.write_text("#version: 0.2\na b\n")
        obj = tokenizer.BPETokenizer(model_path, "en", "es")
        monkeypatch.setattr(apply_bpe, "BPE", constructor)
        invoke, loaded = obj.lazy_load, lambda: obj.bpe_source

    lock = ObservedLock(obj._init_lock)
    obj._init_lock = lock
    with ThreadPoolExecutor(2) as pool:
        first = pool.submit(invoke)
        try:
            assert started.wait(5)
            lock.attempts.get(timeout=5)
            second = pool.submit(invoke)
            lock.attempts.get(timeout=5)
            assert not second.done()
            if kind == "bpe":
                assert obj.tokenizer is None
                assert obj.normalizer is None
        finally:
            release.set()
        first.result(timeout=5)
        second.result(timeout=5)
    assert constructor.call_count == 1
    assert loaded() is model
    invoke()
    assert constructor.call_count == 1
    assert lock.attempts.empty(), "Warm use should not acquire the initialization lock"


def test_bpe_failed_initialization_can_retry(tmp_path, monkeypatch):
    path = tmp_path / "bpe.model"
    path.write_text("#version: 0.2\na b\n")
    obj = tokenizer.BPETokenizer(path, "en", "es")
    real_bpe = apply_bpe.BPE
    with path.open() as model_file:
        model = real_bpe(model_file)
    constructor = Mock(side_effect=[RuntimeError("load failed"), model])
    monkeypatch.setattr(apply_bpe, "BPE", constructor)
    with pytest.raises(RuntimeError, match="load failed"):
        obj.encode("hello")
    assert obj.tokenizer is None
    assert obj.detokenizer is None
    assert obj.normalizer is None
    assert obj.bpe_source is None
    assert obj.decode(obj.encode("hello")) == "hello"
    assert constructor.call_count == 2


def test_translation_inference_remains_concurrent(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "chunk_type", settings.ChunkType.NONE)
    obj = translate.PackageTranslation(
        None, None, SimpleNamespace(package_path=tmp_path)
    )
    monkeypatch.setattr(
        translate.ctranslate2, "Translator", Mock(return_value=object())
    )
    barrier = Barrier(2)

    def infer(*args):
        barrier.wait(timeout=5)
        return [translate.Hypothesis("ok", 0)]

    monkeypatch.setattr(translate, "apply_packaged_translation", infer)
    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(lambda _: obj.translate("text"), range(2)))
    assert results == ["ok", "ok"]
    assert translate.ctranslate2.Translator.call_count == 1


@pytest.mark.parametrize("change", ["uninstall", "clear"])
def test_graph_publication_cannot_race_invalidation(change, tmp_path, monkeypatch):
    started, release = Event(), Event()
    pkg = SimpleNamespace(
        from_code="en",
        to_code="es",
        from_name="English",
        to_name="Spanish",
        type="translate",
        package_path=tmp_path / "model",
    )
    pkg.package_path.mkdir()
    monkeypatch.setattr(settings, "model_provider", settings.ModelProvider.OPENNMT)
    monkeypatch.setattr(
        package,
        "get_installed_packages",
        lambda: [pkg] if pkg.package_path.exists() else [],
    )

    def construct(source, target, pkg):
        started.set()
        assert release.wait(5)
        return SimpleNamespace(from_lang=source, to_lang=target)

    monkeypatch.setattr(translate, "PackageTranslation", construct)
    translate.get_installed_languages.cache_clear()
    lock = ObservedLock(package.package_lock)
    monkeypatch.setattr(package, "package_lock", lock)
    try:
        with ThreadPoolExecutor(2) as pool:
            building = pool.submit(translate.get_installed_languages)
            try:
                assert started.wait(5)
                lock.attempts.get(timeout=5)
                action = (
                    (lambda: package.uninstall(pkg))
                    if change == "uninstall"
                    else translate.get_installed_languages.cache_clear
                )
                changing = pool.submit(action)
                lock.attempts.get(timeout=5)
                assert not changing.done()
            finally:
                release.set()
            assert len(building.result(timeout=5)) == 2
            changing.result(timeout=5)
        assert translate.get_installed_languages.cache_info().currsize == 0
        if change == "uninstall":
            assert translate.get_installed_languages() == []
    finally:
        translate.get_installed_languages.cache_clear()


def test_concurrent_graph_lookups_share_one_build(monkeypatch):
    started, release = Event(), Event()

    def read_packages():
        started.set()
        assert release.wait(5)
        return []

    reader = Mock(side_effect=read_packages)
    monkeypatch.setattr(package, "get_installed_packages", reader)
    monkeypatch.setattr(settings, "model_provider", settings.ModelProvider.OPENNMT)
    translate.get_installed_languages.cache_clear()
    lock = ObservedLock(package.package_lock)
    monkeypatch.setattr(package, "package_lock", lock)
    try:
        with ThreadPoolExecutor(2) as pool:
            first = pool.submit(translate.get_installed_languages)
            try:
                assert started.wait(5)
                lock.attempts.get(timeout=5)
                second = pool.submit(translate.get_installed_languages)
                lock.attempts.get(timeout=5)
                assert not second.done()
            finally:
                release.set()
            assert first.result(timeout=5) is second.result(timeout=5)
        assert reader.call_count == 1
    finally:
        translate.get_installed_languages.cache_clear()
