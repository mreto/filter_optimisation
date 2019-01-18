import matplotlib.pyplot as plt
from threading import Thread
from mpl_toolkits.mplot3d import Axes3D
from solver import Solver
from utilty import load_obj, save_obj, D_tuple
import numpy as np


class Minimizer:
    def __init__(self):
        """
        self.history - list containing all the intermiedete points, gradients
        and scores of the function in the format
        [[point, gradient, score], [point, gradient, score]]
        point and gradients list with the same length responding to the
        dimension

        Solver - is the helper class that computes the function
        in single point

        h - is the number to numerically compute derivative, it depends on the
        machine epsilon.

        all the function starting with the _ depends on history and
        also change it, they should not be called direct
        """
        self.history = []
        self.solver = Solver(d13_target=3.4, d2_target=2.7)
        self.h = np.sqrt(np.finfo(float).eps)

    def compute_gradient(self, last_point, last_score, h, function):
        gradient = np.zeros_like(last_point)
        for i in range(len(last_point)):
            h_local = h
            point_h = last_point.copy()
            point_h[i] = float(point_h[i] + h_local)
            score_h = function(point_h)
            while score_h == last_score:
                h_local = h_local * 2
                print(
                    'the slope was to small, the h is doubled and now it is %f'
                    % (h_local))
                print()
                point_h[i] = float(point_h[i] + h_local)
                score_h = function(point_h)
            gradient[i] = (score_h - last_score) / h_local
            print("partial gradient is")
            print(gradient)
        return gradient

    def _compute_gradient(self):
        """
        IMPORTANT! To use this function there need to be atleast one record in self.history
        with point and score
        """
        gradient = []
        last_point, last_score = self.history[-1][0], self.history[-1][2]
        h = 0.008
        gradient = self.compute_gradient(
            last_point,
            last_score,
            h,
            self.compute_goal_function,
        )
        print("gradient is: ")
        print(gradient)
        self.history[-1][1] = gradient
        return gradient

    # IN PROGRESS DOESNT WORK
    def line_search(self, q, last_score, gradient, derivative_step):
        """
        return the size of the step, according to line search algorithm
        """
        lambda_a = lambda a, q, f_0, gradient: f_0 + q * (gradient).dot(-gradient) * a
        # approx = lambda a, gradient: f_0 + a * (gradient).dot(-gradient)
        # while lambda_a(a)<

    def compute_goal_function(self, args):
        """
        Compute the function without changing history of minimiser
        """
        # TODO napisać w docach czemu sa dwie funkcje compute_function
        d13 = args[0]
        d2 = args[1]
        score = self.solver.goal_function(d13, d2)
        return score

    def _compute_goal_function(self):
        """
        Compute the score for the last point in the history and put
        it into it.
        """
        point = self.history[-1][0]
        print("computed point i")
        print(point)
        score = self.compute_goal_function(point)
        self.history[-1][2] = score
        return score

    def _make_step(self, step_size):
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
        self._compute_goal_function()
        for i in range(max_steps):
            # in the function computed gradient is put into the history
            print("start computing gradient")
            self._compute_gradient()
            # in the function new points is put into the history as a new
            # record
            print("start making step")
            self._make_step(step_size)
            print("start computing goal in new point")
            self._compute_goal_function()
            # TODO to jest cringe ale dla testow
            save_obj(self.history, 'history_' + str(step_size))
            print(self.history)
        return self.history


if __name__ == "__main__":
    m = Minimizer()
    hist = m.minimize(4.5, 4.5, 50, 0.03)
