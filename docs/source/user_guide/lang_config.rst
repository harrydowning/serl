.. _lang-config:

Language Configuration
======================

Languages are specified with `YAML <https://yaml.org/spec/1.2.2/>`_ syntax. 
This page documents the possible properties/configuration fields.
See the section :ref:`using-yaml` for tips.

:code:`version`
---------------
:Type: ``string``, ``number``
:Required: ``False``

Language version shown with :code:`--version` if :ref:`usage` pattern specified.

:Example:

.. code-block:: yaml

  version: 0.0.1

.. _usage:

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
        -o, --output=FILE  Output file. 


.. Note::
  Command line arguments are available in :ref:`code` through the identifier :code:`args`.
  They will be represented with a dictionary with keys corresponding to positional and optional arguments as shown below.


.. code-block:: console

  $ serl run language -o out.txt example.cfg in.txt
  {
    '--help': False,
    '--output': 'out.txt',
    '--version': False,
    '<config>': 'example.cfg',
    '<src>': 'in.txt'
  }

.. _tokens:

:code:`tokens`
--------------
:Type: ``object``
:Required: ``True``
:Property Type: ``string``

Tokens to be used when constructing the :term:`lexer`.
Tokens are specified as a mapping between a token identifier and regex pattern.
Token identifiers can be used within :term:`grammar productions <grammar production>` as terminals and can contain any character except for whitespace.

Tokens can be referenced and substituted into other tokens through :term:`token expansion <token expansion >`.
See the :ref:`meta-tokens-ref` property for details on the syntax used to reference other tokens.

.. Note::
  Any tokens defined but not used within the :ref:`grammar` will be ignored.
  This could be because those tokens are used only to be substituted into another token for readability.

Tokens can also be specified implicitly.
These are tokens used within a :term:`grammar production` but not defined within this object.
These tokens will be interpreted literally as a fully escaped regex.
For example, if :code:`**` is used but not defined in this object then its corresponding token pattern would be :code:`\\*\\*`.
This is useful for tokens such as operators or delimiters.

.. Note::
  By default, regex patterns will be specified according to Python's `re <https://docs.python.org/3/library/re.html>`_ module with the `verbose <https://docs.python.org/3/library/re.html#re.VERBOSE>`_ flag. 
  However, this can be changed with the :ref:`meta-tokens-regex` and :ref:`meta-tokens-flags` properties respectively.

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

A list of token precedence levels, from lowest (first) to highest (last).
This can be used to disambiguate shift/reduce or reduce/reduce parser conflicts.
Precedence levels are specified with an association type followed by a whitespace separated list of identifiers from the :ref:`tokens` object.
Association type can be ``left``, ``right``, or ``nonassoc``.

The precedence of a specific :ref:`grammar` production can also be overridden by specifying the non-terminal name and position (:code:`name[pos]`).
This will only affect the rightmost terminal of the production.
For example, this could be used to give higher precedence to unary minus.

:Example:

.. code-block:: yaml

  precedence:
    - left + -
    - right * /
    - nonassoc < >
    - right exp[4]


:code:`error`
-------------
:Type: ``string``
:Required: False

The name of an error token to be used in the :ref:`grammar` property.
The error token can be used to support :term:`panic-mode` parsing.
Typically, a good place to use error tokens is before delimiters.

This can be used to find more errors, rather than stop on the first, or if :ref:`meta-grammar-permissive` is set to :code:`True` allow execution to continue.

:Example:

In the following grammar snippet, a new production has been added with the error token (:code:`err`) placed before a semi-colon (marking the end of a statement).

.. code-block:: yaml
  
  error: err
  grammar:
    err-stmt:
      - stmt ;
      - err ;
    stmt: ...

The following would happen if :code:`stmt` contained a syntax error:

* Any symbols pushed onto the stack will be popped off (assuming no error token within :code:`stmt`) until the state corresponding to :code:`err-stmt` is reached.
* All :term:`tokens <token>` will be discarded until a semi-colon.
* The :code:`$.grammar.err-stmt[1]` :term:`production <grammar production>` will be reduced.
* On execution :code:`$.code.err-stmt[1]` will be run.

