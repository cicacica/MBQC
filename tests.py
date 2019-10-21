#!/usr/bin/env python3

__doc__: """
    Some program tests.

    Implemented :

        - Lemma 2
        - Lemma 3
        - Lemma 4

    """


import example_graphstates
from example_graphstates import *
from boqc import Lazy1WQC


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

    for rep in range(repeat):
        for graphf in get_graphs_fun():
            lazyc = Lazy1WQC(*graphf(), dict())
            lazyc.set_total_order_random()
            print(lazyc.lemma2(), graphf.__name__)


def test_lemma3(repeat=1):
    """
    Test lemma 3 from BOQC paper by trying out different graphs
    """
    print("Start testing Lemma 3 with %i repetition, different random orderings"%repeat)

    for rep in range(repeat):
        for graphf in get_graphs_fun():
            lazyc = Lazy1WQC(*graphf(), dict())
            lazyc.set_total_order_random()
            print(lazyc.lemma3(), graphf.__name__)



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



if __name__ == "__main__" :

    test_lemma2(5)
    print('')
    test_lemma3(5)
    print('')
    test_lemma4(5)

