
Settings
======================

Argos Translate can be configured either by setting environment variables or editing the config file.

~/.config/argos-translate/settings.json
.. code-block:: json

   {
     "ARGOS_DEBUG": "1",
     "ARGOS_PACKAGE_INDEX": "https://raw.githubusercontent.com/argosopentech/argospm-index/main/"
   }


.. code-block:: sh

  export ARGOS_DEBUG=1
  export ARGOS_PACKAGE_INDEX="https://raw.githubusercontent.com/argosopentech/argospm-index/main"

Set package index
-----------------

Reads package index at https://raw.githubusercontent.com/argosopentech/argospm-index/main/index.json

.. code-block:: sh

  export ARGOS_PACKAGE_INDEX="https://raw.githubusercontent.com/argosopentech/argospm-index/main"

View debugging information
--------------------------

Argos Translate prints more verbose logging 

.. code-block:: sh

  export ARGOS_DEBUG=1

Chunk Type
--------------------------

Configure Sentence Boundary Detection (SBD) model

The seq2seq neural networks that Argos Translate uses for translation can only handle
~150 tokens of input at at time. Argos Translate uses a separate SBD model to split
text into sentences before translation. By default Argos Translate uses 
`MiniSBD <https://github.com/LibreTranslate/MiniSBD>`_, however, Stanza and Spacy are
also supported.

.. code-block:: sh

  pip install "argostranslate[stanza]" # Stanza/PyTorch is an optional dependency
  export ARGOS_CHUNK_TYPE="STANZA"

.. code-block:: sh

  export ARGOS_CHUNK_TYPE="SPACY"

.. code-block:: sh

  export ARGOS_CHUNK_TYPE="NONE"

.. code-block:: sh

  export ARGOS_CHUNK_TYPE="DEFAULT"

Set packages dir
----------------

This is the directory that Argos Translate saves installed packages to.

.. code-block:: sh

  export ARGOS_PACKAGES_DIR="/home/user/.local/share/argos-translate/packages/"

Set device
----------

.. code-block:: sh

  export ARGOS_DEVICE_TYPE="cpu"
  export ARGOS_DEVICE_TYPE="cuda"

Set max loaded models
---------------------

Cap on the number of resident translation models. 0 (default) keeps every
model loaded; a positive value evicts the least recently used model when
the cap is exceeded.

.. code-block:: sh

  export ARGOS_MAX_LOADED_MODELS="0"