.. _grammar:

:code:`grammar`
---------------
:Type: ``object``
:Required: ``True`` 
:Property Type: ``string``, ``array[string]``

The language grammar specified as an object of productions.
A grammar production consists of a head and a body, where the head is a non-terminal and the body is an arrangement of terminals (i.e., tokens) and other non-terminals.

A key of this property represents the head of a production, with the value being the corresponding body.
If the value is a list, then each element will be its own grammar production but all will correspond to the same head. 

Whitespace is ignored and so rules can be spread across multiple lines.
The grammar start symbol will be taken as the head of the production defined first.

:Example:

.. code-block:: yaml

  grammar:
    start: # production for start symbol
    non-terminal:
      - # production 0 for non-terminal
      - # production 1 for non-terminal
      - # production 2 for non-terminal

.. _code:

:code:`code`
------------
:Type: ``object``
:Required: ``True`` 
:Property Type: ``string``, ``array[string | null]``

Language functionality specified with code blocks written in Python code or Shell commands.
Defined properties of this object directly correspond to the properties of the :ref:`grammar` object to allow functionality to be associated with syntax.

:Example:

.. code-block:: yaml

  grammar:
    non-terminal: # production

  code:
    non-terminal: # functionality for production

For multiple :term:`productions <grammar production>` with the same non-terminal head, the list elements also correspond.

:Example:

.. code-block:: yaml

  grammar:
    non-terminal:
      - # production 0
      - # production 1
      - # production 2

  code:
    main: # main functionality must come first
    non-terminal:
      - # functionality for non-terminal production 0
      - # functionality for non-terminal production 1
      - # functionality for non-terminal production 2

The return value for properties defined within the :ref:`grammar` object but not within this object will be a Python dictionary of their :ref:`variable-environment`.
Details about return values can be found within :ref:`python-code` or :ref:`shell-commands`.

.. _variable-environment:

Variable Environment
~~~~~~~~~~~~~~~~~~~~

Each code block has access to the global scope and variables of the symbols in the corresponding grammar production i.e., :term:`grammar variables <Grammar Variables >`.
See :term:`non-terminal variables <non-terminal variable >` and :term:`terminal variables <terminal variable >`.

The following variables are initially available in the global scope:

* :code:`__name__`: The name of the executing language
* :code:`args`: A dictionary of the parsed command line argument values (see :ref:`usage`)
* Start symbol :term:`non-terminal variable <non-terminal variable >` (only in main functionality)

:Example:

.. code-block:: yaml
  
  tokens:
    name: (\w+):(\w+)

  grammar:
    tag: |
      <name>
        value
      </name>
    value: ...

  code:
    main: ...
    tag: ...
    value: ...

For the configuration above and the following source (details of :code:`value` omitted):

.. code-block:: console

  <a:b>
    value
  </c:d>


The code block :code:`code.tag` (corresponding to :code:`grammar.tag`) would have access to the following environment:

.. code-block:: python

  {
    # Any global variables, or keyword variables passed down through tag(...)
    '<': ('<',),
    '>': ('>',),
    'name': [('a:b', 'a', 'b'),('c:d', 'c', 'd')],
    'value': <function execute at 0x000002273B488AE0>
  }

.. Note::
  * The :term:`terminal variable <terminal variable >` :code:`name` is returned as a list since the symbol is used multiple times in the :code:`grammar.tag` production.
    Elements of this list correspond to the order they appear in the grammar production.
  * Calling the function :code:`value` will execute the code block :code:`code.value`.



Main functionality
~~~~~~~~~~~~~~~~~~

If the first property doesn't correspond to a defined grammar non-terminal then it acts as the main functionality and is executed in a global context.
This allows code to be executed before and after the main :term:`AST` traversal.

If no main functionality is defined then traversal, and thus execution is initiated with the code of the grammar start symbol.
Otherwise, it is the responsibility of the main function to start traversal, which is done by calling the :term:`non-terminal variable <non-terminal variable >` corresponding to the grammar start symbol.

If the code that initiates execution (either main or start symbol code) returns a value it will be sent to :code:`stdout`.

