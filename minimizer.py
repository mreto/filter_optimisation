import matplotlib.pyplot as plt
from threading import Thread
from mpl_toolkits.mplot3d import Axes3D
from solver import Solver
from utilty import load_obj, save_obj, D_tuple
import numpy as np


class Minimizer:
    def __init__(self):
        """
        self.history - list containing all the intermiedete points, gradients and scores of
        the function in the format [[point, gradient, score], [point, gradient, score]]
        point and gradients list with the same length responding to the dimension

        solver - is the helper class that computes the function

        h - is the number to numerically compute derivative, it depends on the
        machine epsilon.
        """
        self.history = []
        self.solver = Solver(d13=3.4, d2=2.7)
        self.h = np.sqrt(np.finfo(float).eps)

    def compute_gradient(self):
        """
        IMPORTANT! To use this function there need to be atleast one record in self.history
        with point and score
        """
        gradient = []
        last_point, last_score = self.history[-1][0], self.history[-1][2]
        print("dupa")
        for i in range(len(last_point)):
            point_h = last_point.copy()
            h = 0.007
            point_h[i] = float(point_h[i] + h)
            score_h = self._compute_function(point_h)
            while score_h == last_score:
                h = h * 2
                point_h[i] = float(point_h[i] + h)
                score_h = self._compute_function(point_h)
        self.history[-1][1] = gradient
        return gradient

    def _compute_function(self, args):
        # TODO napisać w docach czemu sa dwie funkcje compute_function
        # TODO zastanowić się nad nazwami funkcji, może te co zmieniają cos w
        # srodku powinny być w podkreślnikami
        d13 = args[0]
        d2 = args[1]
        score = self.solver.function_complete(d13, d2)
        return score

    def compute_function(self):
        point = self.history[-1][0]
        score = self._compute_function(point)
        self.history[-1][2] = score
        return score

    def make_step(self, step_size):
        gradients = self.history[-1][1]
        last_point = self.history[-1][0]
        new_point = []
        for g, p in (zip(gradients, last_point)):
            new_point.append(p - (g * step_size))
        self.history.append([new_point, None, None])
        return new_point

    def minimize(self, d13_start, d2_start, max_steps, step_size):
        self.history.append([[d13_start, d2_start], None, None])
        # the score is put into the history
        self.compute_function()
        for i in range(max_steps):
            try:
                # in the function computed gradient is put into the history
                self.compute_gradient()
                # in the function new points is put into the history as a new record
                self.make_step(step_size)
                print(self.history)
                self.compute_function()
                # TODO to jest cringe ale dla testow
                save_obj(self.history, 'history_' + str(step_size))
            except:
                return self.history
        return self.history


if __name__ == "__main__":
    m = Minimizer()
    hist = m.minimize(4.5, 4.5, 50, 0.03)
