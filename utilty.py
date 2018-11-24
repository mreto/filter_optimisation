import pickle
from collections import namedtuple
import numpy as np

D_tuple = namedtuple("D_tuple", ['d13', 'd2'])


def save_obj(obj, name):
    with open('./stored_objects/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open('./stored_objects/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


def savePoints(points, triangles_ids, enterPoints, exitPoints, boundPoints,
               freePoints, enterIndx, exitIndx, boundIndx, freeIndx, directory,
               id):
    file = open(directory + id + "_points.txt", "w")
    for point in points:
        for coord in point:
            file.write("%s " % coord)
        file.write("\n")

    file = open(directory + id + "_trian.txt", "w")
    for trian in triangles_ids:
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
