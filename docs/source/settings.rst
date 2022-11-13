
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

Set packages dir
----------------

.. code-block:: sh

  export ARGOS_PACKAGES_DIR="/home/user/.local/share/argos-translate/packages/"

Set device
----------

.. code-block:: sh

  export ARGOS_DEVICE_TYPE="cpu"
  export ARGOS_DEVICE_TYPE="cuda"
