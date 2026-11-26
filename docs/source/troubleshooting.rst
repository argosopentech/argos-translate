Offline use and troubleshooting
=================================

Offline translation
---------------------

Argos Translate runs translation locally with its default ``OPENNMT`` provider.
However, installing a translation package does not always install all sentence
boundary detection (SBD) resources. First use may download them. Optional remote
API providers are not offline translation.

For a predictable offline setup, select ``MINISBD`` explicitly, install the
required packages, and translate representative text while connected:

.. code-block:: sh

   export ARGOS_CHUNK_TYPE=MINISBD
   argospm update
   argospm install translate-en_es
   argos-translate --from-lang en --to-lang es "Hello world. This is an offline test."

Repeat for every direction you need, including routes through intermediate
languages. Then disconnect networking and repeat the translations in a **new
process**, using the same user account, settings, package versions, and data
paths. Offline runtime code should call translation only, not repeat index updates
or package downloads from the setup example.

* **MiniSBD:** uses a packaged ``minisbd/*.onnx`` model when present. Otherwise,
  first translation downloads the selected source-language model into
  ``minisbd/`` under the Argos data directory (normally
  ``~/.local/share/argos-translate/minisbd``). Existing files are reused without a
  download. Some language codes map to a related language or fall back to English.
* **SpaCy:** selecting ``SPACY`` checks/prepares its multilingual model cache at
  import time. This is normally ``~/.local/cache/argos-translate/spacy``. A missing
  cache may trigger a download even before a translation is requested.
* **Stanza:** the current integration leaves Stanza's download policy at its
  default. Stanza 1.10.1 can check/download resource metadata when creating a new
  pipeline even after an earlier warm-up. Do not assume cached models alone make
  this path network-free; select and prepare ``MINISBD`` for the workflow above.
* **NONE:** disables sentence splitting without loading an SBD model. Translation
  models must still be installed. Each newline-delimited paragraph is translated
  as one segment. Prefer one sentence per line: unsplit multi-sentence input can
  lose content, and long paragraphs can exceed model input limits.

``DEFAULT`` can select Stanza when suitable package data and the optional Stanza
library are present, so it is less explicit than ``MINISBD`` for deployment.

To move to another machine or container, transfer the installed translation
packages **and** the prepared splitter resources, and install matching Python
dependencies for the target platform. Copying only ``.argosmodel`` archives can
miss cached resources. Inspect the active paths in :doc:`settings`; preserve the
same overrides or configure the new paths before importing Argos. Test again with
networking disabled after changing models, dependencies, or splitter settings.

Common problems
-----------------

* **Missing language or route:** inspect ``argospm list`` and install the required
  direction. Reverse directions need separate packages. See :doc:`examples` for
  checking a Python translation route before using it.
* **Index/download failure:** check connectivity and ``ARGOS_PACKAGE_INDEX``. It
  must be a base URL containing ``index.json``, not the filename itself. Refresh
  with ``argospm update`` while connected.
* **Slow first call:** model loading and splitter initialization happen on first
  use. Measure repeated calls in one process separately from startup time.
* **GPU error:** retry with ``ARGOS_DEVICE_TYPE=cpu`` in a new process, then check
  the installed CTranslate2 version's driver/runtime requirements.
* **Unexpected output:** check language codes and model versions. A route through
  an intermediate language can reduce quality. With ``NONE``, shorten long input.
* **Missing files or permission errors:** compare the active account and paths
  used for installation and translation. Services and containers may use different
  XDG directories. Restart after changing configuration.

For help, use the `forum <https://community.libretranslate.com/c/argos-translate/5>`_
or `issue tracker <https://github.com/argosopentech/argos-translate/issues>`_. Include
versions, language directions, settings, and a short reproducible example.
``ARGOS_DEBUG=1`` enables more logging; review logs before sharing because they may
contain the text being translated.
