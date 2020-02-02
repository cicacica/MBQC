 #!/usr/bin/env python3

__doc__="""
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
import json
from multiprocessing import Pool, cpu_count
from itertools import product, combinations
from time import time

#non-standard libraries
from mbqc.lib import FlowError
from mbqc.qres import flow


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
        Set attribute ntypes for every node: {input, output, aux(iliary)}
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
        f_exist, f, poset = flow(self.G, self.I, self.O)

        if not f_exist :
            raise FlowError('graph does not have a flow. Sorry, find another Graph')

        for dom, cod in f.items():
            self.G.add_node(dom, flow=cod)

        self.ordering_class = poset
        self.f = f


## aesthetic-related methods
    def draw_graph(self, outfile='out.png', title='', **options):
        """
        Draw graph with some options

        output : out.png file
        title : str, the title of the graph
        options : { flow : True,
                    total_order : False,
                    partial_order : False
                  }
        """
        opt = {'flow': True, #done
               'total_order': False, #not yet
               'partial_order': False, #not yet
               'color': True
               }
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
        sdot = 'digraph{ labelloc="t"; label="%s";'%title+\
               ''.join(snodes)+'rankdir=LR;'+''.join(sedges)+\
               '{rank=same;'+ ';'.join(str(i) for i in self.I)+';}'+\
               '{rank=same;'+ ';'.join(str(i) for i in self.O - self.I)+';}'+\
               '}'
        graphv = pgv.AGraph(sdot)
        graphv.layout(prog='dot')
        graphv.draw(outfile)


## open graphs generation-related method

    @classmethod
    def generate_all(cls, nodes, I, O, ncpu=False, parallel=True):
        """
        Generate all possible open graphs. This does not consider isomorphism, since
        graph isomorphism is NP, while flow assessment is in P. Since this is a
        brute-force approach, I recommend you to estimate the resources first.
        param
            :nodes: list(int, str), the complete list of nodes
            :I: set
            :O: set
            :ncpu: int
            :parallel: boolean
        """
        #initialization
        G = nx.complete_graph(nodes)
        nset = cls.get_power_set(G.nodes)

        ncpu = ncpu if ncpu else cpu_count()
        P = Pool(ncpu)
        edges_pset = cls.get_power_set(G.edges)

        p_args = [(edges,G.nodes, I,O) for edges in edges_pset]
        results = P.starmap(cls._try_graph, p_args)
        opengraphs = [(res, I, O) for res in results if res]


    @classmethod
    def random_open_graph(cls, n_I, n_O, n_aux, ngraph=False, random_seed=None, ncpu=False, parallel=True):
        """
        Return a (list) open graphs at random, with the following steps:
            1) choose input-output nodes at random, where they may partially overlap
            2) iterates all possible graphs
            3) chooses n-graphs at random.
        Seeding is done once.

        param
            :n_I:int, number of input nodes
            :n_O:int, number of output nodes
            :n_aux:int, number of auxiliary nodes
            :ngraph:bool or int, return all possible graphs if not stated
            :random_seed:int, random seed
            :ncpu:int=cpu_count(), number of cpu
        return
            (G,I,O) or list((G,I,O))
        """
        nodes = range(n_I+n_O+n_aux)

        #get random input-output set
        random.seed(random_seed)
        I, O = {1}, {1}
        while I == O :
            I = set(random.choice(nodes), size=n_I, replace=False)
            O = set(random.choice(nodes), size=n_O, replace=False)
        print("Input and output set", I, O)

        opengraphs = cls.generate_all(nodes, I, O, ncpu=ncpu, parallel=parallel)

        if ngraph :
            return random.choice(opengraphs, size=ngraph, replace=False)
        else :
            random.seed(random_seed)
            return random.choice(opengraphs)


    @staticmethod
    def _try_graph(edges, nodes, I, O):
        """
        Try to obtain a graph with flow by removing edges of graph G

        :G: nx.Graph(), the graph
        :I: iter, the list of input nodes
        :O: iter, the list of output nodes
        :redges: list(tuple), pair of nodes at the end of edge to be removed
        """
        if len(edges) == 0 :
            return False

        G = nx.Graph(edges)
        G.add_nodes_from(nodes)

        if not nx.is_connected(G):
            return False
        else :
            flow_exist, f, vs = flow(G,I,O)
            if flow_exist :
                return G
            else :
                return False



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

        return power_set


