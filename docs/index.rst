Argos Translate Documentation
===========================================
Open-source offline translation library written in Python

Argos Translate uses OpenNMT for translations, SentencePiece for tokenization, Stanza for sentence boundary detection, and PyQt for GUI. Argos Translate can be used as either a Python library, command-line, or GUI application. LibreTranslate is an API and web-app built on top of Argos Translate.

Argos Translate supports installing language model packages which are zip archives with a ".argosmodel" extension with the data needed for translation.

Argos Translate also manages automatically pivoting through intermediate languages to translate between languages that don't have a direct translation between them installed. For example, if you have a es ➔ en and en ➔ fr translation installed you are able to translate from es ➔ fr as if you had that translation installed. This allows for translating between a wide variety of languages at the cost of some loss of translation quality.

Python Example
--------------
.. code-block:: python
        import argostranslate.package, argostranslate.translate

        # Download and install .argosmodel package
        available_packages = argostranslate.package.get_available_packages()
        available_package_en_es = list(filter(
                lambda x: x.from_code == "en" and x.to_code == "es",
                available_packages))[0]
        download_path = available_package_en_es.download()
        argostranslate.package.install_from_path(download_path)

        # Translate English to Spanish with Argos Translate
        installed_languages = argostranslate.translate.get_installed_languages()
        language_en = list(filter(
                lambda x: x.code == "en",
                installed_languages))[0]
        language_es = list(filter(
                lambda x: x.code == "es",
                installed_languages))[0]
        translation_en_es = language_en.get_translation(language_es)
        translatedText = translation_en_es.translate("Hello World!")
        print(translatedText)
        # '¡Hola Mundo!'


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   source/cli
   source/gui



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
