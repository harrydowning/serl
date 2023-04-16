Other
=====

.. _using-yaml:

Using YAML
----------

.. Important::
  The current version of the tool accepts `YAML 1.1 <https://yaml.org/spec/1.1/current.html>`_ parsed by `PyYAML <https://pypi.org/project/PyYAML/>`_.
  See `YAML Specification Changes <https://yaml.org/spec/1.2.2/ext/changes/>`_.

When using YAML it is recommended, when possible, to use either `plain style <https://yaml.org/spec/1.2.2/#733-plain-style>`_ or `block-scalars <https://yaml.org/spec/1.2.2/#81-block-scalar-styles>`_ to write regex and code blocks.
This is because their contents are interpreted literally and so there is no need to escape values (particularly useful for regex).
Writing code with block-scalars provides an experience most similar to a text editor.

:Example:

.. code-block:: yaml

  example1: This is an example of plain style
  example2: |
    This is an example 
    of a block-scalar


However, it is important to know when `plain style <https://yaml.org/spec/1.2.2/#733-plain-style>`_ specifically is not appropriate.
In particular, this is the case when values clash with the syntax of YAML.
An example of this could be writing a regex or code block using :code:`[ ... ]`, which would be interpreted as a YAML array.

:Example:

.. code-block:: 

  tokens:
    [: \[ # incorrect
    '[': '\[' # correct

  code:
    list: [...] # incorrect: YAML array
    list: '[...]' # correct: Python code
    list: | # correct: Python code using YAML block-scalar
      [...]


.. Tip::
  It is recommended to write YAML with a good syntax highlighter as this will give a visual prompt when values may be misinterpreted.

It is possible to write languages with `JSON <https://www.json.org/json-en.html>`_ as YAML is a `strict superset <https://yaml.org/spec/1.2.2/#12-yaml-history>`_.
However, this is not recommended as it would be far less readable and harder to write regex.
