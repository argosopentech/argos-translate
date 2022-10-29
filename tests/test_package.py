import argostranslate
import pytest


def test_IPackage_load_metadata_from_json():
    metadata = {
        "code": "test",
        "name": "Test Package",
        "package_version": "2.0",
        "argos_version": "2.0",
        "links": ["https://example.com/argospm/translate-en_es-2_0.argosmodel"],
        "type": "translate",
        "languages": [
            {"code": "en", "name": "English"},
            {"code": "es", "name": "Spanish"},
            {"code": "fr", "name": "French"},
        ],
        "dependencies": ["test_dependency"],
    }
    package = argostranslate.package.IPackage()
    package.load_metadata_from_json(metadata)
    assert package.code == "test"
    assert package.name == "Test Package"
    assert package.package_version == "2.0"
    assert package.argos_version == "2.0"
    assert package.links == [
        "https://example.com/argospm/translate-en_es-2_0.argosmodel"
    ]
    assert package.type == "translate"
    assert package.languages == [
        {"code": "en", "name": "English"},
        {"code": "es", "name": "Spanish"},
        {"code": "fr", "name": "French"},
    ]
    assert package.dependencies == ["test_dependency"]
    assert package.source_languages == [
        {"code": "en", "name": "English"},
        {"code": "es", "name": "Spanish"},
        {"code": "fr", "name": "French"},
    ]
    assert package.target_languages == [
        {"code": "en", "name": "English"},
        {"code": "es", "name": "Spanish"},
        {"code": "fr", "name": "French"},
    ]
