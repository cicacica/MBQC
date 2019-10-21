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




class Lazy1WQC(GraphState):

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
        self.total_ordering = False
        self.I_type = 'quantum'
        self.O_type = 'quantum'


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


    def set_io_type(input_type, output_type):
        """ Set the input and output type. By default, input and output are
        quantum.

        param
            :input_type:str('quantum'|'classical') the input type: classical or quantum.
                        if classical, the state does not required to be prepared ahead.
            :output_type:str('quantum'|'classical') the input type: classical or quantum
                        if classical, all qubits in graph will be measured.
        """
        ioty = {'quantum', 'classical'}
        if input_type not in ioty:
            raise ValueError('input type must be quantum or classical')
        if output_type not in ioty:
            raise ValueError('output type must be quantum or classical')



    def set_total_order(self, total_ordering):
        """ Set attribute 'total_order' to every node in G.
        The total order must follows the partial ordering induced by flow.
        The total_order will be placed as attribute

        param
            :total_ordering: dict{node:total_order}, pair of node and it's total order
        """
        #sorted nodes based on total order
        rtorder = dict([(o,n) for n,o in total_ordering.items()])
        sorted_nodes = [rtorder[o] for o in sorted(rtorder.keys())]

        idx = 0
        for sset in self.partial_ordering.values(): #this loop is ordered
            #incomparable set
            inset = set(sorted_nodes[idx:idx+len(sset)])
            idx += len(sset)
            if inset != sset :
                raise ValueError('the total ordering is inconsistent with flow')

        for n, torder in total_ordering.items():
            self.G.add_node(n, total_order=torder)
        self.total_ordering = total_ordering


    def cneighbors(self, node_i) :
        """
        Return a set of closed neighborhood of node i. In BOQC paper
        it is denoted as N_G[i].

        param
            :node:str|int, a node in G

        return
            set
        """
        return set(self.G.neighbors(node_i)).union({node_i})


    def A_i(self, node_i):
        """
        Equation (14) from BOQC paper. It returns the new qubits assigned
        at a time step.

        param
            :node:str|int, a node in G

        return
            set
        """
        try :
            sorted_nodes = sorted(self.G.nodes, key=lambda x:self.G.nodes[x]['total_order'])
        except KeyError :
            raise RuntimeError('You have not set a total ordering yet. Try method set_total_order_random()')

        prev_nodes = list() #list is faster than set
        for node in sorted_nodes:
            if node == node_i :
                break
            prev_nodes += list(self.cneighbors(node))

        if self.I_type == 'quantum' :
            prev_nodes += list(self.I)

        return self.cneighbors(node_i).difference(prev_nodes)


    ## statements present in the BOQC paper

    def lemma2(self):
        """
        A(i) contains at least f(i), for all i in O^c.
        """
        subset = set(self.G.nodes).difference(set(self.O))
        for i in subset :
            if not self.f[i] in self.A_i(i):
                return 'FAIL'
        return 'PASS'







