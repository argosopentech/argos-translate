Argos Translate Documentation
===========================================


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Open-source offline translation library written in Python

Argos Translate uses CTranslate2 for translation. Sentence splitting is configurable; see :doc:`source/settings`. The GUI is maintained in a separate repository. Argos Translate can be used as either a Python library, command-line, or GUI application. LibreTranslate is an API and web-app built on top of Argos Translate.

Argos Translate supports installing language model packages which are zip archives with a ".argosmodel" extension with the data needed for translation.

Argos Translate also manages automatically pivoting through intermediate languages to translate between languages that don't have a direct translation between them installed. For example, if you have a es ➔ en and en ➔ fr translation installed you are able to translate from es ➔ fr as if you had that translation installed. This allows for translating between a wide variety of languages at the cost of some loss of translation quality.

Getting started
-----------------

Install the library with ``python -m pip install argostranslate``. The repository's
unit-test workflow uses Python 3.11 on Ubuntu; other platforms depend on available
native dependency wheels. See the
`CTranslate2 installation requirements <https://opennmt.net/CTranslate2/installation.html>`_.

.. include:: source/examples.rst
   :start-after: .. quickstart-start
   :end-before: .. quickstart-end

Command Line Interface Example
--------------------------------

.. code-block:: sh

   argospm update
   argospm install translate-en_es
   argos-translate --from-lang en --to-lang es "Hello World"

Install a model for each direction you need. English-to-Spanish does not install
Spanish-to-English. Downloads and initial sentence-splitter setup require network
access; see :doc:`source/troubleshooting` before running offline.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   source/settings
   source/cli
   source/gui
   source/examples
   source/troubleshooting
   source/modules

