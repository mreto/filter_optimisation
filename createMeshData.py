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

d_arguments = namedtuple("d_arguments", ['d13', 'd2'])


def get_characteristic(width, lsList, dList, epsilon, lcar):

    # generate the and retrieve all the data
    (points, cells, _, _, _, pList) = mesh(width, lsList, dList, epsilon, lcar)

    # group the point in as we need them in Matlab script
    (enterPoints, exitPoints, boundPoints, freePoints, enterIndx, exitIndx,
     boundIndx, freeIndx) = group_points(points, pList, lsList, width)

    # each thread saves the file for matlab script with own id to prevent races
    id = current_thread().getName()
    directory = './MatlabGen/Siatka/'

    # save the data to files in the 'directory'
    savePoints(points, cells, enterPoints, exitPoints, boundPoints, freePoints,
               enterIndx, exitIndx, boundIndx, freeIndx, directory, id)

    # run the matlab script 'main' with the id as an arrgument
    matlab_procces = Popen(["octave", "--eval", "main('" + id + "')"],
                           cwd="./MatlabGen")
    matlab_procces.wait()

    # retrieve the data from the matlab script
    y1 = np.genfromtxt("./MatlabGen/" + id + "_y1.csv", delimiter=',')
    y2 = np.genfromtxt("./MatlabGen/" + id + "_y2.csv", delimiter=',')
    f = np.genfromtxt("./MatlabGen/" + id + "_f.csv", delimiter=',')
    return y1, y2, f


def create_graph_paralel(data, dvariable, lock_dict, dict, lock_counter,
                         counter, max_iteration):

    (width, lsList, epsilon, lcar, x1, x2) = data
    for (d13, d2) in dvariable:
        d_tuple = d_arguments(d13=d13, d2=d2)
        dList = [d13, d2, d13]
        with lock_counter:
            counter.value = counter.value + 1
            print("iteracja numer :(%d / %d)" % (counter.value, max_iteration))
        y1_mod, y2_mod, freq = get_characteristic(width, lsList, dList,
                                                  epsilon, lcar)
        # for now we don't use the y2_mod but our goal function will proboably
        # change
        x1_mod, x2_mod = get_local_maxims(y1_mod)

        # out current goal function
        score = np.sum(np.absolute(x1 - x1_mod) + np.absolute(x2 - x2_mod))

        with lock_dict:
            dict[d_tuple] = (score, y1, y2)


def get_local_maxims(f1):
    # make it smooth
    # I think maybe we should think if this works heh
    # gota find a way

    # we should make sure that there only two local maximums
    # i didnt check it, just assumed that there are

    y1_smooth = savgol_filter(f1, 5, 3)
    mask = np.diff(np.diff(y1_smooth[0])) > 0
    val_max = freq[np.argwhere(mask == True).flatten() + 1]
    x1_mod = val_max[0]
    x2_mod = val_max[1]
    return x1_mod, x2_mod


if __name__ == "__main__":

    iteration = 1

    # get arguments for all the characteristic
    width = 6.4
    lsList = [6.4, 3.2, 3.2, 6.4]
    epsilon = 0.01
    lcar = 0.3

    # create arguments for x1, x2
    d_tuple = d_arguments(3.4, 2.7)
    dList = [d_tuple.d13, d_tuple.d2, d_tuple.d13]

    y1, y2, freq = get_characteristic(width, lsList, dList, epsilon, lcar)
    x1, x2 = get_local_maxims(y1)

    # pack data to use it parallely
    data = (width, lsList, epsilon, lcar, x1, x2)

    # plt.plot(freq / 1e-9, y1[0], 'r')
    # plt.plot(freq / 1e-9, y2[0], 'b')
    # plt.show()

    # prepare meshgrid of graph
    d13_array = np.linspace(2.0, 5.0, iteration)
    d13_array = np.append(d13_array, d_tuple.d13)
    d13_array.sort()
    d2_array = np.linspace(2.3, 5.5, iteration)
    d2_array = np.append(d2_array, d_tuple.d2)
    d2_array.sort()
    D13, D2 = np.meshgrid(d13_array, d2_array)

    max_iteration = (iteration + 1)**2

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

    # create threads and count the graph
    for worker in range(worker_number):
        thread = Thread(
            target=create_graph_paralel,
            args=(data, tuples[indx[worker]:indx[worker + 1]], lock_dictionary,
                  dict, lock_counter, i, max_iteration))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    # save dict to next session
    save_obj(dict, '_f')

    # assign scores to grids in order to  the graph
    S = np.zeros_like(D13)
    d = dict.copy()
    for key, value in d.items():
        (score, y1, y2) = value
        S[(D13 == key.d13) & (D2 == key.d2)] = score

    # show the graph
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(D13, D2, S)
    plt.show()
