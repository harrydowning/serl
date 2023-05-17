Overview
========

Serl (serialized languages) is a format and corresponding command line tool for creating and using textual domain specific or markup languages with arbitrary syntax.
This is achieved through the concept of :ref:`language configurations <lang-config>`, which are YAML files for specifying language syntax and functionality, used by the tool to execute language programs.
These configurations can then be :ref:`linked <link>`, allowing languages to be used like any other command line tool.

.. toctree::
  :caption: Home
  :hidden:

  self
  glossary

.. toctree::
  :maxdepth: 1
  :caption: User Guide
   
  user_guide/getting_started
  user_guide/lang_config
  user_guide/cli
  user_guide/other

.. user_guide/examples