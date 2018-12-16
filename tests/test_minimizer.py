import sys
import pytest
sys.path.insert(1, '.')
from minimizer import Minimizer
import numpy as np


def test_gradient_simple_function():
    m = Minimizer()
    simple_function = lambda args: args[0] * args[0] + args[1] * args[1]
    gradient = m.compute_gradient([10, 10], 200, 0.0001, simple_function)
    print(gradient)
    for der in gradient:
        assert (der > 19.99)
        assert (der < 20.01)
