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

import example_graphstates
from example_graphstates import *
from boqc import Lazy1WQC
from qres import OpenGraph

def get_graphs_fun():
    """
    Get the graphs functions. Those functions generate graphs.
    """
    return [globals()[name] for name in dir(example_graphstates) if 'graph' in name]


def test_lemma2(repeat=1):
    """
    Test lemma 2 from BOQC paper by trying out different graphs
    """
    print("Start testing Lemma 2 with %i repetition, different random orderings"%repeat)
    iotypes = {'classical', 'quantum'}
    for i_type, o_type in product(iotypes, repeat=2):
        print('input:%s ;  output:%s'%(i_type, o_type))
        for rep in range(repeat):
            for graphf in get_graphs_fun():
                lazyc = Lazy1WQC(*graphf(), dict())
                lazyc.set_total_order_random()
                lazyc.set_io_type(i_type, o_type)
                print(lazyc.lemma2(), graphf.__name__)
        print('')


def test_lemma3(repeat=1):
    """
    Test lemma 3 from BOQC paper by trying out different graphs
    """
    print("Start testing Lemma 3 with %i repetition, different random orderings"%repeat)

    iotypes = {'classical', 'quantum'}
    for i_type, o_type in product(iotypes, repeat=2):
        print('input:%s ;  output:%s'%(i_type, o_type))
        for rep in range(repeat):
            for graphf in get_graphs_fun():
                lazyc = Lazy1WQC(*graphf(), dict())
                lazyc.set_total_order_random()
                lazyc.set_io_type(i_type, o_type)
                print(lazyc.lemma3(), graphf.__name__)
        print('')


def test_lemma4(repeat=1):
    """
    Test lemma 4 from BOQC paper by trying out different graphs
    """
    print("Start testing Lemma 4 with %i repetition, different random orderings"%repeat)

    for rep in range(repeat):
        for graphf in get_graphs_fun():
            lazyc = Lazy1WQC(*graphf(), dict())
            lazyc.set_total_order_random()
            print(lazyc.lemma4(), graphf.__name__)



def test_conj1(repeat=1, n_sampling=10):
    print('potential conjecture 1: sampling number %i'%n_sampling)
    iotypes = {'classical', 'quantum'}
    for i_type, o_type in product(iotypes, repeat=2):
        print('input:%s ;  output:%s'%(i_type, o_type))
        for r in range(repeat):
            for graphf in get_graphs_fun():
                lazyc = Lazy1WQC(*graphf(), dict())
                lazyc.set_io_type(i_type, o_type)

                guess1 = max([len(lazyc.I),len(lazyc.O)])+1
                guess2 = max([len(c) for c in lazyc.ordering_class.values()])+1

                print(*lazyc.bound_physical_qubit(nsampling=n_sampling),  guess1, guess2, graphf.__name__)
            print(" ")



if __name__ == "__main__" :
    args = sys.argv[1:]

    err_message = """
    You did it wrong, try this:

        test.py kind repeat [n_I, n_O, n_aux]

    where kind = conj1 | lemma2 | lemma3 | lemma4 | random
    arguments inside []  are needed for random kind
    """
    try :
        kind = args[0]
        repeat = int(args[1])

        if kind == 'conj1' :
            test_conj1(repeat=repeat, n_sampling=100)
            print('')
        elif kind == 'lemma2':
            test_lemma2(repeat)
            print('')
        elif kind == 'lemma3':
            test_lemma3(repeat)
            print('')
        elif kind == 'lemma4':
            test_lemma4(repeat)
            print('')
        elif kind == 'random' :
            n_I, n_O, n_aux = map(int, args[1:4])
            OpenGraph.random_open_graph(n_I, n_O, n_aux)
        else :
            raise ValueError(err_message)

    except IndexError :
        print(err_message)

