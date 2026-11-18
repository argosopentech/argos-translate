from types import SimpleNamespace

from argostranslate import sbd


def test_stanza_pipeline_uses_offline_mode(monkeypatch, tmp_path):
    pipeline_args = {}

    class OfflineStanza:
        @staticmethod
        def Pipeline(**kwargs):
            pipeline_args.update(kwargs)
            return lambda text: SimpleNamespace(
                sentences=[SimpleNamespace(text=text)]
            )

    monkeypatch.setattr(sbd, "stanza", OfflineStanza)
    package = SimpleNamespace(from_code="bn", package_path=tmp_path)

    sentencizer = sbd.StanzaSentencizer(package)
    assert sentencizer.split_sentences("offline text") == ["offline text"]
    assert pipeline_args["download_method"] is None
