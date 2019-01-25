"""
Module to define different reaction types
"""

from ._common import Forces


class Reaction(Forces):
    """Base class for all reactions"""

    name = None

    def __init__(self, location, label=None):
        super().__init__(location, label)
        self._force = None
        self._moment = None

    @property
    def force(self):
        return self._force

    @force.setter
    def force(self, f):
        self._force = f

    @property
    def moment(self):
        return self._moment

    @moment.setter
    def moment(self, m):
        self._moment = m

    @property
    def value(self):
        return (self.force, self.moment)

    def invalidate(self):
        """Invalidate the reaction values. To be used whenever the parameters cha Ie, for when inputs change and the
        reaction values are no longer valid
        """
        self.force, self.moment = (None, None)


class PinnedReaction(Reaction):

    name = 'pinned'

    def __init__(self, location, label=None):
        super().__init__(location, label)
        # limit the vertical displacemnt but allow rotation
        self.boundary = (0, None)

    def __str__(self):
        return (f'Pinned Reaction\n'
                f'  Location: {self.location}\n'
                f'     Force: {self.force}\n')

    def __repr__(self):
        return f'PinnedReaction(location={self.location}, label={self.label})'


class FixedReaction(Reaction):

    name = 'fixed'

    def __init__(self, location, label=None):
        super().__init__(location, label)
        # do not allow vertical or rotational displacement
        self.boundary = (0, 0)

    def __str__(self):
        return (f'Fixed Reaction\n'
                f'  Location: {self.location}\n'
                f'     Force: {self.force}\n'
                f'    Moment: {self.moment}\n')