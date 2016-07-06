.. _install:


Installation
============


We recommend to install HTS in a `virtual environment <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_.

HTS uses `GPy <http://sheffieldml.github.io/GPy/>`_ for Gaussian process normalization. GPy itself requires numpy at setup time::

    $ pip install numpy



With pip (or pip3) configured for Python3, you can install the latest version of HTS directly from Github.::

    $ pip install git+https://github.com/elkeschaper/hts.git


GPy is under constant development, and it might be useful to deinstall the PyPi version installed by default, and instead install the `latest develop version <https://github.com/SheffieldML/GPy>`_::

     $ pip install git+https://github.com/SheffieldML/GPy.git


Once HTS is available on Pypi, try::

    $ pip install hts




Now you can import hts in your Python3 project::

    import hts


