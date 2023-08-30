Examples
===========================================

Install package from file path
--------------
.. code-block:: python

        import pathlib
        
        import argostranslate.package
        
        package_path = pathlib.Path("/root/translate-en_it-2_0.argosmodel")
         
        argostranslate.package.install_from_path(package_path)
