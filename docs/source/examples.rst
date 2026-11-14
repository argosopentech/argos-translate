Examples
===========================================

.. quickstart-start

Basic Python example
----------------------

The download and installation steps require internet access. First translation
may also download sentence-splitting resources; subsequent translations use local
models. Exact output varies by model version.

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
    translated_text = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translated_text)
    # '¡Hola Mundo!'

.. quickstart-end

After setup, omit the package download steps and call ``translate.translate``
directly. The example assumes the requested package exists; if ``next`` raises
``StopIteration``, run ``argospm update`` and ``argospm search`` to inspect available
language directions.

Install package from file path
--------------------------------
.. code-block:: python

        import pathlib

        import argostranslate.package

        package_path = pathlib.Path("translate-en_it.argosmodel")

        argostranslate.package.install_from_path(package_path)

Check an installed translation direction
------------------------------------------

.. code-block:: python

    from argostranslate import translate

    source = translate.get_language_from_code("en")
    target = translate.get_language_from_code("es")
    route = source.get_translation(target) if source and target else None
    if route is None:
        raise RuntimeError("Install an English-to-Spanish translation first")
    print(route.translate("Hello World"))

A route may pivot through an intermediate language. Use the codes in installed
package metadata; some variants use codes such as ``pb`` or ``zt``.
