"""
Common constants and parameters to be used functional tests. This is done so that
the beams are all similar in size and loading.
"""

E = 29e6  # psi, Young's modulus
Ixx = 350  # in^4 area moment of inertia of beam
EI = E * Ixx  # common constant
TOL = 1e-1  # allowable tolerance between exact and numerical solutions to pass
