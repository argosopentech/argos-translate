import argostranslate.package


def test_IPackage_load_metadata():
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
    package.load_metadata(metadata)
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


def test_IPackage_load_metadata_v1():
    metadata = {
        "package_version": "1.0",
        "argos_version": "1.0",
        "from_code": "ar",
        "from_name": "Arabic",
        "to_code": "en",
        "to_name": "English",
        "links": [
            "https://argosopentech.nyc3.digitaloceanspaces.com/argospm/translate-ar_en-1_0.argosmodel",
            "https://cdn.argosopentech.io/translate-ar_en-1_0.argosmodel",
            "https://cdn2.argosopentech.io/translate-ar_en-1_0.argosmodel",
            "ipfs://QmV5bmf8iqKpoGoyuTzEppaSWdceuW6zgiePaUr5ThPCpW",
        ],
    }
    package = argostranslate.package.IPackage()
    package.load_metadata(metadata)
    assert package.package_version == "1.0"
    assert package.argos_version == "1.0"
    assert package.from_code == "ar"
    assert package.from_name == "Arabic"
    assert package.to_code == "en"
    assert package.to_name == "English"
    assert package.links == [
        "https://argosopentech.nyc3.digitaloceanspaces.com/argospm/translate-ar_en-1_0.argosmodel",
        "https://cdn.argosopentech.io/translate-ar_en-1_0.argosmodel",
        "https://cdn2.argosopentech.io/translate-ar_en-1_0.argosmodel",
        "ipfs://QmV5bmf8iqKpoGoyuTzEppaSWdceuW6zgiePaUr5ThPCpW",
    ]
