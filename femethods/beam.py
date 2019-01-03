"""
Define a beam object that will have Loads and Reactions.
"""
from scipy.misc import derivative
import matplotlib.pyplot as plt
import numpy as np

# local imports
from .elements import BeamElement
from .loads import PointLoad, MomentLoad
from .reactions import PinnedReaction, FixedReaction


class Beam(BeamElement):
    """definition of a beam object"""

    def __init__(self, length, loads, reactions, E=1, Ixx=1):
        super().__init__(length, loads, reactions, E=1, Ixx=1)
        self._node_deflections = None
        self._K = None  # global stiffness matrix

    @property
    def node_deflections(self):
        if self._node_deflections is None:
            self._node_deflections = self.__calc_node_deflections()
        return self._node_deflections

    def __get_boundary_conditions(self):

        # Initialize the  boundary conditions to None for each node, then
        # iterate over reactions and apply them to the boundary conditions
        # based on the reaction type.
        bc = [(None, None) for k in range(len(self.mesh.nodes))]
        for r in self.reactions:
            i = self.mesh.nodes.index(r.location)
            bc[i] = r.boundary
        return bc

    def __calc_node_deflections(self):
        """solve for vertical and angular displacement at each node"""

        # Get the boundary conditions from the reactions
        bc = self.__get_boundary_conditions()

        # Apply boundary conditions to global stiffness matrix. Note that the
        # boundary conditions are applied to a copy of the stiffness matrix to
        # avoid changing the property K, so it can still be used with further
        # calculations (ie, for calculating reaction values)
        kg = self.K.copy()
        kg = self.apply_boundary_conditions(kg, bc)

        # Use the same method of adding the input loads as the boundary
        # conditions. Start by initializing a numpy array to zero loads, then
        # iterate over the loads and add them to the appropriate index based on
        # the load type (force or moment)
        p = np.zeros((self.mesh.dof, 1))
        for ld in self.loads:
            i = self.mesh.nodes.index(ld.location)
            if isinstance(ld, PointLoad):
                p[i * 2][0] = ld.value  # input force
            elif isinstance(ld, MomentLoad):
                p[i * 2 + 1][0] = ld.value  # input moment

        # Solve the global system of equations {p} = [K]*{d} for {d}
        # save the deflection vector for the beam, so the analysis can be
        # reused without recalculating the stiffness matrix.
        # This vector should be cleared anytime any of the beam parameters
        # gets changed.
        self._node_deflections = np.linalg.solve(kg, p)
        return self._node_deflections

    def deflection(self, x):
        """calculate the deflection at the x location. Note that the x value
        given is the global x-value along the length of the beam.
        """

        # TODO: store the lengths/node locations in the class so they only have
        # to be assessed without recalculating
        nodes = self.mesh.nodes
        L, d = None, None

        # Using the given global x-value, determine the local x-value, length
        # of active element, and the nodal displacements (vertical, angular)
        # vector d
        for i in range(len(self.mesh.lengths)):
            if nodes[i] <= x and x <= nodes[i + 1]:
                # this is the element where the global x-value falls into.
                # Get the parameters in the local system and exit the loop
                x_local = x - nodes[i]
                # L = lengths[i]
                L = self.mesh.lengths[i]
                d = self.node_deflections[i * 2:i * 2 + 4]
                break

        if L is None or d is None:
            return
        return self.shape(x_local, L).dot(d)[0]

    def moment(self, x, dx=1):
        """calculate the moment in the beam at the global x value by taking
        the second derivative of the deflection curve.
        """
        return derivative(self.deflection, x, dx=dx, n=2)

    def shear(self, x, dx=1):
        """calculate the shear force at a given x location as the third
        derivative of displacement with respect to x
        """
        return derivative(self.deflection, x, dx=dx, n=3, order=5)

    def bending_stress(self, x, dx=1, c=1):
        """returns the bending stress at global coordinate x"""
        return self.moment(x, dx=dx) * c / self.Ixx

    def plot(self, n=250, plot_stress=True):
        """plot the deflection, moment, and shear along the length of the beam
        """
        rows = 4 if plot_stress else 3
        fig, axes = plt.subplots(rows, 1, sharex=True)

        # locations of nodes in global coordinate system
        locations = self.mesh.nodes

        # Get the global x values. Note that the x-values for the moment and
        # shear do not contain the endpoints of the x values for the deflection
        # curve. This is because differentiation technique used is the central
        # difference formula, which cannot calculate the value at the
        # endpoints
        xd = np.linspace(0, self.length, n)  # deflection
        xm = xd[1:-2]                        # moment (and stress if applicable)
        xv = xm[2:-3]                        # shear
        v = [self.deflection(xi) for xi in xd]                  # deflection
        m = [self.moment(xi, dx=self.length / n) for xi in xm]  # moment
        V = [self.shear(xi, dx=self.length / n) for xi in xv]   # shear

        # Set up plotting variables to be able to iterate over them more easily
        xs = [xv, xm, xd]
        y = [V, m, v]
        labels = ['shear', 'moment', 'deflection']
        if plot_stress:
            q = [self.bending_stress(xi, dx=self.length / n) for xi in xm]
            xs.append(xm)
            y.append(q)
            labels.append('stress')

        for ax, x, y, label in zip(axes, xs, y, labels):
            ax.plot(x, y)
            ax.fill_between(x, y, 0, color='b', alpha=0.25)
            ax.set_ylabel(label)
            ax.grid(True)

        axes[-1].set_xlabel('Beam position, x')
        axes[-1].set_xticks(locations)

        fig.subplots_adjust(hspace=.25)
        plt.show()

    def get_reaction_values(self):
        """Calculate the nodal forces acting on the beam. Note that the forces
        will also include the input forces.

        reactions are calculated by solving the matrix equation
        {r} = [K] * {d}

        where
           - {r} is the vector of forces acting on the beam
           - [K] is the global stiffness matrix (without boundary conditions applied)
           - {d} displacements of nodes
        """
        K = self.K                 # global stiffness matrix
        d = self.node_deflections  # force displacement vector
        r = np.matmul(K, d)

        for ri in self.reactions:
            i = self.mesh.nodes.index(ri.location)
            force, moment = r[i * 2: i * 2 + 2]

            # set the values in the reaction objects
            ri.force = force[0]
            ri.moment = moment[0]
        return r

    def __str__(self):
        L = ''
        for load in self.loads:
            L += 'Type: {}\n'.format(load.name)
            L += '    Location: {}\n'.format(load.location)
            L += '       Value: {}\n'.format(load.value)

        r = ''
        for reaction in self.reactions:
            r += 'Type: {}\n'.format(reaction.name)
            r += '    Location: {}\n'.format(reaction.location)
            r += '       Force: {}\n'.format(reaction.force)
            r += '      Moment: {}\n'.format(reaction.moment)

        msg = ('PARAMETERS\n'
               f'Length (length): {self.length}\n'
               f"Young's Modulus (E): {self.E}\n"
               f'Area moment of inertia (Ixx): {self.Ixx}\n'
                'LOADING\n'
               f'{L}\n'
               f'REACTIONS\n'
               f'{r}\n')
        return msg
