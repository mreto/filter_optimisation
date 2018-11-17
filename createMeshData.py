from mesh import mesh, group_points
from utilty import savePoints, save_obj
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from subprocess import Popen
from threading import Thread, Lock, current_thread
from collections import namedtuple
from multiprocessing import Manager
from scipy.signal import savgol_filter
from solver import Solver

D_tuple = namedtuple("D_tuple", ['d13', 'd2'])


def create_graph_paralel(data, dvariable):
    (x1, x2, lock_dict, dict, lock_counter, iteration, max_iteration) = data

    solver = Solver()
    for (d13, d2) in dvariable:
        with lock_counter:
            iteration.value = iteration.value + 1
            print(
                "iteracja numer :(%d / %d)" % (iteration.value, max_iteration))

        x1_mod, x2_mod = solver.compute_function(d13, d2)

        # out current goal function
        score = np.sum(np.absolute(x1 - x1_mod) + np.absolute(x2 - x2_mod))
        d_tuple = D_tuple(d13, d2)
        with lock_dict:
            dict[d_tuple] = (score)


def create_graph():
    solver = Solver()
    d13 = 3.4
    d2 = 2.7
    x1, x2 = solver.compute_function(3.4, 2.7)

    iteration = 10
    max_iteration = (iteration + 1)**2

    # prepare meshgrid of graph
    d13_array = np.linspace(2.0, 5.0, iteration)
    d13_array = np.append(d13_array, d13)
    d13_array.sort()
    d2_array = np.linspace(2.3, 5.5, iteration)
    d2_array = np.append(d2_array, d2)
    d2_array.sort()
    D13, D2 = np.meshgrid(d13_array, d2_array)

    # prepare threading
    worker_number = 3
    threads = []
    lock_dictionary = Lock()
    lock_counter = Lock()
    manager = Manager()
    i = manager.Value('i', 0)
    dict = manager.dict()

    # divide meshgrid to threads
    tuples = list(zip(np.ravel(D13), np.ravel(D2)))
    indx = np.linspace(0, len(tuples), worker_number + 1, dtype=np.int32)
    data = (x1, x2, lock_dictionary, dict, lock_counter, i, max_iteration)
    # create threads and count the graph
    for worker in range(worker_number):
        thread = Thread(
            target=create_graph_paralel,
            args=(data, tuples[indx[worker]:indx[worker + 1]]))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    # save dict to next session
    save_obj(dict, '_f')

    # assign scores to grids in order to  the graph
    S = np.zeros_like(D13)
    d = dict.copy()
    save_obj(d, '_dicto')
    for key, value in d.items():
        (score) = value
        S[(D13 == key.d13) & (D2 == key.d2)] = score

    # show the graph
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(D13, D2, S)
    plt.show()
    return d


if __name__ == "__main__":
    create_graph()