.. _python-code:

Python Code
~~~~~~~~~~~

Without the :ref:`shell-commands` modifier (:code:`$`), blocks are by default interpreted as normal Python code.

When :term:`non-terminal variables <non-terminal variable >` are called in Python, they can take any number of keyword arguments which will be passed down to the local environment of the called code block. 

.. Note::
  Variables in Python can only be accessed by a `limited character set <https://docs.python.org/3/reference/lexical_analysis.html#identifiers>`_.
  However, :term:`grammar variables <Grammar Variables >` that use characters outside this set can still be accessed through the `locals <https://docs.python.org/3/library/functions.html#locals>`_ or `vars <https://docs.python.org/3/library/functions.html#vars>`_ functions, which allow access to variables with arbitrary names.

The value of the final `Python statement <https://docs.python.org/3/reference/simple_stmts.html#simple-statements>`_ of a code block will be used as the return value.
If you don't wan't to return anything you can explicitly make the final statement :code:`None` or :code:`pass`.

.. Note::
  * Only the value of the final statement is used, and so if this is an assignment (e.g., :code:`a = 5`) then the variable :code:`a` would never be created, but :code:`5` would be returned.
  * If the final statement doesn't have a value (e.g., a function definition) then :code:`None` will be returned.
  * The :code:`return` keyword can only be used in the final statement, but is not strictly necessary.

:Example:

.. code-block:: yaml

  grammar:
    tag: ...

  code:
    main: | # python
      # import modules, create classes/functions etc.
      val = tag() # Main execution on grammar start symbol called 'tag'
      # Do something with val
      val # return val to stdout
    tag: # Code for tag

.. Note::
  Currently available for `VS Code <https://code.visualstudio.com/>`_ the `YAML Embedded Languages <https://marketplace.visualstudio.com/items?itemName=harrydowning.yaml-embedded-languages>`_ extension provides syntax highlighting within YAML block-scalars by specifying the language name in a comment next to the block to highlight as shown above.

.. _shell-commands:

Shell Commands
~~~~~~~~~~~~~~

Shell commands can be used by making the first character of the code-block :code:`$`.
Global, and :term:`grammar variables <Grammar Variables >` can be accessed using the Python `format language <https://docs.python.org/3/library/string.html#format-string-syntax>`_.

Accessing :term:`non-terminal variables <non-terminal variable >` will be equivalent to calling them, although keyword arguments cannot be passed with the `format language <https://docs.python.org/3/library/string.html#format-string-syntax>`_.

.. Note::
  * Use of ``{`` or ``}`` for anything other than format strings require escaping with ``{{`` or  ``}}`` e.g., :code:`$ echo ${{HOME}}`.
  * :term:`Grammar variables <Grammar Variables >` with incompatible syntax with the `format language <https://docs.python.org/3/library/string.html#format-string-syntax>`_, can be accessed through the special key :code:`locals()` e.g., :code:`{locals()[{]}` for a variable named :code:`{`.


The output (:code:`stdout`) of a command will be used as the return value for the code block.
If the command fails it will raise a `CalledProcessError <https://docs.python.org/3/library/subprocess.html#subprocess.CalledProcessError>`_, which if caught allows access to :code:`stderr` and the :code:`returncode`.

:Example:

.. code-block:: yaml

  code:
    non-terminal: $ echo {args[<src>]}


.. _tokentypes:

:code:`tokentypes`
------------------
:Type: ``object``
:Required: ``False``
:Property Type: ``string``

Tokens and corresponding type used in the syntax highlighter lexer.
This is represented as a mapping between token identifiers from the :ref:`tokens` object and a dot separated list in title case (e.g., :code:`Token.Text.Whitespace`) to represent token type.
Arbitrary regex can also be assigned a token type.

.. Important::
  To take advantage of built-in `Pygments styles <https://pygments.org/styles/>`_ it is recommended to use standard tokens names, see `Pygments built-in tokens <https://pygments.org/docs/tokens/#module-pygments.token>`_.


:Example:

