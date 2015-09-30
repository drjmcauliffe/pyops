#!/usr/bin/env bash

# install the pypi requirements.
pip install -r requirements.txt

# install PyAstronomy - needs Numpy to be already installed.
cd ..
git clone https://github.com/sczesla/PyAstronomy.git PyAstronomy
cd PyAstronomy
python setup.py --with-ext install
cd ..

# install svgFig for orbital graphics
wget http://svgfig.googlecode.com/files/svgfig-1.1.2.tgz
tar -xvf svgfig-1.1.2.tgz
rm svgfig-1.1.2.tgz
cd svgfig
python setup.py install
cd ..

# install PySpice - for now! Soon to be updated to SpiceyPy
git clone https://github.com/johnnycakes79/PySPICE.git PySPICE
cd PySPICE
python getspice.py
python setup.py install
cd ..

# finally install e[PY]s
cd pyops
python setup.py install
rm -rf build dist pyops.egg-info
python setup.py test # run tests to check basic functionality

# run an ipython notebook to see if things work
ipython notebook --ip=127.0.0.1