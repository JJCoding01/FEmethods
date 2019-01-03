# FEMethods

## Introduction
_FEMethods_ is a module that uses Finite Element Methods to determine the reactions, and plot the shear, moment, and deflection along the length of a beam.

Using Finite elements has the advantage over using exact solutions because it can be used as a general analysis, and can analyze beams that are statically indeterminate. The downside of this numerical approach is it will be less accurate than the exact approach.


## Installation


## General Layout

`FEMethods` is made up of several sub-classes to make it easy to define loads and reaction types.

### femethods.loads
There are currently only two different load types that are implemented.

 * `PointLoad`, a normal force acting with a constant magnitude on a single point
 * `MomentLoad`, a rotational force acting with a constant magnitude acting at a single point

All loads are defined by a `location` along the element, and a value (magnitude). The `location` must be positive or it will raise a `ValueError`

_Future goals are to add a library of standard distributed loads (constant, ramp, etc) as well as functionality that will allow a distributed load function to be the input._

#### femethods.loads.PointLoad
The `PointLoad` class describes a standard point load. A normal load acting at a single point with a constant value. It is defined with a location and a value (magnitude).

```python
>> PointLoad(5, -10)
PointLoad(location=5, value=-10)
```

The `location` must be a positive value, otherwise it will raise a `ValueError`.

#### femethods.loads.MomentLoad
A `MomentLoad` class describes a standard moment load. A moment acting at a single point with a constant value. It is defined with a location and a value.

```python
>> MomentLoad(2, 5)
MomentLoad(location=2, value=5)
```
The `location` must be a positive value, otherwise it will raise a `ValueError`.

### femethods.reactions

There are two different reactions that can be used to support an element.

  * `FixedReaction` does not allow vertical or rotational displacement
  * `PinnedReaction` does not allow vertical displacement but does allow rotational displacement

All reactions have two properties, a `force` and a `moment`. They represent the numerical value for the resistive force or moment acting on the element to support the load(s). These properties are set to `None` when the reaction is instantiated (ie, they are unknown). They are calculated and set when analyzing a element. Note that the `moment` property of a `PinnedReaction` will always be `None` because it does not resisit a moment.

The `value` property is a read-only combination of the `force` and `moment` properties, and is in the form `value = (force, moment)`

All reactions have an `invalidate` method that will set the `force` and `moment` back to `None`. This is useful when changing parameters and the calculated reactions are no longer valid.

#### femethods.reactions.FixedReaction
The `FixedReaction` is a reaction class that prevents both vertical and angular (rotational displacement). It has boundary conditions of `bc = (0, 0)`

```python
>> FixedReaction(3)
Fixed Reaction
  Location: 3
     Force: None
    Moment: None
```

The `location` must be a positive value, otherwise it will raise a `ValueError`.

#### femethods.reactions.PinnedReaction
The `PinnedReaction` is a reaction class that prevents vertical displacement, but allows angular (rotational) displacement. It has boundary conditions of `bc = (0, None)`

```python
>> PinnedReaction(7)
Pinned Reaction
  Location: 7
     Force: None
```

The `location` must be a positive value, otherwise it will raise a `ValueError`.

### femethods.beam
Defines a beam as a finite element. This class will handle the bulk of the analysis, populating properties (such as meshing and values for the reactions).

To create a `Beam` object, write the following:

```python
b = Beam(length, loads, reactions, E=1, Ixx=1)
```

Where the loads and reactions are a list of `loads` and `reactions` respectively.

**Note**
Loads and reactions must be a list, even when there is only one.

 The `E` and `Ixx` parameters are Young's modulus and the polar moment of inertia about the bending axis. They both default to `1`.

## Examples

This section contains several different examples of how to use the beam element, and their results.

For all examples, the following have been imported:

```python
from femethods.beam import Beam
from femethods.reactions import FixedReaction, PinnedReaction
from femethods.loads import PointLoad, MomentLoad

```

### Example: Cantilevered Beam with Fixed Support and End Loading

```python
beam_len = 10

reactions = [FixedReaction(0)]     # define reactions
loads = [PointLoad(beam_len, -2)]  # define loads

b = Beam(beam_len, loads, reactions, E=1, Ixx=1)
b.get_reaction_values()
print(b)
b.plot()
```
The output of the program is
```
PARAMETERS
Length (length): 10
Young's Modulus (E): 1
Area moment of inertia (Ixx): 1
LOADING
Type: point load
    Location: 10
       Value: -2
REACTIONS
Type: fixed
    Location: 0
       Force: 2.0
      Moment: 19.999999999999986
```

### Example: Cantilevered Beam with 3 Pinned Supports and End Loading

```python
beam_len = 10

reactions = [PinnedReaction(0), PinnedReaction(2), PinnedReaction(6)]     # define reactions
loads = [PointLoad(beam_len, -2)]  # define loads

b = Beam(beam_len, loads, reactions, E=1, Ixx=1)
b.get_reaction_values()
print(b)
b.plot()
```

```
PARAMETERS
Length (length): 10
Young's Modulus (E): 1
Area moment of inertia (Ixx): 1
LOADING
Type: point load
    Location: 10
       Value: -2

REACTIONS
Type: pinned
    Location: 0
       Force: 1.3333333333333321
      Moment: 0.0
Type: pinned
    Location: 2
       Force: -3.9999999999999973
      Moment: -8.881784197001252e-16
Type: pinned
    Location: 6
       Force: 4.666666666666664
      Moment: -3.552713678800501e-15
```


## TODO
 * Add a more thorough documentation for all the features, limitations and FE fundamentals for each section
 * Add additional element types, such as the bar element
 * Add a general `solve` function for elements that will define all unknowns (nodal displacements, reaction forces)

 ## Acknowledgements
[Derivation of stiffness matrix for a beam](https://www.12000.org/my_notes/stiffness_matrix/stiffness_matrix_report.htm#x1-50002.1.1)
