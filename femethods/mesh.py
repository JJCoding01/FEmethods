import numpy as np

from . import validation


class Mesh:
    """
    Mesh to handle degrees-of-freedom (dof) and element lengths

    Parameters:
        length: float: overall length of structure
        locations: sequence: sequence of locations of nodes (loads and reactions)
        node_dof: int: degrees-of-freedom for a single node

    .. versionchanged:: 0.1.8a1 renamed :obj:`dof` parameter to :obj:`node_dof`
    """

    def __init__(
        self,
        length,
        locations,
        node_dof,
    ):
        self.length = length
        self.locations = locations
        self.node_dof = node_dof

        self.__lengths = None  # this will be lazy calculated on-demand

    @property
    def node_dof(self):
        """
        degrees of freedom for a single node

        Raises:
            TypeError: when not a number
            ValueError: when not a positive integer
        """
        return self.__node_dof

    @node_dof.setter
    @validation.is_numeric
    @validation.positive
    def node_dof(self, value):
        if value != int(value):
            raise ValueError(f"node_dof must be an integer, not {value}")
        self.__node_dof = value

    @property
    def nodes(self):
        """location of nodes"""
        # create set of locations of each load and reaction, and the ends of the beam.
        # ensure first node is always at zero (0) (start of beam)
        nodes__ = np.array([0, self.length])
        nodes__ = np.append(nodes__, self.locations, axis=0)
        nodes__ = np.unique(nodes__)
        nodes__ = np.sort(nodes__)

        nodes__.add(self.length)  # ensure last node is at the end of the beam
        return sorted(nodes__)

    @property
    def dof(self):
        """
        Degrees of freedom of the entire beam

        Returns:
            :obj:`int`: Read-only. Number of degrees of freedom of the beam
        """
        return self.node_dof * len(self.nodes)

    @property
    def lengths(self):
        """
        List of lengths of mesh elements

        Returns:
            :obj:`list`: Read-only. List of lengths of local mesh elements
        """
        if self.__lengths is not None:  # pragma: no cover
            return self.__lengths

        # the lengths have not been calculated yet. Calculate the lengths of each
        # element
        self.__lengths = np.diff(self.nodes)
        return self.__lengths

    def __str__(self):
        mesh_string = (
            "MESH PARAMETERS\n"
            f"Number of elements: {len(self.lengths)}\n"
            f"Node locations: {self.nodes}\n"
            f"Element Lengths: {self.lengths}\n"
            f"Total degrees of freedom: {self.dof}\n"
        )
        return mesh_string
