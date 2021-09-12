"""
Module to define different loads
"""


from ..core import Forces


class Load(Forces):
    """Base class for all load types

    Used primarily for type checking the loads on input
    """

    name = ""
