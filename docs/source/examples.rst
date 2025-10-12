Examples
===========================================

Basic Python example
--------------
.. code-block:: python

        import argostranslate.package
        import argostranslate.translate

        from_code = "en"
        to_code = "es"

        # Download and install Argos Translate package
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        package_to_install = next(
        filter(
                lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
        )
        )
        argostranslate.package.install_from_path(package_to_install.download())

        # Translate
        translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
        print(translatedText)
        # '¡Hola Mundo!'


Install package from file path
--------------
.. code-block:: python

        import pathlib
        
        import argostranslate.package
        
        package_path = pathlib.Path("/root/translate-en_it-2_0.argosmodel")
         
        argostranslate.package.install_from_path(package_path)
