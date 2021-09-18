"""
Mesh module that will define the mesh.
"""


class Mesh:
    """
    Mesh to handle degrees-of-freedom (dof) and element lengths

    Parameters:
        length: float: overall length of beam
        loads: list: loads
        reactions: list: reactions
        element_dof: int: degrees-of-freedom for a single element


    .. versionchanged:: 0.1.8a1 renamed :obj:`dof` parameter to :obj:`element_dof`
    """

    def __init__(
        self,
        length,
        loads,
        reactions,
        element_dof,
    ):
        self._dof = dof * self.num_elements + dof
        self.__nodes = self.__get_nodes(length, loads, reactions)
        self.__lengths = self.__get_lengths()
        self.__num_elements = len(self.lengths)
        self.element_dof = element_dof

    @property
    def element_dof(self):
        """degrees of freedom for a single element"""
        return self.__element_dof

    @element_dof.setter
    def element_dof(self, value):

        if value != int(value):
            raise ValueError(f"element_dof must be an integer, not {value}")

        if value <= 0:
            raise ValueError(
                f"degrees of freedom must be a positive integer, not {value}"
            )

        self.__element_dof = value

    @property
    def nodes(self):
        """location of nodes relative to base"""
        return self.__nodes

    @property
    def dof(self):
        """
        Degrees of freedom of the entire beam

        Returns:
            :obj:`int`: Read-only. Number of degrees of freedom of the beam
        """
        return self._dof

    @property
    def lengths(self):
        """
        List of lengths of mesh elements

        Returns:
            :obj:`list`: Read-only. List of lengths of local mesh elements
        """
        return self.__lengths

    @property
    def num_elements(self):
        """
        Number of mesh elements

        Returns:
            :obj:`int`: Read-only. Number of elements in mesh

        """

        return self.__num_elements

    def __get_lengths(self):
        # Calculate the lengths of each element
        lengths = []
        for k in range(len(self.nodes) - 1):
            lengths.append(self.nodes[k + 1] - self.nodes[k])
        return lengths

    @staticmethod
    def __get_nodes(length, loads, reactions):
        # create set of locations of each load and reaction, and the ends of the beam.
        # ensure first node is always at zero (0) (start of beam)
        nodes = {0}
        for item in loads + reactions:
            nodes.add(item.location)

        nodes.add(length)  # ensure last node is at the end of the beam
        return sorted(nodes)

    def __str__(self):
        mesh_string = (
            "MESH PARAMETERS\n"
            f"Number of elements: {self.num_elements}\n"
            f"Node locations: {self.nodes}\n"
            f"Element Lengths: {self.lengths}\n"
            f"Total degrees of freedom: {self.dof}\n"
        )
        return mesh_string
