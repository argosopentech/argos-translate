Argos Translate Documentation
===========================================
Open-source offline translation library written in Python

Argos Translate uses OpenNMT for translations, SentencePiece for tokenization, Stanza for sentence boundary detection, and PyQt for GUI. Argos Translate can be used as either a Python library, command-line, or GUI application. LibreTranslate is an API and web-app built on top of Argos Translate.

Argos Translate supports installing language model packages which are zip archives with a ".argosmodel" extension with the data needed for translation.

Argos Translate also manages automatically pivoting through intermediate languages to translate between languages that don't have a direct translation between them installed. For example, if you have a es ➔ en and en ➔ fr translation installed you are able to translate from es ➔ fr as if you had that translation installed. This allows for translating between a wide variety of languages at the cost of some loss of translation quality.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   source/cli	     



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
