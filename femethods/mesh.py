from typing import Optional

import numpy as np
import numpy.typing as npt

from . import validation


class Mesh:
    """
    Mesh to handle degrees-of-freedom (dof) and element lengths

    Parameters
    ----------
        length : float
            overall length of structure
        locations : sequence
            locations of nodes (loads and reactions)
        node_dof : int
            degrees-of-freedom for a single node
        max_element_length : float | None
            maximum allowed length of mesh element
        min_element_count : int | None
            minimum required number of elements

    .. versionchanged:: 0.1.8a1 renamed :obj:`dof` parameter to :obj:`node_dof`
    """

    def __init__(
        self,
        length: float,
        locations: npt.NDArray[np.float64],
        node_dof: int,
        *,
        max_element_length: Optional[float] = None,
        min_element_count: Optional[int] = None,
    ) -> None:
        self.length = length
        self.locations = locations
        self.node_dof = node_dof

        self.__lengths: npt.NDArray[np.float64] | None = (
            None  # this will be lazy calculated on-demand
        )

        self.max_element_length = max_element_length
        self.min_element_count = min_element_count

    @property
    def node_dof(self) -> int:
        """
        degrees of freedom for a single node

        Raises
        ------
            TypeError: when not a number
            ValueError: when not a positive integer
        """
        return self.__node_dof

    @node_dof.setter
    @validation.is_numeric
    @validation.positive
    def node_dof(self, value: int, /) -> None:
        if value != int(value):
            raise ValueError(f"node_dof must be an integer, not {value}")
        self.__node_dof = value

    @property
    def max_element_length(self) -> Optional[float]:
        """
        maximum allowed length of mesh element

        Returns
        -------
        float: maximum allowed length of mesh element
        """
        return self.__max_element_length

    @max_element_length.setter
    def max_element_length(self, value: Optional[float]) -> None:
        if value is None:
            self.__max_element_length = None
            return

        if not isinstance(value, (int, float)):
            raise TypeError(f"max_element_length must be a number, not {value}")
        if value <= 0:
            raise ValueError(
                f"max_element_length must be a positive number, not {value}"
            )
        self.__max_element_length = value

    @property
    def min_element_count(self) -> Optional[int]:
        """
        Minimum required number of elements.

        Returns
        -------
        int | None
            minimum required number of elements
        """
        return self.__min_element_count

    @min_element_count.setter
    def min_element_count(self, value: Optional[int]) -> None:
        if value is None:
            self.__min_element_count = None
            return

        if not isinstance(value, int):
            raise TypeError(f"min_element_count must be a number, not {value}")
        if value <= 0:
            raise ValueError(
                f"min_element_count must be a positive number, not {value}"
            )
        self.__min_element_count = value

    def __max_length_nodes(
        self, required_nodes: npt.NDArray[np.float64]
    ) -> npt.NDArray[np.float64]:
        """
        get node locations when the max length of an element is specified
        """

        if self.__max_element_length is None:  # pragma: no cover
            return required_nodes

        # there is a requirements on the max length of elements. Create a copy of the
        # nodes to be manipulated
        nodes = np.copy(required_nodes)

        # continually iterate over nodes until all elements have a length that is
        # less than the max allowed
        lengths = np.diff(nodes)
        while self.__max_element_length < np.max(lengths):
            # there is a node that is longer than allowed
            for node, length in zip(nodes[:-1], lengths):
                if not self.__max_element_length < length:
                    # current element is not longer than the allowed, no changes
                    # required
                    continue
                # current element is too long, split it in half
                nodes = np.append(nodes, node + length / 2)

            # all nodes that were longer than allowed, have been split in half.
            # recalculate node locations
            nodes = np.unique(nodes)
            nodes = np.sort(nodes)

            # update lengths variable, this is required for the exit condition of
            # the while loop that guarantees all elements end up shorter than the
            # maximum allowed length
            lengths = np.diff(nodes)
        return nodes

    def __min_count_nodes(
        self, required_nodes: npt.NDArray[np.float64]
    ) -> npt.NDArray[np.float64]:
        """get node locations when min number of elements are specified"""

        if self.__min_element_count is None:  # pragma: no cover
            return required_nodes

        # there is a requirements on the number of elements. Create a copy of the
        # nodes to be manipulated
        nodes = np.copy(required_nodes)

        # there is a limit on the minimum number of elements that must be used
        while self.__min_element_count > np.size(nodes) - 1:
            # there are not enough elements. Split the largest element in half
            lengths = np.diff(nodes)
            max_length = np.max(lengths)
            for node, length in zip(nodes[:-1], lengths):  # pragma: no branch
                if length == max_length:
                    nodes = np.append(nodes, node + length / 2)
                    nodes = np.unique(nodes)
                    nodes = np.sort(nodes)

                    # this condition focuses on the NUMBER of elements, not the
                    # length. Therefore, only break the first element that equals
                    # the longest. Even if multiple elements have the max length,
                    # only the first one is split
                    break
        return nodes

    @property
    def nodes(self) -> npt.NDArray[np.float64]:
        """location of nodes"""
        # create set of locations of each load and reaction, and the ends of the beam.
        # ensure first node is always at zero (0) (start of beam)
        nodes__ = np.array([0, self.length])
        nodes__ = np.append(nodes__, self.locations, axis=0)
        nodes__ = np.unique(nodes__)
        nodes__ = np.sort(nodes__)

        if self.__max_element_length is not None:
            # there is a maximum limit on the length of the elements.
            nodes__ = self.__max_length_nodes(required_nodes=nodes__)
        if self.__min_element_count is not None:
            # there is a limit on the minimum number of elements that must be used
            nodes__ = self.__min_count_nodes(required_nodes=nodes__)

        return nodes__

    @property
    def dof(self) -> int:
        """
        Degrees of freedom of the entire beam

        Returns
        -------
        int
            Read-only. Number of degrees of freedom of the beam
        """
        return self.node_dof * len(self.nodes)

    @property
    def lengths(self) -> npt.NDArray[np.float64]:
        """
        List of lengths of mesh elements

        Returns
        -------
        array_like
            Read-only. List of lengths of local mesh elements
        """
        if self.__lengths is not None:  # pragma: no cover
            return self.__lengths

        # the lengths have not been calculated yet. Calculate the lengths of each
        # element
        self.__lengths = np.diff(self.nodes)
        return self.__lengths

    def __str__(self) -> str:
        mesh_string = (
            "MESH PARAMETERS\n"
            f"Number of elements: {len(self.lengths)}\n"
            f"Node locations: {self.nodes}\n"
            f"Element Lengths: {self.lengths}\n"
            f"Total degrees of freedom: {self.dof}\n"
        )
        return mesh_string
