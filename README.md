pyFoamd
-------

Pythonic modification of OpenFOAM dictionaries and case files.

Installation
------------

.. code-block:: bash

    python -m pip install pyfoamd

Basic Usage
-----------

Copy a template case and load as a python object

.. code-block:: bash

    cp $FOAM_TUTORIALS/incompressible/simpleFoam/pitzDaily .
    cd pitzDaily
    pf init

View case variables

.. code-block:: bash

    pf edit

.. code-block:: python

    >>> case.constant.turbulenceProperties.RAS.RASModel
    kEpsilon

Change case dictionary entries

.. code-block:: python

    >>> case.constant.case.constant.turbulenceProperties.RAS.RASModel = kOmega

Write the updated case to file

.. code-block:: python

    >>> case.write()

Run the Allrun script

.. code-block:: python

    >>> case.run()

Releasing
---------

Releases are published automatically when a tag is pushed to GitHub.

.. code-block:: bash

   # Set next version number
   export RELEASE=x.x.x

   # Create tags
   git commit --allow-empty -m "Release $RELEASE"
   git tag -a $RELEASE -m "Version $RELEASE"

   # Push
   git push upstream --tags