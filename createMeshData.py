import pygmsh
import os
import functools
from functools import reduce
import math


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
    geom.add_polygon(list_down + list_top, lcar=lcar)#0.25 is quite decent
    geom.add_raw_code('Mesh.Algorithm=3;')
    if os.name == 'posix':
        points, cells, point_data, cell_data, field_data = pygmsh.generate_mesh(geom )
    else:
        points, cells, point_data, cell_data, field_data = pygmsh.generate_mesh(geom ,gmsh_path='C:\\Users\\Asus\\Downloads\\gmsh-3.0.6-Windows64\\gmsh-3.0.6-Windows64\\gmsh.exe')
    return (points, cells, point_data, cell_data, field_data, list_down + list_top)

def distance(pointA, pointB):
    return reduce((lambda x,y: x+y), map((lambda x: (x[0] - x[1])**2), zip(pointA,pointB)))**(1/2)

def check(pointsList, point):
    firstPoint = pointsList[0]

    for nexPoint in pointsList[1:]:
       if(math.isclose(distance(firstPoint, point) + distance(point, nexPoint),distance(firstPoint, nexPoint),rel_tol=1e-6)):
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
        elif point[0] == sum(l_list) and point[1] != 0 and point [1] != width:
            exitPoints.append(point)
            exitIndx.append(index)
        elif check(pList,point):
            boundPoints.append(point)
            boundIndx.append(index)
        else:
            freePoints.append(point)
            freeIndx.append(index)
        index += 1

    return (enterPoints, exitPoints, boundPoints, freePoints, enterIndx, exitIndx, boundIndx, freeIndx)


if __name__ == "__main__":
    import meshio

    width = 6.4
    lsList = [6.4,3.2,3.2,6.4]
    dList = [2.8,4.2,2.8]
    epsilon = 0.01
    lcar = 0.1

    (points, cells, point_data, cell_data, field_data, pList) = siatka(width, lsList, dList, epsilon, lcar)
    print("Number of points:")
    print(len(points))
    print("Number of triangles:")
    print(len(cells['triangle']))

    (enterPoints, exitPoints, boundPoints, freePoints, enterIndx, exitIndx, boundIndx, freeIndx) = groupPoints(points, pList, lsList, width)

    print("Number of points in group 1 - enter points")
    print(len(enterPoints))
    print("Number of points in group 2 - exit points")
    print(len(exitPoints))

    print("Number of points in group 3 - bound points")
    print(len(boundPoints))
    print("Number of points in group 4 - free points")
    print(len(freePoints))

    meshio.write_points_cells('testz.vtk',points, cells)

    file = open("points.txt","w")
    for point in points:
        for coord in point:
            file.write("%s " %coord)
        file.write("\n")

    file = open("trian.txt", "w")
    for trian in cells['triangle']:
        for point in trian:
            file.write("%s " %point)
        file.write("\n")



    file = open("enter.txt", "w")
    for point in enterPoints:
        for coord in point:
            file.write("%s " %coord)
        file.write("\n")

    file = open("exit.txt","w")
    for point in exitPoints:
        for coord in point:
            file.write("%s " %coord)
        file.write("\n")

    file = open("bound.txt","w")
    for point in boundPoints:
        for coord in point:
            file.write("%s " %coord)
        file.write("\n")

    file = open("free.txt","w")
    for point in freePoints:
        for coord in point:
            file.write("%s " %coord)
        file.write("\n")




    file = open("enterIndx.txt", "w")
    for point in enterIndx:
        file.write("%s" %point)
        file.write("\n")

    file = open("exitIndx.txt","w")
    for point in exitIndx:
        file.write("%s" %point)
        file.write("\n")

    file = open("boundIndx.txt","w")
    for point in boundIndx:
        file.write("%s" %point)
        file.write("\n")

    file = open("freeIndx.txt","w")
    for point in freeIndx:
        file.write("%s" %point)
        file.write("\n")






