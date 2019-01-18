from functools import reduce
import math
import os
import pygmsh


def mesh(w, l_list, d_list, epsilon, lcar):
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
    geom.add_raw_code('Mesh.Algorithm = 6;')
    # geom.add_raw_code('Mesh.AllowSwapAngle = 15;')
    geom.add_raw_code('Mesh.Smoothing = 0;')
    # geom.add_raw_code('Mesh.ElementOrder = 1;')

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


def group_points(points, pList, l_list, width):
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
