import argostranslate.package


def test_IPackage_load_metadata_from_json():
    metadata = {
        "code": "test",
        "type": "translate",
        "name": "Test Package",
        "package_version": "2.0",
        "argos_version": "2.0",
        "links": ["https://example.com/argospm/translate-2_0.argosmodel"],
        "dependencies": ["test_dependency"],
        "languages": [
            {"code": "en", "name": "English"},
            {"code": "es", "name": "Spanish"},
            {"code": "fr", "name": "French"},
        ],
    }
    package = argostranslate.package.IPackage()
    package.load_metadata_from_json(metadata)
    assert package.code == "test"
    assert package.type == "translate"
    assert package.name == "Test Package"
    assert package.package_version == "2.0"
    assert package.argos_version == "2.0"
    assert package.links == ["https://example.com/argospm/translate-2_0.argosmodel"]
    assert package.dependencies == ["test_dependency"]
    assert package.languages == [
        {"code": "en", "name": "English"},
        {"code": "es", "name": "Spanish"},
        {"code": "fr", "name": "French"},
    ]
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
