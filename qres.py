#!/usr/bin/env python3

__doc__=""" qres --- quantum resource --- contains GraphState class. Graph state object as a resource of 1WQC
computations. Notations are adapted from paper xxx:
"""
__author__ = "Cica Gustiani"
__license__ = "Apache2"
__version__ = "1.0.0"
__maintainer__ = "Cica Gustiani"
__email__ = "cicagustiani@gmail.com"


#standard libraries
import networkx as nx


class GraphState:
    """
    create graph state as a resouce for 1WQC computation.
    """
    def __init__(self, G, I=set(), O=set()):
        """ Instantiation of the GraphState object. That is the resource of
        1WQC computations. Only works with a class of graphs that have flow.

        param
            :G: networkx.graph, an open simple graph
            :I: set, a set input nodes
            :O: set, a set of output nodes
        """
        #input checking
        if nx.classes.graph.Graph != type(G):
            raise TypeError('provide a simple graph, a networkx.Graph object')

        if set != type(I) or not I.issubset(set(G.nodes())) :
            raise ValueError('provide I as a (sub)set of nodes in G, as quantum input')

        if set != type(O) or not O.issubset(set(G.nodes())) :
            raise ValueError('provide O as a (sub)set of nodes in G, as quantum input')

        #initializations
        self.G = G
        self.I = I
        self.O = O
        self.partial_ordering = False
        self.set_flow()

        #quantum part
        self.quantum_input = False
        self.quantum_register = False


    def __copy__(self):
        return GraphState(self.G, self.I, self.O)


    def set_quantum_input(self, rho_in):
        """
        assign quantum state to input nodes
        """
        pass


    def set_flow(self):
        """
        set flow by adding flow attribute to every node and
        set attribute partial_ordering to the graph
        """
        f_exist, f, poset, flow_criteria = self.flow(self.G, self.I, self.O)

        if not f_exist :
            raise RuntimeError('graph does not have a flow')
        if f_exist and not flow_criteria :
            raise ValueError('inconsistent result: A THEORY BUG')

        for dom, cod in f.items():
            self.G.add_node(dom, flow=cod)

        self.partial_ordering = poset




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

        sanity = cls._check_flow_conditions_(G, O, g, Vs_sorted)

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
    def _check_flow_conditions_(G, O, f, L):
        """ Check the flow conditions are fullfilled

        param
            :G: networkx.Graph, the corresponding graph
            :O: set, the output nodes
            :f: dict, flow map, node to node
            :L: dict, the ordering class 1..N

        return
            (bool,bool,bool), truth for each criteria
        """
        def get_flow_class(v,L):
            """
            Return the class of node v
            :v: node
            :L: dict, the ordering class in format {1: {1, 2}, ...
            """
            for c, nodes in L.items():
                if v in nodes :
                    return c
        aux = list(set(G.nodes)-set(O))

        #condition 1: j < f(j), forall j
        c1 = True
        for j in aux :
            if get_flow_class(j,L) >= get_flow_class(f[j],L):
                c1= False
                break

        #condition 2: if j in G(f(i)), then j=i or i<j
        c2 = True
        for i in aux:
            for j in G.neighbors(f[i]) :
                if get_flow_class(j,L)<get_flow_class(i,L) :
                    c2 = False
                    break

        #condition 3: i in G(f(i))
        c3 = True
        for i in aux :
            if i not in G.neighbors(f[i]):
                c3 = False
                break

        return (c1,c2,c3)








