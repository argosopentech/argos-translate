
Settings
======================

Argos Translate can be configured either by setting environment variables or editing the config file.

Environment variables take precedence over the config file. Set them before
starting Python; restart the process after changing settings. The default file is
``~/.config/argos-translate/settings.json``.

.. code-block:: json

   {
     "ARGOS_DEBUG": "1",
     "ARGOS_PACKAGE_INDEX": "https://raw.githubusercontent.com/argosopentech/argospm-index/main/"
   }


.. code-block:: sh

  export ARGOS_DEBUG=1
  export ARGOS_PACKAGE_INDEX="https://raw.githubusercontent.com/argosopentech/argospm-index/main/"

Set package index
-----------------

Reads package index at https://raw.githubusercontent.com/argosopentech/argospm-index/main/index.json

.. code-block:: sh

  export ARGOS_PACKAGE_INDEX="https://raw.githubusercontent.com/argosopentech/argospm-index/main/"

View debugging information
--------------------------

Argos Translate prints more verbose logging

.. code-block:: sh

  export ARGOS_DEBUG=1

Chunk Type
--------------------------

Configure Sentence Boundary Detection (SBD) model

Translation models work best on short segments. Argos Translate uses a separate
SBD model to split paragraphs into sentences. ``DEFAULT`` (also named
``ARGOSTRANSLATE``) uses packaged Stanza data when available and Stanza is installed;
otherwise it uses `MiniSBD <https://github.com/LibreTranslate/MiniSBD>`_. Packages
containing MiniSBD data take precedence over packaged Stanza data.
Choose one of the following options; these are alternatives, not sequential steps.
See :doc:`troubleshooting` for offline preparation.

.. code-block:: sh

  pip install "argostranslate[stanza]" # Stanza/PyTorch is an optional dependency
  export ARGOS_CHUNK_TYPE="STANZA"

.. code-block:: sh

  export ARGOS_CHUNK_TYPE="SPACY"

.. code-block:: sh

  export ARGOS_CHUNK_TYPE="MINISBD"

.. code-block:: sh

  export ARGOS_CHUNK_TYPE="NONE"

.. code-block:: sh

  export ARGOS_CHUNK_TYPE="DEFAULT"

``NONE`` disables sentence splitting and loads no SBD model. Each paragraph is
translated as one segment; newline boundaries are still preserved. Prefer
already segmented input, such as one sentence per line. Unsplit multi-sentence
paragraphs can reduce quality or omit content; long inputs can exceed model limits.

Set packages dir
----------------

This is the directory that Argos Translate saves installed packages to.

.. code-block:: sh

  export ARGOS_PACKAGES_DIR="/home/user/.local/share/argos-translate/packages/"

Set device
----------

.. code-block:: sh

  export ARGOS_DEVICE_TYPE="cuda"

The default is ``cpu``; ``auto`` lets CTranslate2 select a device. CUDA requires
a compatible GPU, driver, and runtime. See the
`CTranslate2 installation guide <https://opennmt.net/CTranslate2/installation.html>`_.

Performance settings
----------------------

These settings can also be supplied in ``settings.json``. Benchmark on your own
hardware; compute types can change memory use, speed, and translation quality.
There is no universally fastest or most accurate setting.

.. list-table::
   :header-rows: 1

   * - Variable
     - Default
     - Meaning
   * - ``ARGOS_COMPUTE_TYPE``
     - ``auto``
     - CTranslate2 compute type, e.g. ``float32``, ``float16``, ``int8``, or ``int8_float32``; hardware support varies.
   * - ``ARGOS_INTER_THREADS``
     - ``1``
     - Number of CTranslate2 workers (positive integer).
   * - ``ARGOS_INTRA_THREADS``
     - ``0``
     - Threads per worker; ``0`` uses CTranslate2's default selection.
   * - ``ARGOS_BATCH_SIZE``
     - ``32``
     - Maximum batch size in tokens, not documents (positive integer).
   * - ``ARGOS_BEAM_SIZE``
     - ``4``
     - Beam size; requesting more hypotheses may increase it.

Directories and other settings
--------------------------------

Data defaults to ``~/.local/share/argos-translate``, cache to
``~/.local/cache/argos-translate``, and configuration to ``~/.config/argos-translate``.
``XDG_DATA_HOME``, ``XDG_CACHE_HOME``, and ``XDG_CONFIG_HOME`` change the respective
base directories; Argos appends ``argos-translate``. Set XDG variables in the
environment, not in ``settings.json``. Snap uses ``SNAP_USER_DATA`` as its home.

Print the active paths before copying models or deleting cached files:

.. code-block:: sh

   python -c "from argostranslate import settings as s; print(s.data_dir); print(s.cache_dir); print(s.settings_file); print(s.package_dirs)"

``ARGOS_MODEL_PROVIDER`` defaults to ``OPENNMT`` for local translation. Optional
``LIBRETRANSLATE`` and ``OPENAI`` providers require network access and may require
``LIBRETRANSLATE_API_KEY`` or ``OPENAI_API_KEY``. They are not needed for offline use.

In PowerShell use ``$env:ARGOS_CHUNK_TYPE = "NONE"`` instead of ``export``.
