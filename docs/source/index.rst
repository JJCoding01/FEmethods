FEmethods documentation
=======================

FEmethods is a python package designed to analyse structural elements using
Finite Element Methods (FEM) to solve for element reaction forces and calculate
the deflection of the element.

Using FEM has the advantage over closed form
(exact) equations because it uses numerical techniques that can easily be used
on many different load cases, including statically indeterminate cases. The
disadvantage of FEM is that it will have less accuracy then the exact equations
derived for a particular case.

    .. note::
        This package is currently a work-in-progress.

.. toctree::
   :maxdepth: 2
   :caption: Table of Contents:

   intro
   femethods/core/core
   femethods/elements/elements
   femethods/loads/loads
   femethods/reactions/reactions

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
