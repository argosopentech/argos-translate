Command Line Interface
======================

.. code-block:: sh

  argos-translate --from-lang en --to-lang es "Hello World"
  Hola Mundo

  echo "Text to translate" | argos-translate --from-lang en --to-lang es
  Texto para traducir

  argospm --help
  usage: argospm [-h] {update,search,install,list,remove} ...

  positional arguments:
    {update,search,install,list,remove}
                          Available commands.
      update              Downloads remote package index.
      search              Search package from remote index.
      install             Install package.
      list                List installed packages.
      remove              Remove installed package.

  optional arguments:
    -h, --help            show this help message and exit



Translate a string from English to Spanish:

Install the required direction first with ``argospm install translate-en_es``.
Missing languages or routes produce a command-line error.

.. code-block:: sh


    argos-translate --from-lang en --to-lang es "Hello World."
    Hola Mundo



Translate with shorter flag names:

.. code-block:: sh


    argos-translate -f en -t es "Hello World."
    Hola Mundo



Translate longer text piped into ``argos-translate``::


    echo "Text to translate" | argos-translate --from-lang en --to-lang es
    Texto para traducir



Update
------
Downloads the remote package index (requires internet access).

.. code-block:: sh

  argospm update

Search
------
Search the local index; download it if missing. Run ``argospm update`` to refresh it.

.. code-block:: sh

  argospm search --from-lang en --to-lang es

Install
---------
Install package.

.. code-block:: sh

  argospm install translate-en_es

List
------
List installed packages.

.. code-block:: sh

  argospm list

Remove
------
Remove installed package.

.. code-block:: sh

  argospm remove translate-en_es

Enable tab completion for Bash
------------------------------

.. code-block:: bash

  mkdir -p ~/.local/share/bash-completion/completions
  curl -fsSL https://raw.githubusercontent.com/argosopentech/argos-translate/master/scripts/completion.bash -o ~/.local/share/bash-completion/completions/argospm
  source ~/.local/share/bash-completion/completions/argospm


Importing new pairs through the CLI
-------------------------------------

* Update list of available language pairs: `argospm update`
* List all available language pairs: `argospm search`
* Install new pair syntax: `argospm install *lang_pair_name*`

For example, install Turkish to English pair: `argospm install translate-tr_en`

Installing every available package can use substantial bandwidth and storage::

    argospm install translate



Removing a pair through the CLI
---------------------------------

1. Remove the Turkish to English pair: `argospm remove translate-tr_en`

Inspect ``argospm list`` before removing all installed pairs::

    for i in $(argospm list); do argospm remove $i ; done
