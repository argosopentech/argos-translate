
Settings
======================


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
text into sentences before translation. By default, Argos Translate uses the
Stanza SBD model when available. Spacy is used as a fallback when Stanza is not available
and is typically faster than Stanza. However, Spacy doesn't support as many languages
as Stanza.

.. code-block:: sh

  export ARGOS_CHUNK_TYPE="SPACY"

Set packages dir
----------------

.. code-block:: sh

  export ARGOS_PACKAGES_DIR="/home/user/.local/share/argos-translate/packages/"

Set device
----------

.. code-block:: sh

  export ARGOS_DEVICE_TYPE="cpu"
  export ARGOS_DEVICE_TYPE="cuda"
