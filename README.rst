e[py]s
======

.. image:: https://travis-ci.org/johnnycakes79/epys.png?branch=master
        :target: https://travis-ci.org/johnnycakes79/epys
.. image:: https://coveralls.io/repos/johnnycakes79/epys/badge.png?branch=master 
		:target: https://coveralls.io/r/johnnycakes79/epys?branch=master


ePYs is a python library for the manipulation, processing and plotting
of the input and output files of ESA Experiment Planning Software (EPS).

.. WARNING::
   This is a very beta-project. It's not on PyPI and can't be installed via PIP.

* Free software: BSD license
* Documentation: http://epys.rtfd.org.

Features
--------

* Read an EPS data-rate output file into a numpy array with instrument header information.

Installation
------------

At the command line::

1. Clone the repo to your local machine::

    $ git clone git@github.com:johnnycakes79/epys.git

3. Install your local copy::

    $ cd epys/
    $ python setup.py install

4. Import and use module::

    $ python
    >>> from epys import epys
