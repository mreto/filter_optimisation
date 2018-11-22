from threading import current_thread
import matplotlib.pyplot as plt
import numpy as np
from subprocess import Popen
from mesh import mesh, group_points
from utilty import savePoints
from scipy.signal import savgol_filter


class Solver:
    def __init__(self,
                 f1_taget=None,
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
        self.f1, self.f2 = None, None
        self.charac1, self.charac2, self.freq = None, None, None
        if d13_target and d2_target is not None:
            self.f1_target, self.f2_target = self.compute_f(
                d13_target, d2_target)
        elif f1_taget and f2_target is not None:
            self.f1_target, self.f2_target = f1_taget, f2_target
        else:
            raise ValueError("You didnt specified d_list nor f_target")

    def _helper_to_remove(self, d_list):
        # generate the and retrieve all the data
        (points, cells, _, _, _, pList) = mesh(
            self._width, self._lsList, d_list, self._epsilon, self._lcar)

        # group the point in as we need them in Matlab script
        (enterPoints, exitPoints, boundPoints, freePoints,
         enterIndx, exitIndx, boundIndx, freeIndx) = group_points(
             points, pList, self._lsList, self._width)

        # each thread saves the file for matlab script with own id to prevent races
        id = current_thread().getName()
        directory = './MatlabGen/Siatka/'

        # save the data to files in the 'directory'

        # TODO change names
        traingles_id = np.array(cells['triangle'])
        points_numpy = np.array(points)
        angles = []
        sum_angles = []
        sum_absolute = []
        for traian in traingles_id:
            p1, p2, p3 = points_numpy[traian[0]], points_numpy[
                traian[1]], points_numpy[traian[2]]
            p12 = np.linalg.norm(p1 - p2)
            p23 = np.linalg.norm(p2 - p3)
            p13 = np.linalg.norm(p1 - p3)
            angle1 = np.degrees(
                np.arccos(np.dot(p1 - p2, p1 - p3) / (p12 * p13)))
            if angle1 > 180:
                angle1 = 360 - angle1
            angle2 = np.degrees(
                np.arccos(np.dot(p1 - p2, p2 - p3) / (p12 * p23)))
            if angle2 > 180:
                angle2 = 360 - angle2
            angle3 = np.degrees(
                np.arccos(np.dot(p2 - p3, p1 - p3) / (p23 * p13)))
            if angle3 > 180:
                angle3 = 360 - angle3
            print(angle1)
            print(angle2)
            print(angle3)
            angles.append(angle1)
            angles.append(angle2)
            angles.append(angle3)
            sum_angles.append(angle3 + angle2 + angle1)
            sum_absolute.append(
                np.abs(angle3) + np.abs(angle2) + np.abs(angle1))
        savePoints(points, cells, enterPoints, exitPoints, boundPoints,
                   freePoints, enterIndx, exitIndx, boundIndx, freeIndx,
                   directory, id)
        an = np.array(angles)
        print(an[np.argmin(an)])
        plt.hist(angles, 30)
        plt.show()
        plt.hist(sum_angles, 30)
        plt.show()
        plt.hist(sum_absolute, 30)
        plt.show()
        return traingles_id, points_numpy

    def get_characteristic(self, d_list):
        # generate the and retrieve all the data
        (points, cells, _, _, _, pList) = mesh(
            self._width, self._lsList, d_list, self._epsilon, self._lcar)

        # group the point in as we need them in Matlab script
        (enterPoints, exitPoints, boundPoints, freePoints,
         enterIndx, exitIndx, boundIndx, freeIndx) = group_points(
             points, pList, self._lsList, self._width)

        # each thread saves the file for matlab script with own id to prevent races
        id = current_thread().getName()
        directory = './MatlabGen/Siatka/'

        # save the data to files in the 'directory'
        savePoints(points, cells, enterPoints, exitPoints, boundPoints,
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
        self.charac1, self.charac2, self.freq = self.get_characteristic(d_list)
        minimum1, minumum2 = self.get_local_minimums(self.charac1, self.freq)
        return minimum1, minumum2

    def print_characteristic(self):
        """
        Print the recent characteristic
        """
        if self.charac1 or self.charac2 is None:
            raise ValueError("You didnt computed characteristic yet")
        plt.plot(self.freq / 1e-9, self.c1[0], 'r')
        plt.plot(self.freq / 1e-9, self.c2[0], 'b')
        plt.show()

    def goal_function(self, d13, d2):
        """
        Compute the goal function sum(f1_target - f1) + sum(f2_target-f2)
        The f1_target and f2_target are created only one at the creation
        of the object, the recent f1 and f2 are stored as members.
        """
        if self.f1_target is None or self.f2_target is None:
            raise ValueError("You didnt specified d_list nor f_target")
        self.f1, self.f2 = self.compute_f(d13, d2)
        score = np.sum(
            np.absolute(self.f1_target - self.f1) +
            np.absolute(self.f2_target - self.f2))
        return score
