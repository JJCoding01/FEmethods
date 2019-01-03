"""
Module to define a general mesh element to be used for any FEM element, and
the base element class that all FEM elements will be derived from
"""

import numpy as np
import matplotlib.pyplot as plt


class Decorator(object):
    """Decorator class used to validate parameters"""
    @staticmethod
    def positive(param_name='parameter'):
        """Function decorator to handle validating input parameters to ensure
        parameters are positive values.

        The input, param_name, is the parameter name that will show up in the
        call-stack when an invalid parameter is entered.
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                if args[1] <= 0:
                    raise ValueError(param_name + ' must be positive!')
                func(*args, **kwargs)
            return wrapper
        return decorator


class Mesh(object):
    """define a mesh that will handle degrees-of-freedom (dof), element lengths
    etc."""

    def __init__(self, length, loads, reactions, dof):
        self._nodes = self.__get_nodes(length, loads, reactions)
        self._lengths = self.__get_lengths()
        self._num_elements = len(self.lengths)
        self._dof = dof * self.num_elements + dof

    @property
    def nodes(self):
        return self._nodes

    @property
    def dof(self):
        return self._dof

    @property
    def lengths(self):
        return self._lengths

    @property
    def num_elements(self):
        return self._num_elements

    @num_elements.setter
    @Decorator.positive('number of elements')
    def num_elemnts(self, n):
        self._num_elements = n

    def __get_lengths(self):
        # Calculate the lengths of each element
        lengths = []
        for k in range(len(self.nodes) - 1):
            lengths.append(self.nodes[k + 1] - self.nodes[k])
        return lengths

    def __get_nodes(self, length, loads, reactions):
        nodes = [0]  # ensure first node is always at zero (0)
        for param in loads + reactions:
            nodes.append(param.location)
        nodes.append(length)  # ensure last node is at the end of the beam
        nodes = list(set(nodes))   # remove duplicates
        nodes.sort()
        return nodes

    def __str__(self):
        s = ('MESH PARAMETERS\n'
            f'Number of elements: {self.num_elements}\n'
            f'Node locations: {self.nodes}\n'
            f'Element Lengths: {self.lengths}\n'
            f'Total degrees of freedom: {self.dof}\n')
        return s


class Base(object):
    """base object to be used as base for both FEM analysis"""

    def __init__(self, length, E=1, Ixx=1):
        self.length = length
        self.E = E      # Young's modulus
        self.Ixx = Ixx  # area moment of inertia

    @property
    def length(self):
        return self._length

    @length.setter
    @Decorator.positive('length')
    def length(self, length):
        self._length = length

    @property
    def E(self):
        return self._E

    @E.setter
    @Decorator.positive("Young's modulus")
    def E(self, E):
        self._E = E

    @property
    def Ixx(self):
        return self._Ixx

    @Ixx.setter
    @Decorator.positive('Area moment of inertia')
    def Ixx(self, Ixx):
        self._Ixx = Ixx


class Element(Base):
    """General element that will be inherited from for specific elements"""

    def __init__(self, length, E=1, Ixx=1):
        super().__init__(length, E, Ixx)

    @property
    def K(self):
        """global stiffness matrix"""
        if self._K is None:
            self._K = self.stiffness_global()
        return self._K

    def stiffness(self):
        """return local stiffness matrix, k, as numpy array evaluated with beam
        element length L, where L defaults to the length of the beam
        """
        raise NotImplemented('Method must be overloaded!')

    def stiffness_global(self):
        # Initialize the global stiffness matrix, then iterate over the
        # elements, calculate a local stiffness matrix, and add it to the
        # global stiffness matrix.
        raise NotImplemented('Method must be overloaded!')

    def apply_boundary_conditions(self, k, bcs):
        """
        Given the stiffness matrix 'k', and the boundary conditions as a list
        of tuples, apply the boundary conditions to the stiffness matrix by
        setting the rows and columns that correspond to the boundary conditions
        to zeros, with ones on the diagonal.

        The boundary conditions (bcs) are in the form
        bcs = [(displacement1, rotation1), (displacement2, rotation2)]

        For the boundary condition, if the conditional evaulates to None, then
        movement is allowed, otherwise no displacement is allowed.

        The boundary condition coordinates must match the stiffness matrix.
        That is, if the stiffness matrix is a local matrix, the boundary
        conditions must also be local.

        returns the adjusted  stiffness matrix after the boundary
        conditions are applied
        """

        def apply(k, i):
            """sub function to apply the boundary condition at row/col i to
            stiffness matrix k

            return the stiffness matrix k with boundary conditions applied
            """
            k[i] = 0     # set entire row to zeros
            k[:, i] = 0  # set entire column to zeros
            k[i][i] = 1  # set diagonal to 1
            return k

        # TODO: Check the sizes of the boundary conditions and stiffness matrix

        node = 0
        for bc in bcs:
            v, q = bc
            if v is not None:
                k = apply(k, node * 2)
            if q is not None:
                k = apply(k, node * 2 + 1)
            node += 1
        return k


class BeamElement(Element):
    """base beam element"""

    def __init__(self, length, loads, reactions, E=1, Ixx=1):
        super().__init__(length, E, Ixx)
        self.loads = loads
        self.reactions = reactions
        self.mesh = Mesh(length, loads, reactions, 2)

    def shape(self, x, L=None):
        """return an array of the shape functions evaluated at x the local
        x-value
        """
        if L is None:
            L = self.length
        N1 = 1 / L**3 * (L**3 - 3 * L * x**2 + 2 * x**3)
        N2 = 1 / L**2 * (L**2 * x - 2 * L * x**2 + x**3)
        N3 = 1 / L**3 * (3 * L * x**2 - 2 * x**3)
        N4 = 1 / L**2 * (-L * x**2 + x**3)
        return np.array([N1, N2, N3, N4])

    def plot_shapes(self, n=25):
        """plot shape functions for the with n data points"""
        x = np.linspace(0, self.length, n)

        # set up list of axes with a grid where the two figures in each column
        # share an x axis
        axes = []
        fig = plt.figure()
        axes.append(fig.add_subplot(221))
        axes.append(fig.add_subplot(222))
        axes.append(fig.add_subplot(223, sharex=axes[0]))
        axes.append(fig.add_subplot(224, sharex=axes[1]))

        N = [[], [], [], []]
        for xi in x:
            n = self.shape(xi)
            for i in range(4):
                N[i].append(n[i])

        for k in range(4):
            ax = axes[k]
            ax.grid(True)
            ax.plot(x, N[k], label=f'$N_{k+1}$')
            ax.legend()

        fig.subplots_adjust(wspace=0.25, hspace=0)
        plt.show()

    def stiffness(self, L=None):
        """return local stiffness matrix, k, as numpy array evaluated with beam
        element length L, where L defaults to the length of the beam"""

        if L is None:
            L = self.length

        E = self.E
        Ixx = self.Ixx

        k = np.array([[12,       6 * L,       -12,        6 * L   ],
                      [6 * L,    4 * L**2,     -6 * L,    2 * L**2],
                      [-12,     -6 * L,        12,       -6 * L   ],
                      [6 * L,    2 * L**2,     -6 * L,    4 * L**2]])
        return E * Ixx / L**3 * k

    def stiffness_global(self):
        # Initialize the global stiffness matrix, then iterate over the
        # elements, calculate a local stiffness matrix, and add it to the
        # global stiffness matrix.
        kg = np.zeros((self.mesh.dof, self.mesh.dof))
        for e in range(self.mesh.num_elements):
            # iterate over all the elements and add the local stiffness matrix
            # to the global stiffness matrix at the proper index
            k = self.stiffness(self.mesh.lengths[e])  # local stiffness matrix
            i1, i2 = (e * 2, e * 2 + 4)               # global slicing index
            kg[i1:i2, i1:i2] = kg[i1:i2, i1:i2] + k   # current element
        self._K = kg

        return self._K
