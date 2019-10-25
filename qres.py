 #!/usr/bin/env python3

__doc__=""" qres --- quantum resource --- contains:
    1) class OpenGraph. The graph that is used for GraphState, in hypothetical sense.
       The clients and the server have access to this information.
    2) class GraphState. Graph state object as a resource of 1WQC
        computations. Only server that has access to this.
    3) class Server. The child class inherited from GraphState
    4) class Client. The client with small quantum power, depending on the input/output type.

    All notations used here are adapted from Blind Oracular Quantum Computation
    paper (unpublished).
"""

__author__ = "Cica Gustiani"
__license__ = "Apache2"
__version__ = "1.0.0"
__maintainer__ = "Cica Gustiani"
__email__ = "cicagustiani@gmail.com"


#standard libraries
import networkx as nx
import pygraphviz as pgv
import random
from multiprocessing import Pool
from itertools import product




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



class OpenGraph:
    """
    Create an open-graph as a hypothetical resouce for 1WQC computation.
    """
    def __init__(self, G, I, O):
        """ Instantiation of the OpenGraph object. That is the resource of
        1WQC computations. Only works with a class of graphs that have flow.
        Everything here is classical. It is the parent of all classess here.
        All methods here are related to graph, in GRAPH-THEORY sense.

        param
            :G: networkx.graph, an open simple graph
            :I: set, a set input nodes
            :O: set, a set of output nodes
        """
        #input checking
        if not isinstance(G, nx.classes.graph.Graph):
            raise TypeError('provide a simple graph, a networkx.Graph object')

        if not isinstance(I,set):
            raise TypeError('I must be a set()')
            if not I.issubset(set(G.nodes())) or len(I)==0:
                raise ValueError('I must be a nonempty subset of nodes in G')

        if not isinstance(O,set):
            raise TypeError('O must be a set()')
            if not O.issubset(set(G.nodes())) or len(O)==0:
                raise ValueError('O must be a subset of nodes in G')

        #initializations
        self.G = G
        self.I = I
        self.O = O
        self.ordering_class = False
        self.f = False
        self._set_nodetypes_()
        self._set_flow_()

    def __copy__(self):
        return OpenGraph(self.G, self.I, self.O)

    def _set_nodetypes_(self):
        """
        Set attirubute ntypes for every node: {input, output, aux(iliary)}
        """
        types = dict([(n, list()) for n in self.G.nodes])
        for i in self.I :
            types[i] +=  ['input']

        for i in self.O :
            types[i] +=  ['output']

        for i in set(self.G.nodes)-self.I-self.O:
            types[i] +=  ['aux']

        #assign it to the nodes
        for node in self.G.nodes:
            self.G.add_node(node, ntypes = set(types[node]))


    def _set_flow_(self):
        """
        set flow by adding flow attribute to every node and
        set attribute partial_ordering to the graph
        """
        f_exist, f, poset, flow_criteria = self.flow(self.G, self.I, self.O)

        if not f_exist :
            raise FlowError('graph does not have a flow. Sorry, find another Graph')
        if f_exist and not flow_criteria :
            raise ValueError('inconsistent result: DANGEROUS! A THEORY BUG')

        for dom, cod in f.items():
            self.G.add_node(dom, flow=cod)

        self.ordering_class = poset
        self.f = f



