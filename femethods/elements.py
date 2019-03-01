"""
Define a beam object that will have Loads and Reactions.
"""
import matplotlib.pyplot as plt
import numpy as np
from scipy.misc import derivative

# local imports
from ._base_elements import BeamElement


class Beam(BeamElement):
    """definition of a beam object"""

    def __init__(self, length, loads, reactions, E=1, Ixx=1):
        super().__init__(length, loads, reactions, E=E, Ixx=Ixx)

    def deflection(self, x):
        """calculate the deflection at the x location. Note that the x value
        given is the global x-value along the length of the beam.
        """

        # TODO: store the lengths/node locations in the class so they only have
        #  to be assessed without recalculating
        nodes = self.mesh.nodes
        L, d = None, None

        # Using the given global x-value, determine the local x-value, length
        # of active element, and the nodal displacements (vertical, angular)
        # vector d
        x_local = None
        for i in range(len(self.mesh.lengths)):
            if nodes[i] <= x <= nodes[i + 1]:
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

        M(x) = E * Ixx * d^2 v(x) / dx^2
        """
        return self.E * self.Ixx * derivative(self.deflection, x, dx=dx, n=2)

    def shear(self, x, dx=1):
        """calculate the shear force at a given x location as the third
        derivative of displacement with respect to x

        V(x) = E * Ixx * d^3 v(x) / dx^3
        """
        return self.E * self.Ixx * derivative(self.deflection, x, dx=dx, n=3,
                                              order=5)

    def bending_stress(self, x, dx=1, c=1):
        """returns the bending stress at global coordinate x"""
        return self.moment(x, dx=dx) * c / self.Ixx

    def plot(self, n=250, plot_stress=True, title='Beam Analysis'):
        """plot the deflection, moment, and shear along the length of the beam
        """
        rows = 4 if plot_stress else 3
        fig, axes = plt.subplots(rows, 1, sharex='all')

        # locations of nodes in global coordinate system
        locations = self.mesh.nodes

        # Get the global x values. Note that the x-values for the moment and
        # shear do not contain the endpoints of the x values for the deflection
        # curve. This is because differentiation technique used is the central
        # difference formula, which cannot calculate the value at the
        # endpoints
        xd = np.linspace(0, self.length, n)  # deflection
        xm = xd[1:-2]                        # moment (and stress)
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
        fig.suptitle(title)
        return fig

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
               f'LOADING\n'
               f'{L}\n'
               f'REACTIONS\n'
               f'{r}\n')
        return msg
