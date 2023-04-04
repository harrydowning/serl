.. _lang-config:

Language Configuration
======================

Languages are specified with `YAML <https://yaml.org/spec/1.2.2/>`_ syntax. 
This page documents the possible configuration fields.
See the section :ref:`using-yaml` for tips.

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

.. Note::
  Add how this can be accessed in code. And command?

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

.. _code:

:code:`code`
------------
:Type: ``object``
:Required: ``True`` or ``commands``
:Property Type: ``str``, ``list[str | null]``

If you don't want to return anything you can explicitly make the final statement ``pass``

:code:`commands`
----------------
:Type: ``object``
:Required: ``True`` or ``code``
:Property Type: ``str``, ``list[str | null]``

.. Note::
  To be able to access values with identifiers containing special characters not normally allowed within environment variables ensure the more explicit syntax ``${...}`` is used e.g., ``${*${}``.
  The exception is the character ``}`` which can't be referenced with any syntax.

.. Note::
  In general it is also recommened to use Unix style environment variable syntax (``$...`` and ``${...}``) as this makes languages more portable since these are also supported on Windows.


:code:`tokentypes`
------------------

:code:`styles`
--------------
:Type: ``object``
:Required: ``False``
:Property Type: ``string``

A mapping between `built-in <https://pygments.org/docs/tokens/>`_ or user-defined :term:`token types`, and styles specified in the format of `Pygments <https://pygments.org/>`_ `style rules <https://pygments.org/docs/styledevelopment/#style-rules>`_.
These styles will override those used by the :term:`base style`.

:Example:

.. code-block:: yaml

  styles:
    Number: "#42f2f5"
    Keyword.Constant: "bold #ff0000"
    Punctuation: "#f57242"
    String: "#75b54a"
    Whitespace: "bg:#e8dfdf"
    
.. Note::
  The use of quotes around the styles in the above example are neccessary, as otherwise the hex colours would be treated as YAML comments and ``:`` would try to create another mapping.
  See :ref:`using-yaml` for tips.

:code:`environment`
-------------------
:Type: ``string``
:Required: ``False``

The name of a virtual environment to be created to contain any python dependencies specified in :ref:`requirements`.

This is only required if you plan to use dependencies that may clash with those used by the tool or other serl languages used in the same environemnt.
Not setting this property means that language dependencies are installed to the environemnt where the instance of the tool being used was installed.

To list the dependencies used by the tool and then get a specific version thereof you can use:

.. code-block:: console

  $ pip show serl
  $ pip show <dependency>

.. Note::
  When running a language that specifies an environment that doesn't already exist, a new environment will be created and the specified requirements will be installed.
  This may take a bit of time to complete but will only be run once unless the environment is removed.

Environments are created using the `venv <https://docs.python.org/3/library/venv.html>`_ module from the Python `standard library <https://docs.python.org/3/library/>`_ and are located in the directory ``~/.serl/environments``.

Environments can be manually created, however they must be created in the aforementioned directory and with the same `venv <https://docs.python.org/3/library/venv.html>`_ module.
Creating environments manually would still require setting the value of this property to the name of the environment directory.

:Example:

.. code-block:: yaml

  environment: venv-lang

.. _requirements:

:code:`requirements`
--------------------

:code:`meta`
------------
:Type: ``object``
:Required: ``False``

The meta object provides the ability to alter certain aspects of the configuration or language behaviour.

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
If the value of this property is set to null or equivalently defined but not given a value, :term:`token expansion` will not take place.

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

.. _meta-tokens-regex:

:code:`meta.tokens.regex`
^^^^^^^^^^^^^^^^^^^^^^^^^
:Type: ``boolean``
:Required: ``False``
:Default: ``False``

Setting this property to :code:`True` allows for the use of the more feature rich 3rd party `regex <https://github.com/mrabarnett/mrab-regex>`_ module for patterns in the :ref:`tokens` object.

.. Important::
  When used this will change the interface for language captures.
  Specifically, they will now be returned as a list rather than a single value.
  This is due to the fact that the `regex <https://github.com/mrabarnett/mrab-regex>`_ package offers the ability to retain all captures within a group even when modified by a regex quantifier.

.. Note::
  The `regex <https://github.com/mrabarnett/mrab-regex>`_ module may only be used with CPython implementations.
  
  Run the following two commands in Python's interactive shell to see what implmentation you're using:
  
  .. code-block:: console

    $ python
    >>> import platform
    >>> platform.python_implementation()


:Example:

.. code-block:: yaml

  meta:
    tokens:
      regex: True

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

A whitespace seperated list of regex flags for the lexer to use corresponding to the regex patterns defined in the :ref:`tokens` object.
Valid flags include any defined in the `re <https://docs.python.org/3/library/re.html#flags>`_ module or if :ref:`meta-tokens-regex` is enabled, any flag in the `regex <https://github.com/mrabarnett/mrab-regex#flags>`__ module.

:Example:

.. code-block:: yaml

  meta:
    tokens:
      flags: VERBOSE MULTILINE I

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
