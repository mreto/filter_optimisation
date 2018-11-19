from threading import current_thread
import matplotlib.pyplot as plt
import numpy as np
from subprocess import Popen
from mesh import mesh, group_points
from utilty import savePoints
from scipy.signal import savgol_filter


class Solver:
    def __init__(self, f1_taget=None, f2_target=None, d13=None, d2=None):
        self._width = 6.4
        self._lsList = [6.4, 3.2, 3.2, 6.4]
        self._epsilon = 0.01
        self._lcar = 0.3
        # TODO napsiac w docach co znacza te argumenty bo to jest tak srednio widoczne
        # TODO wymyslić jakies lepsze nazwy niż f2 f1, target, wymslic nazwe dobra na
        # funckje całkowitą
        if d13 and d2 is not None:
            self.f1_target, self.f2_target = self.compute_function(d13, d2)
        elif f1_taget and f2_target is not None:
            self.f1_target, self.f2_target = f1_taget, f2_target
        else:
            self.f1_target, self.f2_target = None, None

    def _get_characteristic(self, d_list):

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

    def _get_local_maxims(self, charac1, freq):
        # make it smooth
        # I think maybe we should think if this works heh
        # gota find a way

        # we should make sure that there only two local maximums
        # i didnt check it, just assumed that there are

        charac1_smooth = savgol_filter(charac1, 5, 3)
        mask = np.diff(np.diff(charac1_smooth[0])) > 0
        val_max = freq[np.argwhere(mask == True).flatten() + 1]
        f1 = val_max[0]
        f2 = val_max[1]
        return f1, f2

    def compute_function(self, d13, d2):
        d_list = [d13, d2, d13]
        self.charac1, self.charac2, self.freq = self._get_characteristic(
            d_list)
        self.f1, self.f2 = self._get_local_maxims(self.charac1, self.freq)
        return self.f1, self.f2

    def print_characteristic(self):
        plt.plot(self.f / 1e-9, self.c1[0], 'r')
        plt.plot(self.f / 1e-9, self.c2[0], 'b')
        plt.show()

    def function_complete(self, d13, d2):
        if self.f1_target and self.f2_target is not None:
            f1, f2 = self.compute_function(d13, d2)
            print("f1")
            print(f1)
            print("f2")
            print(f2)
            score = np.sum(
                np.absolute(self.f1_target - f1) +
                np.absolute(self.f2_target - f2))
            return score
