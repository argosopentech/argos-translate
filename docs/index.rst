Argos Translate Documentation
===========================================


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Open-source offline translation library written in Python

Argos Translate uses OpenNMT for translations, SentencePiece for tokenization, Stanza for sentence boundary detection, and PyQt for GUI. Argos Translate can be used as either a Python library, command-line, or GUI application. LibreTranslate is an API and web-app built on top of Argos Translate.

Argos Translate supports installing language model packages which are zip archives with a ".argosmodel" extension with the data needed for translation.

Argos Translate also manages automatically pivoting through intermediate languages to translate between languages that don't have a direct translation between them installed. For example, if you have a es ➔ en and en ➔ fr translation installed you are able to translate from es ➔ fr as if you had that translation installed. This allows for translating between a wide variety of languages at the cost of some loss of translation quality.

Python Example
--------------
.. code-block:: python

        import argostranslate.package
        import argostranslate.translate

        from_code = "en"
        to_code = "es"

        # Download and install Argos Translate package
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        available_package = list(
            filter(
                lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
            )
        )[0]
        download_path = available_package.download()
        argostranslate.package.install_from_path(download_path)

        # Translate
        installed_languages = argostranslate.translate.get_installed_languages()
        from_lang = list(filter(
                lambda x: x.code == from_code,
                installed_languages))[0]
        to_lang = list(filter(
                lambda x: x.code == to_code,
                installed_languages))[0]
        translation = from_lang.get_translation(to_lang)
        translatedText = translation.translate("Hello World!")
        print(translatedText)
        # '¡Hola Mundo!'

Command Line Interface Example
--------------
.. code-block:: bash
        argospm update
        argospm install translate-en_de
        argos-translate --from en --to de "Hello World!"
        # Hallo Welt!



.. toctree::
   :maxdepth: 2
   :caption: Contents:

   :ref:`genindex`
   source/settings
   source/cli
   source/gui

