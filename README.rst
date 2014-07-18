e[py]s
======

.. image:: https://pypip.in/v/epys/badge.png
        :target: https://pypi.python.org/pypi/epys/
        
.. image:: https://travis-ci.org/johnnycakes79/epys.png?branch=master
        :target: https://travis-ci.org/johnnycakes79/epys/
        
.. image:: https://coveralls.io/repos/johnnycakes79/epys/badge.png?branch=master
        :target: https://coveralls.io/r/johnnycakes79/epys/

.. image:: https://pypip.in/d/epys/badge.png
        :target: https://pypi.python.org/pypi/epys/

.. image:: https://pypip.in/egg/epys/badge.png
        :target: https://pypi.python.org/pypi/epys/

.. image:: https://pypip.in/wheel/epys/badge.png
        :target: https://pypi.python.org/pypi/epys/

.. image:: https://pypip.in/license/epys/badge.png
        :target: https://pypi.python.org/pypi/epys/


ePYs is a python library for the manipulation, processing and plotting
of the input and output files of ESA Experiment Planning Software (EPS).

* Free software: BSD license
* Documentation: http://epys.rtfd.org.

Modules
-------
* **draw** makes pretty orbit graphics
* **events** provides a series of time/date utilities
* **maps** does things with maps and images
* **orbit** processes mission analysis orbit files
* **read** reads EPS/MAPPS output into useable dataframes and/or arrays
* **utils** more utilities ...

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

Testing
-------

Testing is very little at the moment. But it's a start... At the command line::

1. Run py.test::

    $ python setup.py test
