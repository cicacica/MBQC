 #!/usr/bin/env python3

__doc__="""boqc --- blind oracular quantum computation.

methods: user choise

lazy1WQC :  lazy_lemmas(OpenGraph, 2|3|4) , see  boqc paper
            inherited from OpenGraph

boqc :

bqc :

"""

__author__ = "Cica Gustiani"
__license__ = "Apache2"
__version__ = "1.0.0"
__maintainer__ = "Cica Gustiani"
__email__ = "cicagustiani@gmail.com"


from qres import GraphState, OpenGraph
from numpy import random




class lazy1WQC(GraphState):

    def __init__(self, G, I, O, phi):
        """ Instantiation of lazy1WQC object. This class corresponds to
        Algorithm 1 in BOQC paper.  It is a child of GraphState, which is also a
        grandchild of OpenGraph.

        param
           :G: networkx.graph, an open simple graph
           :I: set, a set input nodes
           :O: set, a set of output nodes
           :phi: dict{node: float}, dict contains node and it's measurement angles
        """
        if not isinstance(phi,dict):
            raise TypeError('phi must be dict type')

        super().__init__(G, I, O)
        self.phi = phi


    def set_total_order_random(self, random_seed=None):
        """ Generate a random total ordering that follows flow, then s
            set attribute 'total_order' to every node in G.
            Total ordering goes from 0 to len(V)-1

        param
            :random_seed: int, the seed for random ordering
        """
        random.seed(random_seed)
        idx, torder = 0, dict()
        for inset in self.partial_ordering.values():
            ridx = random.permutation(range(idx,idx+len(inset)))
            for n,i in zip(inset, ridx):
                torder[n]=i
            idx += len(inset)

        self.set_total_order(torder)



    def set_total_order(self, total_order):
        """ Set attribute 'total_order' to every node in G.
        The total order must follows the partial ordering induced by flow.

        param
            :total_order: dict{node:total_order}, pair of node and it's total order
        """
        #sorted nodes based on total order
        rtorder = dict([(o,n) for n,o in total_order.items()])
        sorted_nodes = [rtorder[o] for o in sorted(rtorder.keys())]

        idx = 0
        for sset in self.partial_ordering.values(): #this loop is ordered
            #incomparable set
            inset = set(sorted_nodes[idx:idx+len(sset)])
            idx += len(sset)
            if inset != sset :
                raise ValueError('the total ordering is inconsistent with flow')

        for n, torder in total_order.items():
            self.G.add_node(n, total_order=torder)


    def cneighbors(self, node) :
        """
        Return a set of closed neighborhood of node

        param
            :node:str|int, a node in G

        return
            set
        """
        return set(self.G.neighbors(node)).union(node)


    def A(self, node):
        """
        Equation (14) from BOQC paper. It returns the new qubits assigned
        at a time step.

        param
            :node:str|int, a node in G

        return
            set
        """
        return




