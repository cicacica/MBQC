 #!/usr/bin/env python3

__doc__="""
        class GraphState. Graph state object as a resource of 1WQC
        computations. Only server that has access to this.

    All notations used here are adapted from Blind Oracular Quantum Computation
    paper (unpublished).
"""

__author__ = "Cica Gustiani"
__license__ = "Apache2"
__version__ = "1.0.0"
__maintainer__ = "Cica Gustiani"
__email__ = "cicagustiani@gmail.com"


#standard libraries

#non-standard libraries
from mbqc.qres import OpenGraph


class GraphState(OpenGraph):
    """
    Create a graph state as a quantum resouce for 1WQC computation. Only
    parties with quantum computer has access to this; that guy is Bob.
    """
    def __init__(self, G, I, O):
        """ Instantiation of the OpenGraph object. That is the resource of
        1WQC computations. Only works with a class of graphs that have flow.
        Everything here is classical. It is the parent of all classess here.

        param
            :G: networkx.graph, an open simple graph
            :I: set, a set input nodes
            :O: set, a set of output nodes

        Methods related to graph state in QUANTUM sense
        """
        super().__init__(G, I, O)
        self.qreg = False


    def init_nodes_plus(self, nqubit):
        """
        Initialize the qubit which corresponding to node in graph with
        state |0>^nqubit

        :nqubit: int, the number of qubits to be assigned
        """
        pass

    def init_nodes_zero(self, nqubit):
        """
        Initialize the qubit which corresponding to node in graph with
        state |0>^nqubit

        :nqubit: int, the number of qubits to be assigned
        """
        pass

    def apply_entangling_to(self, node_set):
        """
        Apply an entangling operations on the corresponding edges
        in a set of qubits node_set
        """
        pass

    def set_quantum_input(self, rho_in):
        """
        assign quantum state to input nodes
        """
        pass

