"""module with exact equations for different load cases

https://www.awc.org/pdf/codes-standards/publications/design-aids/AWC-DA6-BeamFormulas-0710.pdf

"""

import numpy as np
import matplotlib.pyplot as plt

from .elements import Base

from .reactions import PinnedReaction, FixedReaction
from .loads import PointLoad, MomentLoad


class ExactBase(Base):

    def __init__(self, L, E=1, Ixx=1):
        super().__init__(L, E, Ixx)
        self.EI = E * Ixx

    def deflection(self, x):
        raise NotImplemented('method must be overloaded!')
        # pass

    def plot(self, n=25):
        x = np.linspace(0, self.length, n)
        d = [self.deflection(xi) for xi in x]

        plt.plot(x, d)
        plt.show()


class SimpleSupportPointLoad(ExactBase):
    """Beam, simply supported at both ends, with a point load at any point
    between them.

    Case 8 from reference
    """

    def __init__(self, L, load, E=1, Ixx=1):
        super().__init__(L, E, Ixx)
        self.load = load
        self.reactions = [PinnedReaction(0), PinnedReaction(L)]

    def deflection(self, x):
        P = self.load.value
        L = self.length
        a = self.load.location
        b = L - a
        EI = self.EI
        if x < a:
            return P * b * x / (6 * EI * L) * (L**2 - b**2 - x**2)
        elif x > a:
            return P * a * (L - x) / (6 * EI * L) * (2 * L * x - x**2 - a**2)
        else:
            return P * a**2 * b**2 / (3 * EI * L)


def main():
    load = PointLoad(location=7, value=-1)
    b = SimpleSupportPointLoad(10, load)
    b.plot(700)


if __name__ == '__main__':
    main()
