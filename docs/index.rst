.. Argos Translate documentation master file, created by
   sphinx-quickstart on Sat Sep 12 21:47:20 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Argos Translate Documentation
===========================================
Open-source offline translation library written in Python. Uses OpenNMT for translations, SentencePiece for tokenization, Stanza for sentence boundary detection, and PyQt for GUI. Designed to be used as either a Python library, command-line, or GUI application. LibreTranslate is an API and web-app built on top of Argos Translate.

Argos Translate supports installing model files which are a zip archive with an ".argosmodel" extension that contains an OpenNMT CTranslate2 model, a SentencePiece tokenization model, a Stanza tokenizer model for sentence boundary detection, and metadata about the model.

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
