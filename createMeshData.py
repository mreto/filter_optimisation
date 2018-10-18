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
from multiprocessing import Manager


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

    print(id)
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
        dList = [d13, d2, d13]
        with lock_counter:
            counter.value = counter.value + 1
            print("iteracja numer :(%d / %d)" % (counter.value, max_iteration))
        f1_mod, f2_mod, _ = get_characteristic(width, lsList, dList, epsilon,
                                               lcar)
        score = np.sum(np.absolute(f1 - f1_mod) + np.absolute(f2 - f2_mod))
        s.append(score)
        dict[score] = (d13, d2)


if __name__ == "__main__":

    import meshio

    verbose = False
    iteration = 15

    width = 6.4
    lsList = [6.4, 3.2, 3.2, 6.4]
    d13 = 3.3
    d2 = 4.6
    dList = [d13, d2, d13]
    epsilon = 0.01
    lcar = 0.1
    f1, f2, freq = get_characteristic(width, lsList, dList, epsilon, lcar)
    data = (width, lsList, epsilon, lcar, f1, f2)
    # plt.plot(freq / 1e-9, f1[0], 'r')
    # plt.plot(freq / 1e-9, f2[0], 'b')
    # plt.show()

    d13_array = np.linspace(2.0, 5.0, iteration)
    d13_array = np.append(d13_array, 3.3)
    d2_array = np.linspace(3.0, 6.0, iteration)
    d2_array = np.append(d2_array, 4.6)
    D13, D2 = np.meshgrid(d13_array, d2_array)
    s = []
    roznica = 10
    max_iteration = (iteration + 1)**2

    worker_number = 3
    threads = [None for _ in range(worker_number)]

    [(2.8, 4.2), (3.44, 2.7), (3.22, 3.45), (2.9, 4.1)]

    lock_dictionary = Lock()
    lock_counter = Lock()
    manager = Manager()
    i = manager.Value('i', 0)
    dict = manager.dict()
    tuples = list(zip(np.ravel(D13), np.ravel(D2)))
    indx = np.linspace(0, len(tuples), worker_number + 1, dtype=np.int32)
    for worker in range(worker_number):
        threads[worker] = Thread(
            target=get_characteristic_paralel,
            args=(data, tuples[indx[worker]:indx[worker + 1]], lock_dictionary,
                  dict, lock_counter, i, max_iteration)).start()

    save_obj(dict, 'dic')
    S = np.zeros_like(D13)
    d = dict.copy()
    for key, value in d.items():
        (k1, k2) = value
        S[(D13 == k1) & (D2 == k2)] = key
    S[S == 0] = np.nan
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(D13, D2, S)
    np.savetxt('S.csv', S, delimiter=",")
    np.savetxt('D13.csv', D13, delimiter=",")
    np.savetxt('D2.csv', D2, delimiter=",")
    plt.savefig("./scores.png")
    plt.savefig("./scores.pdf")
    plt.show()
