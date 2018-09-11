.. _config:

HTS configuration files
========================

There are two types of config files: `protocol` and `run_config`::

    * `protocol` defines all tasks that you would like to run on your type of data. This can be data normalization tasks, quality control tasks, and analysis tasks.
    * `run_config` defines everything that is specific your data set, such as paths file I/O, formats and meta data. Also, what `protocol` do use with your data is defined here.


Both `protocol` and `run_config` are based on [configobj](https://configobj.readthedocs.io/) (see [specifications](https://configobj.readthedocs.io/en/latest/configobj.html#the-config-file-format)).

Whenever a `protocol` task requires data specific information (such as a path to save output files) there must be a `run_config` task with the same name.



Run config
----------

(Beware - slightly redundant with [load_data__tutorial](notebooks/load_data__tutorial.ipynb)).


Protocol
---------

Todo: Define!

