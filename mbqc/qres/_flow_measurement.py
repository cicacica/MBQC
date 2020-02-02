 #!/usr/bin/env python3

__doc__="""
Flow of measurements quantum computation

implemented:

    flow --- casual flow defined by Danos and Kashefi at:
    https://arxiv.org/abs/quant-ph/0506062

future, maybe:
    gflow --- generalized version of flow

"""

#standard libraries


#non-standard libraries
from mbqc.lib import FlowError



def flow(G, I, O):
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

    for v in O:
        l[v] = 0
    is_cflow_exist = _flowaux(G,I,O,O-I,1,g,l,Vs)

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

    if is_cflow_exist :
        sanity= 4 == sum([_criteria_f0(G, v_aux, g)
                         ,_criteria_f1(G, v_aux, g, node_ordering)
                         ,_criteria_f2(G, v_aux, g, node_ordering)
                         ,len(I.intersection(g.values()))==0
                        ])
        if not sanity :
            raise FlowError('DANGEROUS! FLOW EXISTS BUT NOT ALL CRITERIA FULLFILLED')


    return (is_cflow_exist, g, Vs_sorted)


def _flowaux(G, In, Out, C, k, g, l, Vs):
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
        if len(Out.intersection(V))== len(V):
            return True
        else :
            return False
    else :
        return _flowaux(G,In,Out.union(Out2),(C-C2).union(Out2.intersection(V)-In),k+1,g,l,Vs)


def _criteria_f0(G, v_aux, f):
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


def _criteria_f1(G, v_aux, f, ordering):
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


def _criteria_f2(G, v_aux, f, ordering):
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





