from threading import current_thread
import pdb
import matplotlib.pyplot as plt
import numpy as np
from subprocess import Popen
from mesh import mesh, group_points
from utilty import savePoints
from scipy.signal import savgol_filter


class Solver:
    def __init__(self,
                 f1_target=None,
                 f2_target=None,
                 d13_target=None,
                 d2_target=None):
        """

        Class that task is to solve the goal function.
        The function first compute the f1 and f2 values for d1, d2,
        and the output is the sum(f1_target - f1) + sum(f2_target-f2)

        The constactor can take either the already computed f1_target
        and f2_target, or get teh d13 and d2 and then computer the
        above by itself, otherwise is raise an Exception

        The arguments _witdth, _lsList, _epsilon and _lcar are
        fixed we try to optimize only d13, d2.

        The solver can compute the f1, f2 with computer_f().

        It can compute the whole goal_function with the initialy
        given f1_taget, f2_target with goal_function()

        If the goal_function is used the f1, f2 are stored as
        hisory (it stores only the recent one)

        Every time the characteristic is computed is also save
        in history (the last computed overwrite it)
        """
        self._width = 6.4
        self._lsList = [6.4, 3.2, 3.2, 6.4]
        self._epsilon = 0.01
        # TODO zmien lcar na 0.3 zmieniłem tylko do testów na inne
        self._lcar = 0.3
        self._f1, self._f2 = None, None
        self._charac1, self._charac2, self._freq = None, None, None
        self._d_list = [None]
        self._old_mesh = None
        if d13_target is not None and d2_target is not None:
            self.f1_target, self.f2_target = self.compute_f(
                d13_target, d2_target)
        elif f1_target is not None and f2_target is not None:
            self.f1_target, self.f2_target = f1_target, f2_target
        else:
            raise ValueError("You didnt specified d_list nor f_target")

    def get_triangles_angles(self, triangles_ids, points):
        """
        return angles in every triangle in the mesh
        """
        angles = []
        for i, trian_id in enumerate(triangles_ids):
            p1, p2, p3 = points[trian_id[0]], points[trian_id[1]], points[
                trian_id[2]]
            p12 = np.sqrt(np.sum(((p1 - p2)**2)))
            p23 = np.sqrt(np.sum(((p2 - p3)**2)))
            p13 = np.sqrt(np.sum(((p1 - p3)**2)))
            angles1 = np.degrees(
                np.arccos((p12**2 + p13**2 - p23**2) / (2 * p12 * p13)))
            angles2 = np.degrees(
                np.arccos((p12**2 + p23**2 - p13**2) / (2 * p12 * p23)))
            angles3 = np.degrees(
                np.arccos((p13**2 + p23**2 - p12**2) / (2 * p13 * p23)))
            angles.append(angles1)
            angles.append(angles2)
            angles.append(angles3)
        values, _, _ = plt.hist(angles, bins=[i for i in range(0, 180, 10)])
        return values

    def check_triangles_angles(self, triangles_ids, points):
        pass

    def fx(self, x, x_max, x_min, xc):
        """
        x point in wich we want to compute translation
        x_max maximal value of x in filter
        x_min min value of x in filter
        xc point in which the trasforation was made
        """
        if xc > x:
            return (1 - ((x - xc) / (xc - x_min))**2)**(3 / 2)
        else:
            return (1 - ((x - xc) / (x_max - xc))**2)**(3 / 2)

    def fy(self, y, y_max, y_min, yc):
        """
        y point in wich we want to compute translation
        y_max maximal value of y in filter
        y_min min value of y in filter
        yc point in which the trasforation was made
        """
        if yc > y:
            return (1 - ((y - yc) / (yc - y_min))**2)**(3 / 2)
        else:
            return (1 - ((y - yc) / (y_max - yc))**2)**(3 / 2)

    def deform(self, points, xc, yc, h):
        """
        change the mesh with the algorithm in ms
        """
        x_max = 0
        for i in self._lsList:
            x_max += i
        x_min = 0
        y_max = self._width
        y_min = 0
        new_points = np.zeros_like(points, dtype=np.float_)
        for i, point in enumerate(points):
            # in our case the point only moves in one dimension - y
            # so we only change the point [1]
            new_points[i][0] = point[0]
            new_points[i][1] = point[1] + (
                self.fy(point[1], y_max, y_min, yc) * self.fx(
                    point[0], x_max, x_min, xc) * h)
        return new_points

    def get_characteristic(self, d_list):
        # Check if it is possible to deform existing mesh,
        # otherwise create new

        # if all(d is not None
        #        for d in self._d_list) and self._old_mesh is not None:

        #     (points, triangles_ids, p_list) = self._old_mesh
        #     x = 0.0
        #     for l, old_d, new_d in zip(self._lsList, self._d_list, d_list):
        #         x += l
        #         y = (self._width - old_d) / 2
        #         if old_d != new_d:
        #             points = self.deform(points, x, y, new_d - old_d)
        #             p_list = self.deform(p_list, x, y, new_d - old_d)
        #         if np.abs(new_d - old_d) > 0.002:
        #             self._d_list = d_list
        #             (points, cells, _, _, _, p_list) = mesh(
        #                 self._width, self._lsList, d_list, self._epsilon,
        #                 self._lcar)
        #             self._old_mesh = (np.array(points),
        #                               np.array(cells['triangle']), p_list)
        #             triangles_ids = np.array(cells['triangle'])
        #             break
        # else:
        self._d_list = d_list
        (points, cells, _, _, _, p_list) = mesh(
            self._width, self._lsList, d_list, self._epsilon, self._lcar)
        self._old_mesh = (np.array(points), np.array(cells['triangle']),
                          p_list)
        triangles_ids = np.array(cells['triangle'])
        # end of else

        # group the point in as we need them in Matlab script
        (enterPoints, exitPoints, boundPoints, freePoints,
         enterIndx, exitIndx, boundIndx, freeIndx) = group_points(
             points, p_list, self._lsList, self._width)

        # each thread saves the file for matlab script with own id to prevent
        # races
        id = current_thread().getName()
        directory = './MatlabGen/Siatka/'

        # save the data to files in the 'directory'
        savePoints(points, triangles_ids, enterPoints, exitPoints, boundPoints,
                   freePoints, enterIndx, exitIndx, boundIndx, freeIndx,
                   directory, id)

        # run the matlab script 'main' with the id as an arrgument
        matlab_procces = Popen(["octave", "--eval", "main('" + id + "')"],
                               cwd="./MatlabGen")
        matlab_procces.wait()

        # retrieve the data from the matlab script
        charac1 = np.genfromtxt(
            "./MatlabGen/" + id + "_charac1.csv", delimiter=',')
        charac2 = np.genfromtxt(
            "./MatlabGen/" + id + "_charac2.csv", delimiter=',')
        freq = np.genfromtxt("./MatlabGen/" + id + "_freq.csv", delimiter=',')
        return charac1, charac2, freq / 1e+9

    def get_local_minimums(self, charac1, freq):
        # we should make sure that there only two local minimums
        # I didnt check it, just assumed that there are
        # very dangerous function, assumes a lot
        charac1_smooth = savgol_filter(charac1, 5, 3)
        mask = np.diff(np.diff(charac1_smooth[0])) > 0
        val_max = freq[np.argwhere(mask == True).flatten() + 1]
        minimum1 = val_max[0]
        minimum2 = val_max[1]
        return minimum1, minimum2

    def compute_f(self, d13, d2):
        """
        Compute the f1, f2 (minimum1, and minimum2)
        """
        d_list = [d13, d2, d13]
        self._charac1, self._charac2, self._freq = self.get_characteristic(
            d_list)
        minimum1, minumum2 = self.get_local_minimums(self._charac1, self._freq)
        return minimum1, minumum2

    def print_characteristic(self):
        """
        Print the recent characteristic
        """
        if self._charac1 is None or self._charac2 is None:
            raise ValueError("You didnt computed characteristic yet")
        plt.plot(self._freq, self._charac1[0], 'r')
        plt.plot(self._freq, self._charac2[0], 'b')
        plt.show()

    def goal_function(self, d13, d2):
        """
        Compute the goal function sum(f1_target - f1) + sum(f2_target-f2)
        The f1_target and f2_target are created only once at the creation
        of the object, the recent f1, f2, charact1 and charact2
        are stored as members.
        """
        if self.f1_target is None or self.f2_target is None:
            raise ValueError("You didnt specified d_list nor f_target")
        self._f1, self._f2 = self.compute_f(d13, d2)
        score = np.sum(
            np.absolute(self.f1_target - self._f1) +
            np.absolute(self.f2_target - self._f2))
        return score

    def fu(x):
        pdb.set_trace()
        pdb.breakpoint()
        return x + 1
