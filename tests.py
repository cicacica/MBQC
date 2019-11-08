#!/usr/bin/env python3

__doc__: """
    Some program tests.

    Implemented :

        - Lemma 2
        - Lemma 3
        - Lemma 4
        - Conjecture 1

    """

from itertools import product
import sys
from subprocess import run
import networkx as nx
import json

import example_graphstates
from example_graphstates import *
from boqc import Lazy1WQC
from qres import OpenGraph, FlowError

def get_graphs_fun():
    """
    Get the graphs functions. Those functions generate graphs.
    """
    return [globals()[name] for name in dir(example_graphstates) if 'graph' in name]


def test_lemma2(gio_list):
    """
    Test lemma 2 from BOQC paper by trying out different graphs

    :gio_list: list of open graph [(G,I,O,graph_name)]
    """
    print("Start testing Lemma 2 with repetition, different random orderings")
    iotypes = {'classical', 'quantum'}
    for i_type, o_type in product(iotypes, repeat=2):
        print('input:%s ;  output:%s'%(i_type, o_type))
        for graphf in gio_list:
            try :
                lazyc = Lazy1WQC(*graphf[0:3], dict())
                lazyc.set_total_order_random()
                lazyc.set_io_type(i_type, o_type)
                print(lazyc.lemma2(), graphf[3])
            except FlowError :
                print('no flow', graphf[3])


def test_lemma3(gio_list):
    """
    Test lemma 3 from BOQC paper by trying out different graphs

    :gio_list: list of open graph [(G,I,O, graph_name)]
    """
    print("Start testing Lemma 3 , different random orderings")

    iotypes = {'classical', 'quantum'}
    for i_type, o_type in product(iotypes, repeat=2):
        print('input:%s ;  output:%s'%(i_type, o_type))
        for graphf in gio_list:
            lazyc = Lazy1WQC(*graphf[0:3], dict())
            lazyc.set_total_order_random()
            lazyc.set_io_type(i_type, o_type)
            print(lazyc.lemma3(), graphf[3])


def test_lemma4(gio_list):
    """
    Test lemma 4 from BOQC paper by trying out different graphs
    :gio_list: list of open graph [(G,I,O, graph_name)]
    """
    print("Start testing Lemma 4, different random orderings")

    for rep in range(repeat):
        for graphf in gio_list:
            lazyc = Lazy1WQC(*graphf[0:3], dict())
            lazyc.set_total_order_random()
            print(lazyc.lemma4(), graphf[3])


def test_conj1(gio_list, show='print', n_sampling=10):
    """
    Test conjecture 1 from BOQC paper by trying out different graphs.
    Check the upper bound for every graph is |O|+1
    :gio_list: list of open graph [(G,I,O, graph_name)]
    :show: str(print|draw), the means to show the result
    """
    print('Conjecture 1: bound of #physical qubit=|O|+1.  Sampling number %i'%n_sampling)
    for i,res in enumerate(results):
        bounds, iotypes = [], ('classical', 'quantum')
        for i_type, o_type in product(iotypes, repeat=2):
            lazyc = Lazy1WQC(*res,dict())
            lazyc.set_io_type(i_type, o_type)
            bounds.append(lazyc.bound_physical_qubit(nsampling=10))
        upper_bound, conj1 = max(bounds), len(res[2])+1
        if upper_bound > conj1 :
            print("Conjecture 1 fails at graph with edges",lazyc.G.edges)

        if show == 'draw':
            fname = 'openg-%i.png'%i
            title = 'nqubit: %i, conj1: %i'%(upper_bound, conj1)
            lazyc.draw_graph('%s/%s'%(outpath,fname), title=title)




def get_random_graphs(n_I, n_O, n_aux, outpath, not_tight_bound_draw=True, ncpu=False, conj1=True):
    """
    Obtain random graphs with flow in folder 'graphf'. This also tests conjecture 1
    :n_I: int, number of input
    :n_O: int, number of output
    :n_aux: int, number of n_aux
    :outpath: str, output folder
    :not_equal_bound_only:boolean, only draw if it is not a tight bound
    :conj1:boolean, also test the conjecture
    """
    run(['mkdir', '-p', outpath])
    results = OpenGraph.random_open_graph(n_I, n_O, n_aux, return_many=True, random_seed=None, ncpu=ncpu)

    dicress =  []
    for i,res in enumerate(results) :
        dres = dict()
        dres['nodes']=list(res[0].nodes())
        dres['edges']=list(res[0].edges())
        dres['I'] = list(res[1])
        dres['O'] = list(res[2])
        dres['bound']=n_O+1

        lazyc = Lazy1WQC(*res,dict())
        dres['nqubit']=lazyc.bound_physical_qubit(nsampling=10)

        if not_tight_bound_draw and dres['bound'] != dres['nqubit']:
            title = 'nqubit: %i, conj1: %i'%(dres['nqubit'], dres['bound'])
            lazyc.draw_graph('%s/graph%i.png'%(outpath,i), title=title)

        dicress.append(dres)

    with open(outpath+'/random_graphs.json', 'w') as outf :
        json.dump(dicress, outf)




if __name__ == "__main__" :
    args = sys.argv[1:]

    err_message = """
    You did it wrong, try this:

        test.py kind (repeat)/[n_sampling] [n_I, n_O, n_aux, outpath, graph_list_json]

    where kind = conj1 | lemma2 | lemma3 | lemma4 | random

    note:
        argument inside () is needed for 'conj1' kind
        arguments inside []  are needed for 'random' kind

    """
    try :
        kind = args[0]
        repeat = int(args[1])
    except IndexError :
        sys.exit(err_message)

    gio_list = [(*func(),func.__name__) for func in get_graphs_fun()]

    if kind == 'conj1' :
        try :
            n_sampling = int(args[2])
        except IndexError :
            sys.exit(err_message)

        for i in range(repeat):
            test_conj1(gio_list, n_sampling=n_sampling)
        print('')

    elif kind == 'lemma2':
        for i in range(repeat):
            test_lemma2(gio_list)
        print('')

    elif kind == 'lemma3':
        for i in range(repeat):
            test_lemma3(gio_list)
        print('')

    elif kind == 'lemma4':
        for i in range(repeat):
            test_lemma4(gio_list)
        print('')

    elif kind == 'random' :
        try :
            n_I, n_O, n_aux= map(int, args[1:4])
            folder_name = args[4]
        except IndexError :
            sys.exit(err_message)

        try :
            graph_file = args[5]
        except IndexError :
            pass

        get_random_graphs(n_I, n_O, n_aux, folder_name)
    else :
        raise ValueError(err_message)

