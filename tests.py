#!/usr/bin/env python3

__doc__: """
    Some program tests.

    Implemented :

        - lemma 2

    """


import example_graphstates
from example_graphstates import *
from boqc import Lazy1WQC


def get_graphs_fun():
    """
    Get the graphs functions. Those functions generate graphs.
    """
    return [globals()[name] for name in dir(example_graphstates) if 'graph' in name]


def test_lemma2():
    """
    Test lemma 2 from BOQC paper by trying out different graphs
    """
    print("Start testing Lemma 2")
    for graphf in get_graphs_fun():
        lazyc = Lazy1WQC(*graphf(), dict())
        lazyc.set_total_order_random()
        print(lazyc.lemma2(), graphf.__name__)



if __name__ == "__main__" :

    test_lemma2()

