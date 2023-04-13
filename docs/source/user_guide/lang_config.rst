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
:Property Type: ``string``



Token names shouldn't contain whitespace.

.. note ::
  A note on verbose regex

:Example:

.. code-block:: yaml

  tokens:
    +: \+
    '-': \-
    '*': \*
    /: /
    (: \(
    ): \)
    num: \d+

:code:`precedence`
------------------
:Type: ``array``
:Required: False
:Item Type: ``string``

A list of token precedence levels with the lowest being the first item in the list.
This can be used to disambiguate shift/reduce or reduce/reduce parser conflicts.
Precedence levels are specified as an association type followed by a whitespace seperated list of tokens.
Association type can be either ``left``, ``right``, or ``nonassoc``.

:Example:

.. code-block:: yaml

  precedence:
    - left + -
    - right * /
    - nonassoc < >


:code:`sync`
------------

.. _grammar:

:code:`grammar`
---------------

.. _code:

:code:`code`
------------
:Type: ``object``
:Required: ``True`` 
:Property Type: ``string``, ``array[string | null]``

Language functionality specified with either Python or shell commands.
Defined properties of this object directly correspond to the properties of the :ref:`grammar` object to allow functionality to be associated with syntax.

:Example:

.. code-block:: yaml

  grammar:
    non-termianl: ... # production

  code:
    non-termianl: ... # functionality for production

For non-terminals with multiple productions the same applies but the list elements also correspond.

:Example:

.. code-block:: yaml

  grammar:
    non-termianl:
      - ... # production 1
      - ... # production 2
      - ... # production 3

  code:
    non-termianl:
      - ... # functionality for production 1
      - ... # functionality for production 2
      - ... # functionality for production 3

Properties defined within this object but not within the :ref:`grammar` object will be ignored, except for the first property, but only if it doesn't have a corresponding property in the :ref:`grammar` object.
This property is taken as the main or entry point, allowing the user to write any .
Without this property the entry point will be the property corresponding to the grammar start non-terminal.

The functionality for properties defined within the :ref:`grammar` object but not within this object will default to returning a Python dictionary of their local values.

The following sections provide more detail regarding the two functionality modes.

Python Code
~~~~~~~~~~~

If you don't want to return anything you can explicitly make the final statement ``pass``

:Example:

.. code-block:: yaml

  code:
    main: | # python
      # import modules ...
      # Create classes/functions ...
      start() # Result of grammar start non-terminal
    
    start: | # python
      # Code for start
    ...

.. Note::
  Currently available for `VS Code <https://code.visualstudio.com/>`_ the `YAML Embedded Languages <https://marketplace.visualstudio.com/items?itemName=harrydowning.yaml-embedded-languages>`_ extension provides syntax highlighting within YAML block-scalars by specifying the language name in a comment next to the block to highlight as shown above.

Shell Commands
~~~~~~~~~~~~~~
Shell commands can be used by making the first character of the property value :code:`$`.
Global, local, and :term:`grammar variables` can be accessed through the Python `format language <https://docs.python.org/3/library/string.html#format-string-syntax>`_.

.. Note::
  Use of ``{`` or ``}`` in other contexts than for format strings require escaping with ``{{`` or  ``}}``.

:Example:

.. code-block:: yaml

  code:
    non-termianl: $ echo {args[<src>]}


:code:`tokentypes`
------------------
:Type: ``object``
:Required: ``False``
:Property Type: ``string``



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
:Type: ``string``
:Required: ``False``

The required dependencies for the languages, which if specified as a pip requirements file, can be automatically downloaed with the command line :ref:`run` option :code:`-r` or :code:`--requirements`.

:Example:

.. code-block:: yaml

  requirements: | # pip
    PyYAML==6.0
    docopt==0.6.2
    ply==3.11
    regex==2022.10.31
    networkx==2.8.8
    jsonschema==4.17.3
    Pygments==2.13.0
    Pillow==9.4.0
    requests==2.28.2
    
    # Dev
    pytest==7.2.2
    pytest-cov==4.0.0

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

A regex specifying characters to be ignored by the lexer.
This will have the lowest precedence in the lexer and so the default value can be interpreted as any character not matched in a token by the patterns in the :ref:`tokens` object.

.. Note::
  The regex flags used for this property will be the same as those used in the :ref:`tokens` object.
  Therefore, changes to the :ref:`meta-tokens-flags` will also be reflected here.

:Example:

.. code-block:: yaml

  meta:
    tokens:
      ignore: \s

.. _meta-tokens-flags:

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
