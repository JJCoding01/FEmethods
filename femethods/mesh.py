"""
Mesh module that will define the mesh.
"""

from typing import List, Sequence, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from femethods.reactions import Reaction
    from femethods.loads import Load


class Mesh(object):
    """define a mesh that will handle degrees-of-freedom (dof), element lengths
    etc.

    the input degree-of-freedom (dof) parameter is the degrees-of-freedom for
    a single element
    """

    def __init__(
            self, length: float, loads: List["Load"], reactions: List["Reaction"], dof: int
    ):
        self._nodes = self.__get_nodes(length, loads, reactions)
        self._lengths = self.__get_lengths()
        self._num_elements = len(self.lengths)
        self._dof = dof * self.num_elements + dof

    @property
    def nodes(self) -> Sequence[float]:
        return self._nodes

    @property
    def dof(self) -> int:
        """
        Degrees of freedom of the entire beam

        Returns:
            :obj:`int`: Read-only. Number of degrees of freedom of the beam
        """
        return self._dof

    @property
    def lengths(self) -> List[float]:
        """
        List of lengths of mesh elements

        Returns:
            :obj:`list`: Read-only. List of lengths of local mesh elements
        """
        return self._lengths

    @property
    def num_elements(self) -> int:
        """
        Number of mesh elements

        Returns:
            :obj:`int`: Read-only. Number of elements in mesh

        """

        return self._num_elements

    def __get_lengths(self) -> List[float]:
        # Calculate the lengths of each element
        lengths: List[float] = []
        for k in range(len(self.nodes) - 1):
            lengths.append(self.nodes[k + 1] - self.nodes[k])
        return lengths

    @staticmethod
    def __get_nodes(
            self, length: float, loads: List["Load"], reactions: List["Reaction"]
    ) -> Sequence[float]:
        nodes: List[float] = [0]  # ensure first node is always at zero (0)
        for item in loads + reactions:  # type: ignore
            nodes.append(item.location)
        nodes.append(length)  # ensure last node is at the end of the beam
        nodes = list(set(nodes))  # remove duplicates
        nodes.sort()
        return nodes

    def __str__(self) -> str:
        s = (
            "MESH PARAMETERS\n"
            f"Number of elements: {self.num_elements}\n"
            f"Node locations: {self.nodes}\n"
            f"Element Lengths: {self.lengths}\n"
            f"Total degrees of freedom: {self.dof}\n"
        )
        return s
