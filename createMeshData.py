import pygmsh
import os
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from functools import reduce
import math
import matplotlib.pyplot as plt
from subprocess import Popen
from random import random
import pickle
from threading import Thread, Lock, current_thread
from collections import namedtuple
from multiprocessing import Manager
from scipy.signal import savgol_filter

d_arguments = namedtuple("d_arguments", ['d13', 'd2'])


def save_obj(obj, name):
    with open('./stored_objects/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open('./stored_objects/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


def siatka(w, l_list, d_list, epsilon, lcar):
    geom = pygmsh.built_in.Geometry()
    # I draw separatly the top line and the bottom line than reverse the top
    # line and merge to with bottom line to create closed polygon
    x = 0.0
    # first two points
    list_top = [[0.0, w, 0.0]]
    list_down = [[0.0, 0.0, 0.0]]
    for l, d in zip(l_list, d_list):
        x += l
        length = (w - d) / 2

        list_down.append([x, 0.0, 0.0])
        list_down.append([x, length, 0.0])
        list_down.append([x + epsilon, length, 0.0])
        list_down.append([x + epsilon, 0.0, 0.0])

        list_top.append([x, w, 0.0])
        list_top.append([x, w - length, 0.0])
        list_top.append([x + epsilon, w - length, 0.0])
        list_top.append([x + epsilon, w, 0.0])

    # there will be one more element in l_list than in d_list
    # so need to add the last one
    x += l_list[-1]
    list_down.append([x, 0.0, 0.0])
    list_top.append([x, w, 0.0])
    list_top.reverse()
    geom.add_polygon(list_down + list_top, lcar=lcar)  #0.25 is quite decent
    geom.add_raw_code('Mesh.Algorithm=3;')
    if os.name == 'posix':
        points, cells, point_data, cell_data, field_data = pygmsh.generate_mesh(
            geom)
    else:
        points, cells, point_data, cell_data, field_data = pygmsh.generate_mesh(
            geom,
            gmsh_path=
            'C:\\Users\\Asus\\Downloads\\gmsh-3.0.6-Windows64\\gmsh-3.0.6-Windows64\\gmsh.exe'
        )
    return (points, cells, point_data, cell_data, field_data,
            list_down + list_top)


def distance(pointA, pointB):
    return reduce((lambda x, y: x + y),
                  map((lambda x: (x[0] - x[1])**2), zip(pointA,
                                                        pointB)))**(1 / 2)


def check(pointsList, point):
    firstPoint = pointsList[0]

    for nexPoint in pointsList[1:]:
        if (math.isclose(
                distance(firstPoint, point) + distance(point, nexPoint),
                distance(firstPoint, nexPoint),
                rel_tol=1e-6)):
            return True
        firstPoint = nexPoint
    return False


def groupPoints(points, pList, l_list, width):
    enterPoints = []
    exitPoints = []
    boundPoints = []
    freePoints = []

    enterIndx = []
    exitIndx = []
    boundIndx = []
    freeIndx = []

    index = 0

    for point in points:
        if point[0] == 0 and point[1] != 0 and point[1] != width:
            enterPoints.append(point)
            enterIndx.append(index)
        elif point[0] == sum(l_list) and point[1] != 0 and point[1] != width:
            exitPoints.append(point)
            exitIndx.append(index)
        elif check(pList, point):
            boundPoints.append(point)
            boundIndx.append(index)
        else:
            freePoints.append(point)
            freeIndx.append(index)
        index += 1

    return (enterPoints, exitPoints, boundPoints, freePoints, enterIndx,
            exitIndx, boundIndx, freeIndx)


def savePoints(variablesToSave,
               names_files=[
                   'points', 'cells', 'point_data', 'cell_data', 'field_data',
                   'pList'
               ],
               directory=''):

    assert (len(variablesToSave) == len(names_files))
    for variable, name in zip(variablesToSave, names_files):
        file = open(directory + name + ".txt", "w")
        for point in variable:
            file.write("%s %s" % (point[0], point[1]))
        file.write("\n")


def get_characteristic(width, lsList, dList, epsilon, lcar):

    import meshio
    (points, cells, point_data, cell_data, field_data, pList) = siatka(
        width, lsList, dList, epsilon, lcar)

    print("Number of points:")
    print(len(points))
    print("Number of triangles:")
    print(len(cells['triangle']))

    (enterPoints, exitPoints, boundPoints, freePoints, enterIndx, exitIndx,
     boundIndx, freeIndx) = groupPoints(points, pList, lsList, width)

    meshio.write_points_cells('testz.vtk', points, cells)

    id = current_thread().getName()
    directory = './MatlabGen/Siatka/'

    file = open(directory + id + "_points.txt", "w")
    for point in points:
        for coord in point:
            file.write("%s " % coord)
        file.write("\n")

    file = open(directory + id + "_trian.txt", "w")
    for trian in cells['triangle']:
        for point in trian:
            file.write("%s " % point)
        file.write("\n")

    file = open(directory + id + "_enter.txt", "w")
    for point in enterPoints:
        for coord in point:
            file.write("%s " % coord)
        file.write("\n")

    file = open(directory + id + "_exit.txt", "w")
    for point in exitPoints:
        for coord in point:
            file.write("%s " % coord)
        file.write("\n")

    file = open(directory + id + "_bound.txt", "w")
    for point in boundPoints:
        for coord in point:
            file.write("%s " % coord)
        file.write("\n")

    file = open(directory + id + "_free.txt", "w")
    for point in freePoints:
        for coord in point:
            file.write("%s " % coord)
        file.write("\n")

    file = open(directory + id + "_enterIndx.txt", "w")
    for point in enterIndx:
        file.write("%s" % point)
        file.write("\n")

    file = open(directory + id + "_exitIndx.txt", "w")
    for point in exitIndx:
        file.write("%s" % point)
        file.write("\n")

    file = open(directory + id + "_boundIndx.txt", "w")
    for point in boundIndx:
        file.write("%s" % point)
        file.write("\n")

    file = open(directory + id + "_freeIndx.txt", "w")
    for point in freeIndx:
        file.write("%s" % point)
        file.write("\n")

    matlab_procces = Popen(
        ["octave", "--eval", "main('" + id + "')"], cwd="./MatlabGen")
    matlab_procces.wait()

    S1 = np.genfromtxt("./MatlabGen/" + id + "_S11.csv", delimiter=',')
    S2 = np.genfromtxt("./MatlabGen/" + id + "_S22.csv", delimiter=',')
    f = np.genfromtxt("./MatlabGen/" + id + "_f.csv", delimiter=',')
    return S1, S2, f


def get_characteristicc(width, lsList, dList, epsilon, lcar):
    return 10, 20, 30


def get_characteristic_paralel(data, dvariable, lock_dict, dict, lock_counter,
                               counter, max_iteration):
    (width, lsList, epsilon, lcar, f1, f2) = data
    for (d13, d2) in dvariable:
        d_tuple = d_arguments(d13=d13, d2=d2)
        dList = [d13, d2, d13]
        with lock_counter:
            counter.value = counter.value + 1
            print("iteracja numer :(%d / %d)" % (counter.value, max_iteration))
        y1, y2, _ = get_characteristic(width, lsList, dList, epsilon, lcar)

        # make it smooth
        # I think maybe we should think if this works heh
        # gota find a way

        # we should make sure that there only two local maximums
        # i didnt check it, just assumed that there are
        y1_smooth = savgol_filter(y1, 5, 3)
        mask = np.diff(np.diff(y1_smooth[0])) > 0

        val_max = freq[np.argwhere(mask == True).flatten() + 1]
        f1_mod = val_max[0]
        f2_mod = val_max[1]
        score = np.sum(np.absolute(f1 - f1_mod) + np.absolute(f2 - f2_mod))
        s.append(score)
        dict[d_tuple] = (score, y1, y2)


if __name__ == "__main__":

    import meshio

    verbose = False
    iteration = 14

    width = 6.4
    lsList = [6.4, 3.2, 3.2, 6.4]
    d_tuple = d_arguments(3.4, 2.7)
    dList = [d_tuple.d13, d_tuple.d2, d_tuple.d13]
    epsilon = 0.01
    lcar = 0.3
    y1, y2, freq = get_characteristic(width, lsList, dList, epsilon, lcar)

    # make it smooth
    # I think maybe we should check if this works heh
    # i took it from stack i have no idea how does it work
    y1_smooth = savgol_filter(y1, 5, 3)
    mask = np.diff(np.diff(y1_smooth[0])) > 0
    val_max = freq[np.argwhere(mask == True).flatten() + 1]
    f1 = val_max[0]
    f2 = val_max[1]
    data = (width, lsList, epsilon, lcar, f1, f2)

    # plt.plot(freq / 1e-9, y1_smooth[0], 'r')
    # plt.plot(freq / 1e-9, y2[0], 'b')
    # plt.show()

    d13_array = np.linspace(2.0, 5.0, iteration)
    d13_array = np.append(d13_array, d_tuple.d13)
    d13_array.sort()
    d2_array = np.linspace(2.3, 5.5, iteration)
    d2_array = np.append(d2_array, d_tuple.d2)
    d2_array.sort()

    D13, D2 = np.meshgrid(d13_array, d2_array)
    s = []
    roznica = 10
    max_iteration = (iteration + 1)**2

    worker_number = 4
    threads = []

    [(2.8, 4.2), (3.44, 2.7), (3.22, 3.45), (2.9, 4.1)]

    lock_dictionary = Lock()
    lock_counter = Lock()
    manager = Manager()
    i = manager.Value('i', 0)
    dict = manager.dict()
    tuples = list(zip(np.ravel(D13), np.ravel(D2)))
    indx = np.linspace(0, len(tuples), worker_number + 1, dtype=np.int32)
    for worker in range(worker_number):
        thread = Thread(
            target=get_characteristic_paralel,
            args=(data, tuples[indx[worker]:indx[worker + 1]], lock_dictionary,
                  dict, lock_counter, i, max_iteration))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
    save_obj(dict, '_f')
    S = np.zeros_like(D13)
    d = dict.copy()
    for key, value in d.items():
        (score, y1, y2) = value
        S[(D13 == key.d13) & (D2 == key.d2)] = score

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(D13, D2, S)
    np.savetxt('S.csv', S, delimiter=",")
    np.savetxt('D13.csv', D13, delimiter=",")
    np.savetxt('D2.csv', D2, delimiter=",")
    plt.savefig("./scores.png")
    plt.savefig("./scores.pdf")
    plt.show()
