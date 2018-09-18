import pygmsh
import os
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from functools import reduce
import math
import matplotlib.pyplot as plt
from subprocess import Popen
from random import random


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

    (points, cells, point_data, cell_data, field_data, pList) = siatka(
        width, lsList, dList, epsilon, lcar)
    if verbose:
        print("Number of points:")
        print(len(points))
        print("Number of triangles:")
        print(len(cells['triangle']))

    (enterPoints, exitPoints, boundPoints, freePoints, enterIndx, exitIndx,
     boundIndx, freeIndx) = groupPoints(points, pList, lsList, width)

    if verbose:
        print("Number of points in group 1 - enter points")
        print(len(enterPoints))
        print("Number of points in group 2 - exit points")
        print(len(exitPoints))
        print("Number of points in group 3 - bound points")
        print(len(boundPoints))
        print("Number of points in group 4 - free points")
        print(len(freePoints))

    meshio.write_points_cells('testz.vtk', points, cells)

    directory = './MatlabGen/Siatka/'

    file = open(directory + "points.txt", "w")
    for point in points:
        for coord in point:
            file.write("%s " % coord)
        file.write("\n")

    file = open(directory + "trian.txt", "w")
    for trian in cells['triangle']:
        for point in trian:
            file.write("%s " % point)
        file.write("\n")

    file = open(directory + "enter.txt", "w")
    for point in enterPoints:
        for coord in point:
            file.write("%s " % coord)
        file.write("\n")

    file = open(directory + "exit.txt", "w")
    for point in exitPoints:
        for coord in point:
            file.write("%s " % coord)
        file.write("\n")

    file = open(directory + "bound.txt", "w")
    for point in boundPoints:
        for coord in point:
            file.write("%s " % coord)
        file.write("\n")

    file = open(directory + "free.txt", "w")
    for point in freePoints:
        for coord in point:
            file.write("%s " % coord)
        file.write("\n")

    file = open(directory + "enterIndx.txt", "w")
    for point in enterIndx:
        file.write("%s" % point)
        file.write("\n")

    file = open(directory + "exitIndx.txt", "w")
    for point in exitIndx:
        file.write("%s" % point)
        file.write("\n")

    file = open(directory + "boundIndx.txt", "w")
    for point in boundIndx:
        file.write("%s" % point)
        file.write("\n")

    file = open(directory + "freeIndx.txt", "w")
    for point in freeIndx:
        file.write("%s" % point)
        file.write("\n")

    matlab_procces = Popen(["octave", "main.m"], cwd="./MatlabGen")
    matlab_procces.wait()

    S1 = np.genfromtxt("./MatlabGen/S11.csv", delimiter=',')
    S2 = np.genfromtxt("./MatlabGen/S22.csv", delimiter=',')
    f = np.genfromtxt("./MatlabGen/f.csv", delimiter=',')
    return S1, S2, f


def get_characteristicc(width, lsList, dList, epsilon, lcar):
    return 10, 20, 30


if __name__ == "__main__":

    import meshio

    verbose = False
    iteration = 13

    width = 6.4
    lsList = [6.4, 3.2, 3.2, 6.4]
    d13 = 3.3
    d2 = 4.6
    dList = [d13, d2, d13]
    epsilon = 0.01
    lcar = 0.1

    f1, f2, freq = get_characteristic(width, lsList, dList, epsilon, lcar)
    np.zeros(iteration)
    # plt.plot(freq / 1e-9, f1[0], 'r')
    # plt.plot(freq / 1e-9, f2[0], 'b')
    # plt.show()

    # d13_array = 3.3 + (np.random.rand(iteration, 1) - 0.5) * 3.4
    d13_array = np.linspace(2.0, 5.0, iteration)
    # d2_array = 4.6 + (np.random.rand(iteration, 1) - 0.5) * 3.4
    d2_array = np.linspace(3.0, 6.0, iteration)
    D13, D2 = np.meshgrid(d13_array, d2_array)
    s = []
    i = 0
    for d13, d2 in zip(np.ravel(D13), np.ravel(D2)):
        print("iteracja numer :(%d / %d)" % (i, iteration * iteration))
        i += 1
        dList = [d13, d2, d13]
        f1_mod, f2_mod, _ = get_characteristic(width, lsList, dList, epsilon,
                                               lcar)
        s.append(np.sum(np.absolute(f1 - f1_mod) + np.absolute(f2 - f2_mod)))
        if i % 5 == 0:
            np.savetxt("scores.csv", np.array(s), delimiter=",")

    S = np.array(s).reshape(D13.shape)
    np.savetxt("D13.csv", D13, delimiter=",")
    np.savetxt("D2.csv", D2, delimiter=",")
    np.savetxt("S.csv", S, delimiter=",")
    np.savetxt("D13_a.csv", d13_array, delimiter=",")
    np.savetxt("D2_a.csv", d2_array, delimiter=",")
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(D13, D2, S)
    plt.savefig("./scores.png")
    plt.savefig("./scores.pdf")
    # plt.show()
