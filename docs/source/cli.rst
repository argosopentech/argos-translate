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
