#!/usr/bin/env python3

__doc__="""
Self defined exceptions
"""


# self-defined exceptions
class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class FlowError(Error):
    """Exception raised for errors in the graph

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message

