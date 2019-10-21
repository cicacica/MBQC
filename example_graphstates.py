#!/usr/bin/env python3

import networkx as nx


def graph_example_boqc():
    """ This is the graph that is used to demonstrate boqc
    """
    G = nx.Graph()
    G.add_node(1, pos=(0,0.5))
    G.add_node(2, pos=(0,1.5))
    G.add_node(3, pos=(1,1.5))
    G.add_node(4, pos=(2,2  ))
    G.add_node(5, pos=(1,0.5))
    G.add_node(6, pos=(2,1))
    G.add_node(7, pos=(2,-0.5))
    G.add_edges_from([(1,5),(2,3),(3,4),(3,6),(5,6),(5,7),(2,5),(4,7)])

    I = set([1,2])
    O = set([4,6,7])

    return (G,I,O)


def graph_H():
    """
    return Graph state :  *--o--o
                             |
                          *--o--o
    """
    G = nx.Graph()
    G.add_node(1,pos=(0,0),total_order=1)
    G.add_node(2,pos=(0,1),total_order=2)
    G.add_node(3,pos=(1,0),total_order=3)
    G.add_node(4,pos=(1,1),total_order=4)
    G.add_node(5,pos=(2,0),total_order=5)
    G.add_node(6,pos=(2,1),total_order=6)

    edges = [(1,3),(3,5),(2,4),(4,6),(3,4)]
    G.add_edges_from(edges)

    I = set([1,2])
    O = set([5,6])

    return (G,I,O)


def graph_1d():
    """
    return Graph state :  *--o--o--o--o
            0  a  b  g
    """
    G = nx.Graph()
    G.add_node('in',pos=(0,0))
    G.add_node( 1,  pos=(1,0))
    G.add_node( 2,  pos=(2,0))
    G.add_node( 3,  pos=(3,0))
    G.add_node( 4,  pos=(4,0))

    edges = [('in',1),(1,2),(2,3),(3,4)]
    G.add_edges_from(edges)

    I = set(['in'])
    O = set([4])

    return (G,I,O)


def graph_kashefi_duncan():
    """
    The graph from "Determinism in the one-way model"
    """
    G = nx.Graph()
    G.add_node(1, pos=(0,0.5))
    G.add_node(2, pos=(0,1.5))
    G.add_node(3, pos=(1,1.5))
    G.add_node(4, pos=(2,2  ))
    G.add_node(5, pos=(1,0.5))
    G.add_node(6, pos=(2,1))
    G.add_node(7, pos=(2,0))
    G.add_edges_from([(2,3),(2,5),(3,4),(1,5),(3,4),(3,6),(5,6),(5,7)])

    I = set({1,2})
    O = set({4,6,7})

    return (G,I,O)


def graph_brickwork(H=5, W=8):
    """Generate a brickwork graph

    Generate a brickwork graph with a given width and height

    :H:int, height (number of input qubits)
    :W:int, width (or number of qubit columns)
    """
    G = nx.Graph()

    # add vertices
    G.add_nodes_from(range(0,H*W))

    # add vertical edges
    for w in range(2,W,2):
        for h in range(0,H-1):
            if (2 == w % 8 or 4 == w % 8) and 0 == h % 2:
                G.add_edge(h + w*H,(h+1) + w*H)

            if (6 == w % 8 or 0 == w % 8) and 1 == h % 2:
                G.add_edge(h + w*H, (h+1) + w*H)

    # add horizontal edges
    for w in range(1,W):
        for h in range(0,H):
            G.add_edge(h + (w-1)*H,h + w*H)

    # input
    I = set(range(0,H))
    O = set(range(len(G.nodes)-H,len(G.nodes)))

    return (G,I,O)


## graph state that has known outcome with pre-determined angles

def graph_cnot():
    """The CNOT gate
                         *
                         |
                      *--o--o
    here is an example where I and O are overlap
    """
    G = nx.Graph()
    G.add_edges_from([(1,3),(2,3),(3,4)])
    I,O = set([1,2]), set([2,4])

    return (G,I,O)

def graph_exact3grover():
    """ The graph used in exact 3 qubits grover. Node posisitions are set.
    """
    G = nx.Graph()

    # positions
    r1=[1,4,6,8,10,11,13,19,21,23,26,28,30,32,35,38,41,43,45,47,49,55,57,59,
        62,64,66,68,75,77,79,81,87,89,92,94,96]
    r2=[2,5,7,9,15,17,20,22,24,27,29,31,33,36,39,42,44,46,51,53,56,58,60,63,
        65,67,69,71,73,76,78,83,85,88,90,91]
    r3=[3,12,14,16,18,25,34,37,40,48,50,52,54,61,70,72,74,80,82,84,86,93,95,97]

    G.add_edges_from([(r1[i],r1[i+1]) for i in range(len(r1)-1)])
    G.add_edges_from([(r2[i],r2[i+1]) for i in range(len(r2)-1)])
    G.add_edges_from([(r3[i],r3[i+1]) for i in range(len(r3)-1)])
    G.add_edges_from([(6,7),(19,20),(15,16),(23,24),(32,33),(38,40),(39,40),
                      (44,43),(55,56),(51,52),(59,60),(71,72),(75,76),(79,80),
                      (83,84),(87,88),(92,93)])

    I = set([1,2,3])
    O = set([96,91,97])

    return (G,I,O)

