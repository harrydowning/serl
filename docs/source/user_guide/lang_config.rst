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

.. _tokens:

:code:`tokens`
--------------
:Type: ``object``
:Required: ``True``



Token names shouldn't contain whitespace.

.. note ::
  A note on verbose regex

:code:`precedence`
------------------

:code:`sync`
------------

.. _grammar:

:code:`grammar`
---------------

:code:`code`
------------

If you don't want to return anything you can explicitly make the final statement `pass`

:code:`commands`
----------------

:code:`tokentypes`
------------------

:code:`styles`
--------------

:code:`environment`
-------------------
:Type: ``string``
:Required: ``False``

The name of a virtual environment to be created to contain any python dependencies specified in :ref:`requirements`.

specify that manually created environments should be with builtin venv

.. Note::
  When running a language that specifies an environment that doesn't already exist, a new environment will be created and the specified requirements will be installed.

.. _requirements:

:code:`requirements`
--------------------

:code:`meta`
------------
:Type: ``object``
:Required: ``False``

The meta object provides the ability to alter certain aspects of the configuration and language behaviour.

:code:`meta.tokens`
~~~~~~~~~~~~~~~~~~~
:Type: ``object``
:Required: ``False``

Properties relating to the :ref:`tokens` object.

:code:`meta.tokens.ref`
^^^^^^^^^^^^^^^^^^^^^^^
:Type: ``string``, ``null``
:Required: ``False``
:Default: ``^token(?!$)|(?<= )token``

A regex used to determine how tokens can be referenced in other tokens and consequently expanded (substituted).
If the value of this property is set to null or equivalently defined but not given a value :term:`token expansion<Token Expansion>` will not take place.

The special identifier ``token`` is used as a substitute for user-defined token names.
If this special identifier isn't used the defined regex is assumed to be a prefix to the token name.

:Example:

.. code-block:: yaml
  
  meta:
    tokens:
      ref: \$token

In this example the regex for a token named ``text`` defined in the :ref:`tokens` object could be substituted into any other token by specifying ``$text``.
As previously mentioned if the identifier ``token`` is not used the value of ``meta.tokens.ref`` is taken to be a prefix and so this example can be equivialntly specified as:

.. code-block:: yaml
  
  meta:
    tokens:
      ref: \$

.. Note::
  The ``$`` symbol has been escaped because this string is treated as a regex and this has the special meaning of signifying the end of a string.

:code:`meta.tokens.regex`
^^^^^^^^^^^^^^^^^^^^^^^^^
:Type: ``boolean``
:Required: ``False``
:Default: ``False``

:code:`meta.tokens.ignore`
^^^^^^^^^^^^^^^^^^^^^^^^^^
:Type: ``string``
:Required: ``False``
:Default: ``.``

:code:`meta.tokens.flags`
^^^^^^^^^^^^^^^^^^^^^^^^^
:Type: ``string``
:Required: ``False``
:Default: ``VERBOSE``


:code:`meta.grammar`
~~~~~~~~~~~~~~~~~~~~
:Type: ``object``
:Required: ``False``

Properties relating to the :ref:`grammar` object.

:code:`meta.tokens.permissive`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:Type: ``boolean``
:Required: ``False``
:Default: ``True``


:code:`meta.commands`
~~~~~~~~~~~~~~~~~~~~~

:code:`meta.tokens.prefix`
^^^^^^^^^^^^^^^^^^^^^^^^^^