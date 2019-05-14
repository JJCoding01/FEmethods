Introduction
============

This is the introduction to FEmethods. It will introduce Finite Element Methods
in general, and then give a few examples of how to use FEmethods.

Installation
------------

FEmethods is hosted on PyPi, so installation is straightforward.
    .. code-block:: python

        >>>pip install femethods

Then to test that the installation worked properly, you can try this simple
example case of a simply supported beam with a single, centered point load.

    .. code-block:: python

        >>>from femethods.elements import Beam
        >>>from femethods.reactions import PinnedReaction
        >>>from femethods.loads import PointLoad

        >>>b = Beam(30, loads=[PointLoad(-100, 15)], reactions=[PinnedReaction(x) for x in [0, 30]])

        >>>b.solve()
        >>>print(b)

        PARAMETERS
        Length (length): 30
        Young's Modulus (E): 1
        Area moment of inertia (Ixx): 1
        LOADING
        Type: point load
            Location: 15
           Magnitude: -100
        REACTIONS
        Type: pinned
            Location: 0
               Force: 50.0
              Moment: 0.0
        Type: pinned
            Location: 30
               Force: 50.0
              Moment: 0.0

Platform
--------

FEmethods has only been tested on Windows 10, with python 3.7. Further testing
with some linux distros is planned.


Finite Element Methods
----------------------

Include a brief intro to general finite element methods. Generally, how it works
what are some advantages and disadvantages, etc.
