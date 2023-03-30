.. _lang-config:
Language Configuration
======================

Languages are specified with `YAML <https://yaml.org/spec/1.2.2/>`_ syntax. 
This page documents the possible configuration fields.
See the section :ref:`using-yaml` for YAML tips.

:code:`version`
---------------
:Type: ``string``, ``number``
:Required: ``False``

Language version shown with :code:`--version` if usage pattern specified.

:Example:

.. code-block:: yaml

  version: 0.0.1

:code:`usage`
-------------
:Type: ``string``
:Required: ``False``

Command line usage pattern specified with the `Docopt <http://docopt.org/>`_ language.
This will be run with :code:`options_first=False` and so options can occur in any order around positional arguments.

The only reserved identifier is the positional argument :code:`<src>`, which is used to locate the language input file.
It can be used in the following ways:

- Using :code:`[<src>]` means the input will be read from the file :code:`<src>` or from ``stdin`` if the positional argument is not provided.
- Using :code:`<src>` means the input will only be read from the file :code:`<src>`.
- Not using it at all means the input will always be read from ``stdin``.



:Example:

.. code-block:: yaml

  usage: |
    language

    Usage:
        language [options] <config> [<src>]

    Options:
        -h, --help         Show this screen.
        -v, --version      Show version.
        -o, --output=FILE  Ouput file. 

:code:`tokens`
--------------
Token names shouldn't contain whitespace.

.. note ::
  A note on verbose regex

:code:`precedence`
------------------

:code:`sync`
------------

:code:`grammar`
---------------

:code:`code`
------------

:code:`commands`
----------------

:code:`tokentypes`
------------------

:code:`styles`
--------------

:code:`environment`
-------------------
specify that manually created environments should be with builtin venv


:code:`requirements`
--------------------

:code:`meta`
------------