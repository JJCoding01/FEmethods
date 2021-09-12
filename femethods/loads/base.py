"""
Module to define different loads
"""


from ..core import Force


class Load(Force):
    """Base class for all load types

    Used primarily for type checking the loads on input
    """

    name = ""
