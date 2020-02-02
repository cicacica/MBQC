#!/usr/bin/env python3

__doc__="""
Test for boqc.lib._exceptions.py
"""

from boqc.lib import FlowError

def test_flowerror():
    """
    Raise FlowError: first trial of pytest
    """
    try:
        raise FlowError("Flowerror test works")
    except FlowError :
        assert(True, "exception raise works")
