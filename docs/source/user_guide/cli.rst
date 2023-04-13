Command Line Interface
======================

This page documents the tool's command line interface. 
The following usage pattern shows the tool's main interface.

:Usage:

.. code-block:: console
  
  $ serl help
  serl

  Usage:
      serl [options] <command> [<args>...]

  Commands:
      link       Create a language symbolic link.
      install    install language to .serl in home directory.
      uninstall  Uninstall language from .serl in home directory.       
      list       list installed languages.
      run        Execute language.
      help       Show help for commands.

  Options:
      -h, --help     Show this screen.
      -V, --version  Show version.
      -v, --verbose  Provide more output.


link
----
:Usage:

.. code-block:: console

  $ serl help link
  serl link

  Usage:
      link [options] <language> [<dir>]

  Options:
      -h, --help     Show this screen.
      -V, --version  Show version.
      -v, --verbose  Provide more output.

:Description:

The link command can be used to create a `symbolic link <https://en.wikipedia.org/wiki/Symbolic_link>`_ for a language.
The name of the symbolic link (:code:`<language>`) should be the same as the name of a language in the :term:`system configuration`.
This allows a language to be used directly through the symbolic link, where the command :code:`serl run <language> ...` would be equivalent to :code:`<language> ...`.

.. Note::
  If the symbolic link is created in a directory on the path, or specified as such with :code:`<dir>`, then the language can be used as a system-wide command.

Arguments provided to a linked language will be interpreted as arguemnts of the language rather than the tool.
Any arguments meant for the tool should come before :code:`--`. 
This means there is an implicit :code:`--` after the langage name if not specified elsewhere.
The below usage pattern shows how the tool can be used with symbolic links.

:Usage:

.. code-block:: console

  $ (language) --help --
  serl

  Usage:
      (language) [options] -- [<args>...]

  Symlink Options:
      --where  Show symlink src location.

  Run Options:
      -r, --requirements            Install pip requirements.
      --debug-lexer                 Output tokens found line-by-line.
      --debug-parser=FILE           Create parser state file.
      -H, --highlight=FILE          Create highlighted version of <src> in the
                                    format of the extension of FILE.
      -f, --format=FORMAT           Override file extension format.
      -O, --format-options=OPTIONS  Options supplied to formatter.
      --style-defs=FILE             Output highlight style defs to FILE.

  Options:
      -h, --help     Show this screen.
      -V, --version  Show version.
      -v, --verbose  Provide more output.

install
-------
:Usage:

.. code-block:: console

  $ serl help install
  serl install

  Usage:
      install [options] <language> [(as <alias>)]

  Install Options:
      -U, --upgrade  Override installed language if present.

  Options:
      -h, --help     Show this screen.
      -V, --version  Show version.
      -v, --verbose  Provide more output.

:Description:

The install command can be used to install a language to the :term:`system configuration`.
The specified :code:`<language>` can either be a relative or absolute file path, or a http URL which when resolved returns a language configuration.

.. Note::
  Languages are determined uniquely by their filename.
  This means that two langauges in the :term:`system configuration` can't have the same name.
  By default, the install command won't override langauges in the :term:`system configuration`, however this can be changed with the :code:`-U` or :code:`--upgrade` command.
  This ensures languages won't be accidently overriden.

uninstall
---------
:Usage:

.. code-block:: console

  $ serl help uninstall
  serl uninstall

  Usage:
      uninstall [options] [<language>...]
      uninstall [options] --venv [<env>...]

  Options:
      -h, --help     Show this screen.
      -V, --version  Show version.
      -v, --verbose  Provide more output.


list
----
:Usage:

.. code-block:: console

  $ serl help list
  serl list

  Usage:
      list [options]

  List Options:
      --venv  List installed virtual environments.

  Options:
      -h, --help     Show this screen.
      -V, --version  Show version.
      -v, --verbose  Provide more output.

.. _run:

run
---
:Usage:

.. code-block:: console

  $ serl help run
  serl run

  Usage:
      run [options] <language> [<args>...]

  Run Options:
      -r, --requirements            Install pip requirements.
      --debug-lexer                 Output tokens found line-by-line.   
      --debug-parser=FILE           Create parser state file.
      -H, --highlight=FILE          Create highlighted version of <src> in the
                                    format of the extension of FILE.    
      -f, --format=FORMAT           Override file extension format.     
      -O, --format-options=OPTIONS  Options supplied to formatter.      
      --style-defs=FILE             Output highlight style defs to FILE.

  Options:
      -h, --help     Show this screen.
      -V, --version  Show version.
      -v, --verbose  Provide more output.


help
--------
:Usage:

.. code-block:: console

  $ serl help help
  serl help

  Usage:
      help [<command>]