## aesthetic-related methods

    def draw_graph(self, outfile='out.png', **options):
        """
        Draw graph with some options

        output : out.png file
        options : { flow : True,
                    total_order : False,
                    partial_order : False
                  }
        """
        opt = {'flow': True, 'total_order': False, 'partial_order': False}
        for k,v in opt.items():
            if k in options :
                opt[k] = options[k]

        directed, undirected = list(), list(self.G.edges)
        if opt['flow']:
            for dom, cod  in self.f.items():
                try:
                    idx = undirected.index((dom, cod))
                except ValueError:
                    idx = undirected.index((cod, dom))
                directed += [(dom,cod)]
                undirected[idx] = False

            undirected = [edge for edge in undirected if edge]
        else :
            undirected = self.G.edges #list

        ## creating a dot string

        # nodes part
        snodes = list()
        shape = {'input': 'shape=diamond', 'output': 'shape=circle', 'aux':'shape=circle'}
        style = {'input': '', 'output':'style=filled fillcolor=gray', 'aux':''}
        for n, attr in self.G.nodes.items() :
            natt = ' '.join([shape[t] for t in attr['ntypes']])
            natt += ' '+' '.join([style[t] for t in attr['ntypes']])
            snodes+= ['%s [%s];'%(str(n),natt)  ]

        # edges part
        sedges = list()
        for a,b in undirected :
            sedges += ['%s->%s [arrowhead=none];'%(str(a),str(b))]
        if opt['flow'] :
            for a,b in directed :
                sedges += ['%s->%s;'%(str(a),str(b))]

        #combine the strings
        sdot = 'digraph{'+''.join(snodes)+'rankdir=LR;'+''.join(sedges)+\
               '{rank=same;'+ ';'.join(str(i) for i in self.I)+';}'+\
               '{rank=same;'+ ';'.join(str(i) for i in self.O - self.I)+';}'+\
               '}'
        graphv = pgv.AGraph(sdot)
        graphv.layout(prog='dot')
        graphv.draw(outfile)



## random graph generation-related method

    @classmethod
    def random_open_graph(cls, n_I, n_O, n_aux, f_trial=10):
        """
        Return a random open graph. Iterates the graph, by
        adding one-by one the node as many as n_aux, then add
        the edges randomly.

        param
            :n_I:int, number of input nodes
            :n_O:int, number of output nodes
        """
        I_nodes = set(['i%i'%x for x in range(n_I)])
        O_nodes = set(['o%i'%x for x in range(n_O)])

        #initialize graph, try fully connected I-O
        G = nx.Graph()
        G.add_edges_from(product(I_nodes, O_nodes))

        flow_exist, f, vs, sanity = cls.flow(G,I_nodes,O_nodes)
        if not flow_exist :
            fulledges_pset = cls.get_power_set(G.edges)

            # remove emptyset and the set
            poss_edges = [ss for ss in fulledges_pset]
            poss_edges.remove(set())
            poss_edges.remove(set(G.edges))

            #initial graphs with flow
            P=Pool(4)
            p_args = [(G.copy(),I_nodes,O_nodes, edges, idx) for idx,edges in enumerate(fulledges_pset)]
            res = P.starmap(cls._remove_edges_forflow, p_args)


    @classmethod
    def _remove_edges_forflow(cls, G, I, O, redges, idx):
        """
        Try to obtain a graph with flow by removing edges of graph G

        :G: nx.Graph(), the graph
        :I: iter, the list of input nodes
        :O: iter, the list of output nodes
        :redges: list(tuple), pair of nodes at the end of edge to be removed
        """
        G.remove_edges_from(redges)
        flow_exist, f, vs, sanity = cls.flow(G,I,O)
        if flow_exist :
            og = OpenGraph(G, I, O)
            og.draw_graph('out%s.png'%str(idx))

        return G if flow_exist else False



    @staticmethod
    def get_power_set(s):
        """
        Return the power set of set s, sorted by the size of subset

        :s: iterable
        """
        power_set = [set()]
        for element in s:
            new_sets = []
            for subss in power_set:
                new_sets.append(subss | {element})
            power_set.extend(new_sets)

        return sorted(power_set, key=lambda x: len(x))





    @classmethod
    def _candidate_subgraph_(cls, G, new_node, past_node, I_nodes, ordering, f):
        """
        Iteration to get a graph with flow
        """
        G2, g = G.copy(), f.copy()
        newnode, nattr = new_node[0], new_node[1]
        G2.add_node(newnode,**nattr)
        G2.add_edge(past_node, newnode)
        g[past_node] = newnode
        v_aux = set(G2.nodes)-I_nodes

        #temporary
        dnode = 'd'
        dedge = (newnode, dnode)
        G2.add_node(dnode)
        G2.add_edge(*dedge)
        g[newnode] = dnode
        ordering[dnode] = ordering[newnode]+1
        sanity= 3 == sum((cls.criteria_f0(G2, v_aux, g),
                          cls.criteria_f1(G2, v_aux, g, ordering),
                          cls.criteria_f2(G2, v_aux, g, ordering)))
        G2.remove_edge(*dedge)
        G2.remove_node(dnode)
        del g[newnode]
        del ordering[dnode]

        if sanity:
            return (G2, g)


