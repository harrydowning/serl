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
The name of the symbolic link (:code:`<language>`) should be the same as the name of a language in the :term:`system configuration <system configuration >`.
This allows a language to be used directly through the symbolic link, where the command :code:`serl run <language> ...` would be equivalent to :code:`<language> ...`.

.. Note::
  If the symbolic link is created in a directory on the path, or specified as such with :code:`<dir>`, then the language can be used as a system-wide command.

Arguments provided to a linked language will be interpreted as arguments of the language rather than the tool.
Any arguments meant for the tool should come before :code:`--`. 
This means there is an implicit :code:`--` after the language name if not specified elsewhere.
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
      --style-defs-arg=ARG          Argument supplied to style-defs.

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

The install command can be used to add a language to the :term:`system configuration <system configuration >`.
The specified :code:`<language>` can either be a relative or absolute file path, or a HTTP URL which when resolved returns a language configuration.
Installed languages can be renamed by specifying an :code:`<alias>`.

.. Note::
  Languages are determined uniquely by their filename.
  This means that multiple languages in the :term:`system configuration <system configuration >` cannot have the same name.
  By default, the install command won't override languages in the :term:`system configuration <system configuration >`, however this can be changed with the :code:`-U` or :code:`--upgrade` command.
  This ensures languages won't be accidentally overridden.

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

:Description:

The uninstall command can be used to remove languages or :ref:`environments <environment>` from the :term:`system configuration <system configuration >`.

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

:Description:

The list command can be used to display all installed languages or :ref:`environments <environment>`.

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
      --style-defs-arg=ARG          Argument supplied to style-defs.

  Options:
      -h, --help     Show this screen.
      -V, --version  Show version.
      -v, --verbose  Provide more output.

:Description:

The run command is used to execute a source program for a specific language configuration (:code:`<language>`).
If :code:`-r` or :code:`--requirements` is specified then the dependencies in the :ref:`requirements` property will be installed with `pip <https://pip.pypa.io/>`_.
These dependencies will be installed to the same environment that the tool is installed to or to the specified :ref:`environment`, if it is set.

If no :ref:`usage` pattern is defined in the language configuration, then the first argument of :code:`<args>` is taken to be the source file.
Otherwise, see :ref:`usage`.

.. _static-syntax-highlighting:

Static Syntax Highlighting
~~~~~~~~~~~~~~~~~~~~~~~~~~

The run command also allows static syntax highlighting to be performed on a language source file.
Highlighting is performed by `Pygments <https://pygments.org/>`_ and always starts with a default to limit the work of the user.

The :ref:`tokentypes` property can be used to override the default lexer, which tags anything matched by a pattern in :ref:`tokens` as :code:`Token.Text` and anything matched by :ref:`meta-tokens-ignore` as :code:`Token.Comment`.

The :ref:`styles` property can be used add style to user defined token types, or to override the style of token types in `Pygments default style <https://pygments.org/styles/#default>`_ or another `Pygments style <https://pygments.org/styles/>`_ specified with the :code:`style` key of :code:`--format-options`.

The output format is determined by the file extension of the :code:`-H` or :code:`--highlight` option.
Alternatively, it can be specified with the :code:`-f` or :code:`--format` option.

`Pygments <https://pygments.org/>`_ comes with a range of `formatters <https://pygments.org/docs/formatters/>`_ that can be used.
Each of which has there own options that can be specified with :code:`-O` or :code:`--format-options`.

.. Tip::
  Some particularly useful format options are :code:`style`, :code:`full`, and :code:`linenos`.
  Also see :code:`noclasses` for HTML snippets.

These format options can be specified as comma-separated list of :code:`key=value` pairs.
The :code:`value` will be interpreted as a Python expression, however if that fails, it will fall back to a string.
Setting boolean values to :code:`True` can use the shortcut notation of just :code:`key`.

.. Note::
  Format options can contain whitespace but only if grouped on the command line e.g., surrounded with quotes.

:Example:

.. code-block:: console

  $ serl run -H example.html -O style=github-dark,full,linenos <language> <src>


help
--------
:Usage:

.. code-block:: console

  $ serl help help
  serl help

  Usage:
      help [<command>]

:Description:

The help command is used to display the various tool usage patterns seen on this page.
