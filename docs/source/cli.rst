Command Line Interface
======================

.. code-block:: python

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
    


Translate a string from English to Spanish.

Note: If you do not have the language pair that you are calling installed, you will get a `Traceback` error.::


    argos-translate --from-lang en --to-lang es "Hello World."
    Hola Mundo


Translate longer text piped into `argos-translate`.::


    echo "Text to translate" | argos-translate --from-lang en --to-lang es
    Texto para traducir



Update
------
Downloads remote package index.

.. code-block:: sh

  argospm update
		
Search
------
Search package from remote index.

.. code-block:: sh

  argospm search --from-lang en --to-lang es		

Install
------
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

  curl -sSL https://raw.githubusercontent.com/argosopentech/argos-translate/master/scripts/completion.bash > /etc/bash_completion.d/argospm.bash
  
  
Importing new pairs through the CLI
------

* Update list of available language pairs: `argospm update`
* List all available language pairs: `argospm search`
* Install new pair syntax: `argospm install *lang_pair_name*`

For example, install Turkish to English pair: `argospm install translate-tr_en`

Optionally, you could install all language pairs using BASH.::

    for i in $(argospm search | sed 's/:.*$//g'); do argospm install $i ; done
    


Removing a pair through the CLI
------

1. Remove the Turkish to English pair: `argospm remove translate-tr_en`

Optionally, you could remove all language pairs using BASH if you need to free space fast.

    for i in $(argospm list); do argospm remove $i ; done
