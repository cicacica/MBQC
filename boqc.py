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


from qres import GraphState, OpenGraph, nx
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
            :random_seed: int, the seed for random ordering, for reproducibility
        """
        idx, torder = 0, dict()
        for inset in self.ordering_class.values():
            random.seed(random_seed)
            ridx = random.permutation(range(idx,idx+len(inset)))
            for n,i in zip(inset, ridx):
                torder[n]=i
            idx += len(inset)

        self.set_total_order(torder)


    def set_io_type(self, input_type, output_type):
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

        self.I_type = input_type
        self.O_type = output_type



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
        for sset in self.ordering_class.values(): #this loop is ordered
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

    def neighbors(self, node_i) :
        """
        Return a set of open neighborhood of node i. In BOQC paper
        it is denoted as N_G(i).

        param
            :node:str|int, a node in G

        return
            set
        """
        return set(self.G.neighbors(node_i))

    def sortedtot_nodes(self):
        """
        Return a list of nodes ordered by it's total ordering

        return
            list(nodes)
        """
        try :
            snodes = sorted(self.G.nodes, key=lambda x:self.G.nodes[x]['total_order'])
        except KeyError :
            raise RuntimeError('You have not set a total ordering yet. Try method set_total_order_random()')

        return snodes


    def A_i(self, node_i):
        """
        Equation (14) from BOQC paper. It returns the new qubits assigned
        at a time step. This number varies depending on the ordering and
        input type

        param
            :node:str|int, a node in G

        return
            set
        """
        prev_nodes = list() #list is faster than set
        for node in self.sortedtot_nodes():
            if node == node_i :
                break
            prev_nodes += list(self.cneighbors(node))

        if self.I_type == 'quantum' :
            prev_nodes += list(self.I)

        return self.cneighbors(node_i).difference(prev_nodes)


    def Egt_iK(self, node_i, subK):
        """
        Equation (4), E^>_{iK}

        :node_i:node, the node in G
        :subK:set, subset K, where K is subset of node in G

            return
               list contains the edges
        """
        if not node_i in self.G.nodes :
            raise ValueError('node_i is not an element of nodes in G')
        if not isinstance(subK, set) :
            raise TypeError('subK must be set type')
        if not subK.issubset(set(self.G.nodes)):
            raise ValueError('subK must be a subset of nodes in G')

        sortedK = sorted(subK, key=lambda x: self.G.nodes[x]['total_order'])
        lti = [node_i]  #less than i
        for n in sortedK :
            if n == node_i :
                break
            lti += [n]

        res =  list(self.G.subgraph(lti).edges())
        return res


    def bound_physical_qubit(self, nsampling=1, random_seed=None):
        """
        Explicitely calculate a bound of physical qubits, given random sampling
        n_sampling times. The bound for input-output types are different.

        param
            :nsampling: int, number of sampling
            :random_seed: int, the random seed, for reproduciblility
        """
        bound = []
        for samp in range(nsampling):
            # sample from a random total ordering
            self.set_total_order_random(random_seed=random_seed)
            #"assigning" input state to input nodes
            qalive_i = [0]*len(self.G.nodes)
            qalive = 0 if self.I_type == 'classical' else len(self.I)
            for i,node in enumerate(self.sortedtot_nodes()):
                #"operating N_Ai"
                qalive += len(self.A_i(node))
                qalive_i[i] += qalive

                #"measuring i" if i is not in output nodes
                if node in self.O :
                    if self.O_type == 'quantum' :
                        pass
                else :
                    qalive -= 1
            bound += [max(qalive_i)]
        return max(bound)





    ## statements present in the BOQC paper

    def lemma2(self):
        """
        A(i) contains at least f(i), for all i in O^c.
        """
        subset = set(self.G.nodes).difference(self.O)
        for i in subset :
            if not self.f[i] in self.A_i(i):
                return 'FAIL'
        return 'PASS'


    def lemma3(self):
        """
        If you collect all elements of every A(i), for all i in O^c, you
        will obtain I^c.
        """
        ai = list()
        for i in set(self.G.nodes).difference(self.O):
            ai += list(self.A_i(i))

        if self.I_type == 'quantum':
            i_comp = set(self.G.nodes()).difference(self.I)
        else :
            i_comp = set(self.G.nodes())

        if len(i_comp) == len(ai):
            if len(set(ai).difference(i_comp)) == 0:
                return 'PASS'
        return 'FAIL'


    def lemma4(self):
        """
        Sum of all E^>_{iNg} for all i, results in all edges E
        """
        sum_eing = list()
        for i in self.G.nodes:
            sum_eing += self.Egt_iK(i, self.neighbors(i))

        if nx.is_isomorphic(self.G, nx.Graph(sum_eing)):
            return 'PASS'
        return 'FAIL'