## Flow-related methods

    @classmethod
    def flow(cls, G, I, O):
        """Find flow by Mehdi Mhalla @ arXiv:0709.2670
        :G: nx.Graph(), the graph
        :I: iter, the list of input nodes
        :O: iter, the list of output nodes

        :return:
            (is_flow_exist, g, l, Vs_sorted, sanity)

        :is_flow_exist: indicates whether procedure ends with success.
                        Failure means the graph does not have a flow.
        g defines the flow map
        l ?
        Vs_sorted defines partial order classes
        """
        g, l, Vs = dict(), dict(), dict()

        for v in O: l[v] = 0

        is_cflow_exist = cls._flowaux_(G,I,O,O-I,1,g,l,Vs)

        #the class obtained is reversed
        Vs_sorted = dict()
        for j in range(1,max(Vs.keys())):
            Vs_sorted[j] = Vs[max(Vs.keys())-j]
        Vs_sorted[max(Vs.keys())] = set(O)

        # sanity check
        node_ordering = dict()
        for order,sset in Vs_sorted.items() :
            for node in sset :
                node_ordering[node] = order
        v_aux = set(G.nodes)-I-O

        sanity= 3 == sum((cls.criteria_f0(G, v_aux, g),
                     cls.criteria_f1(G, v_aux, g, node_ordering),
                     cls.criteria_f2(G, v_aux, g, node_ordering)))

        return (is_cflow_exist, g, Vs_sorted, sanity)


    @classmethod
    def _flowaux_(cls, G, In, Out, C, k, g, l, Vs):
        """ iterative method to find the causal flow
        :G: nx.Graph, the graph
        :In: set, input nodes
        :Out: set, output nodes
        :C:  set
        :k:  int
        :Vs: dict
        """
        V, Out2, C2 = set(G.nodes), set(), set()

        for v in C :
            u = set(G.neighbors(v)).intersection(V-Out)
            if len(u)==1:
                g[list(u)[0]] = v
                l[v] = k
                Out2 = Out2.union(u)
                C2 = C2.union({v})
        Vs[k]=Out2
        if len(Out2)==0 :
            if Out == V:
                return True
            else :
                return False
        else :
            return cls._flowaux_(G,In,Out.union(Out2),(C-C2).union(Out2.intersection(V)-In),k+1,g,l,Vs)


    @staticmethod
    def criteria_f0(G, v_aux, f):
        """
        Check flow condition 0: i in G(f(i))

        :G:nx.graph, the graph
        :v_aux:any iterable, the auxiliary nodes
        :f:dict, the dictionary contains flow information {1:2, 3:4, ..}
        """
        for i in v_aux :
            if i not in G.neighbors(f[i]):
                return False
        return True


    @staticmethod
    def criteria_f1(G, v_aux, f, ordering):
        """
        Check flow condition 1: j < f(j), forall j

        :G:nx.graph, the graph
        :v_aux:any iterable, the auxiliary nodes
        :f:dict, the dictionary contains flow information {1:2, 3:4, ..}
        :ordering:dict, the dictionary contains ordering for each node {1:1, 3:1, ..}
        """
        for j in v_aux :
            if ordering[j] >= ordering[f[j]]:
                return False
        return True


    @staticmethod
    def criteria_f2(G, v_aux, f, ordering):
        """
        Check flow condition 2: if j in G(f(i)), then j=i or i<j

        :G:nx.graph, the graph
        :v_aux:any iterable, the auxiliary nodes
        :f:dict, the dictionary contains flow information {1:2, 3:4, ..}
        :ordering:dict, the dictionary contains ordering for each node {1:1, 3:1, ..}
        """
        for i in v_aux:
            for j in G.neighbors(f[i]) :
                if ordering[j] < ordering[i] :
                    return False
        return True





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