.. code-block:: yaml

  tokentypes:
    +: Operator
    '-': Operator
    '*': Operator
    /: Operator
    num: Number

.. _styles:

:code:`styles`
--------------
:Type: ``object``
:Required: ``False``
:Property Type: ``string``

The style to be applied to a certain token type. 
This is represented as a mapping between a token type and a style specified with `Pygments style rules <https://pygments.org/docs/styledevelopment/#style-rules>`_.

:Example:

.. code-block:: yaml

  styles:
    Number: "#42f2f5"
    Keyword.Constant: "bold #ff0000"
    Punctuation: "#f57242"
    String: "#75b54a"
    Whitespace: "bg:#e8dfdf"
    
.. Note::
  The use of quotes around the styles in the above example are necessary, as otherwise the hex colours using :code:`#` would be treated as YAML comments.
  See :ref:`using-yaml` for tips.

See :ref:`static-syntax-highlighting` for more details.

.. _environment:

:code:`environment`
-------------------
:Type: ``string``
:Required: ``False``

The name of a virtual environment to be created to contain any python dependencies specified in :ref:`requirements`.

This is only required if you plan to use dependencies that may clash with those used by the tool or other serl languages used in the same environment.
Not setting this property means that language dependencies are installed to the environment where the instance of the tool being used is installed.

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
If two languages specify an environment with the same name, the environment will be shared.

:Example:

.. code-block:: yaml

  environment: venv-lang

.. _requirements:

:code:`requirements`
--------------------
:Type: ``string``
:Required: ``False``

The required dependencies for the language, which if specified as a `pip requirements <https://pip.pypa.io/en/stable/reference/requirements-file-format/>`_ file, can be automatically downloaded with the command line :ref:`run` option :code:`-r` or :code:`--requirements`.

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

.. _meta-tokens-ref:

:code:`meta.tokens.ref`
^^^^^^^^^^^^^^^^^^^^^^^
:Type: ``string``, ``null``
:Required: ``False``
:Default: ``^token(?!$)|(?<= )token``

A regex used to determine how tokens can be referenced in other tokens and consequently expanded (substituted).
If the value of this property is set to null or equivalently defined but not given a value, :term:`token expansion <token expansion >` will not take place.

The special identifier ``token`` is used as a substitute for user-defined token names.
If this special identifier isn't used the defined regex is assumed to be a prefix to the token name.

:Example:

.. code-block:: yaml
  
  meta:
    tokens:
      ref: \$token

In this example the regex for a token named ``text`` defined in the :ref:`tokens` object could be substituted into any other token by specifying ``$text``.
As previously mentioned if the identifier ``token`` is not used, the value of ``meta.tokens.ref`` is taken to be a prefix and so this example can be equivalently specified as:

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
  
  Run the following two commands in Python's interactive shell to see what implementation you're using:
  
  .. code-block:: console

    $ python
    >>> import platform
    >>> platform.python_implementation()


:Example:

.. code-block:: yaml

  meta:
    tokens:
      regex: True

.. _meta-tokens-ignore:

:code:`meta.tokens.ignore`
^^^^^^^^^^^^^^^^^^^^^^^^^^
:Type: ``string``
:Required: ``False``
:Default: ``.``

A regex specifying characters to be ignored by the :term:`lexer`.
This will have the lowest precedence in the :term:`lexer` and so the default value can be interpreted as any character not matched in a token by the patterns in the :ref:`tokens` object.

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

A whitespace separated list of regex flags for the :term:`lexer` to use corresponding to the regex patterns defined in the :ref:`tokens` object.
Valid flags include any defined in the `re <https://docs.python.org/3/library/re.html>`_ module or if :ref:`meta-tokens-regex` is enabled, any flag in the `regex <https://github.com/mrabarnett/mrab-regex#flags>`__ module.

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

.. _meta-grammar-permissive:

:code:`meta.grammar.permissive`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:Type: ``boolean``
:Required: ``False``
:Default: ``True``

If this property is set to :code:`False`, then language execution will not take place in the event of a syntax error, even if any input was recovered during parsing.

:Example:

.. code-block:: yaml

  meta:
    grammar:
      permissive: False
