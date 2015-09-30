 * authors and contributing defined as local variables
 * cleaning up the documentation and trying to autogenerate a changelog from git - not working so far
 * fixed a few linted errors and cleaned up setup and support files - nothing major
 * make install option added
 * added the power data file to the data_files too.
 * short description added
 * sample_data dir moved out of resources dir and resources dir removed.
 * data_files location updated
 * data_rate_file location updated and tests for the demo function added.
 * sample data files included in the install.
 * demo function added and set to use sample_data that is now included in the install.
 * ignore .cache folder
 * python setup.py test replaced with py.test -v
 * setup function given content. test function split in 2: 1 for data.shape and the other for len(data)
 * pycco webpages of pyops/*.py files created
 * excessive blank lines removed
 * logger comments changed to inline #-tagged comments so that they can be usefully extracted by pycco.
 * pycco function added
 * htmlcov folder ignored
 * first test created to check the shape of the returned data array
 * main function removed.
 * more linting errors fixed
 * linting errors corrected
 * my mistake newline at the end of file removed.
 * newline added at the end of the file
 * I recreated the pyops virtualenv as a clean env with no access to the system level packages. Also, I set up the tox testing env and adjusted the tox.ini accordingly. Finally, I updated the requirements.txt via pip-dump.
 * pycharm project created and commited
 * in-flow docstrings changed to logger message info messages and one to an error message.
 * python 2.5 test req. removed.
 * converted # comments to docstring... not sure yet if this is a good idea...
 * ipython notebook added to gitignore list ... for now. It's a scratch pad after all...
 * Installation section added.
 * updated via pip-dump - removed pyops line.
 * removed local modules from the requirments list.
 * requirements upated with versions.
 * removed pypi testing for now
 * docstring moved up
 * Title changed and floating cells cleaned up. Maybe I won't track this anymore...
 * readthedocs theme installed via pip and added here
 * docstring added explaining what this whole thing is about...
 * Update README.rst
 * Update README.rst
 * history updated by removing pypi reference; readme warning added; installation reference to pip etc. replaced with git cloning installation; imports included in __init__.py; resources directory and sampledata added.
 * hdings defined near start
 * removed default value for fname in function call
 * docs created and pyops.py updated with block read block from ipython notebook
 * initial commit