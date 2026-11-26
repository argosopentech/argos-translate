Graphical User Interface
==========================

The GUI is maintained in a `separate repository
<https://github.com/argosopentech/argos-translate-gui>`_. Install and launch it:

.. code-block:: sh

   python -m pip install argostranslategui
   argos-translate-gui


Installing a language
-----------------------

For platform-specific installation instructions, see the GUI repository.

Languages are chosen as drop down choices. More language pairs can be installed.

The left text box translates into the right box.

Example workflow translating from Vietnamese into English:

* Set the left drop down to `Vietnamese` and the right drop down to `English`.
* Replace the default text `Text to translate from` in the left text box with some text in Vietnamese. A quick way to do this is to click in the left text box and press the keyboard shortcut `CTRL+a` to select all and then `CTRL+v` to paste.
* Wait for the model to load and the translation to finish.
* When text appears in the right text box, read the translation!

If the output looks similar to the input, try changing the origin language as some languages appear similar if you are unfamiliar with them.

Adding language pair models from the graphical interface
----------------------------------------------------------

Model sizes vary. Downloads require internet access; see :doc:`troubleshooting`
for preparing sentence-splitting resources before offline use.

Installing new pairs through the GUI
--------------------------------------

* Open Argos Translate: `argos-translate-gui`
* Click on the `Manage Packages` menu item.
* Click on the `Download packages` button.
* Click on the down arrow beside a language pair that you want to add.
* Wait for the hourglass icon to change into a check mark icon.
* Repeat the last two steps until you have all of the language pairs that you want.
* Click on the `X` in the top right to close the `Download packages` window.
* Click on the `X` in the top right to close the `Manage Packages` window.

Menu details can vary by GUI release. You can also import a downloaded package
file using the instructions below.

Importing new pairs through the GUI
-------------------------------------

* Download or make new pairs.  Model links can be downloaded from https://www.argosopentech.com/argospm/index/ or https://raw.githubusercontent.com/argosopentech/argospm-index/main/index.json
* Open Argos Translate: `argos-translate-gui`
* Click on the `Manage Packages` menu item.
* Click on the `Install package file` button.
* Navigate to where you downloaded the new language pairs, click on the `.argosmodel` file, and click on the `Open` button.
* Repeat the last two steps until you have all of the language pairs that you want.
* Click on the `X` in the top right to close the `Manage Packages` window.

Removing a pair through the GUI
---------------------------------

* Open Argos Translate: `argos-translate-gui`
* Click on the `Manage Packages` menu item.
* Click on the trash can icon besides the pair you want to remove.
* Click on the `X` in the top right to close the `Manage Packages` window.
