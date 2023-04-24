Getting Started
===============

Installation
------------

Serl is available on `PyPI <https://pypi.org/project/serl/>`_ and so can be install with `pip <https://pip.pypa.io/>`_:

.. code-block:: console

  $ pip install serl

A Simple Example
----------------

A good place to start would be to go through the :ref:`lang-config`, and try to understand the following example, which just provides a language for simple mathematical expressions:

.. code-block:: yaml

  tokens:
  num: \d+

  precedence:
    - left + -
    - left * /
    - right exp[4]

  grammar:
    exp:
      - exp + exp
      - exp - exp
      - exp * exp
      - exp / exp
      - -exp
      - (exp)
      - num
    
  code:
    exp:
      - exp[0]() + exp[1]()
      - exp[0]() - exp[1]()
      - exp[0]() * exp[1]()
      - exp[0]() / exp[1]()
      - -exp()
      - exp()
      - int(num[0])

