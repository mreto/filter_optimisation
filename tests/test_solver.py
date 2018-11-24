import sys
import pytest
sys.path.insert(1, '.')
import solver
import numpy as np


def test_fx_the_cx_point():
    s = solver.Solver(f1_target=0, f2_target=0)
    # The point that is at point of translation should move
    # by h so the scale should be 1
    assert s.fx(2, 3, 1, 2) == 1


def test_fx_point_border():
    s = solver.Solver(f1_target=0, f2_target=0)
    # The point that is at the border of range should not move
    assert s.fx(3, 3, 1, 2) == 0


def test_yx_the_cx_point():
    s = solver.Solver(f1_target=0, f2_target=0)
    # The point that is at point of translation should move
    # by h so the scale should be 1
    assert s.fy(2, 3, 1, 2) == 1


def test_yx_point_border():
    s = solver.Solver(f1_target=0, f2_target=0)
    # The point that is at the border of range should not move
    assert s.fy(3, 3, 1, 2) == 0


def test_y():
    s = solver.Solver(f1_target=0, f2_target=0)
    assert s.fy(1, 2, 0, 1) == 1


def test_deform_squere_4_trangles():
    s = solver.Solver(f1_target=0, f2_target=0)
    # make the max y and x = 2
    s._lslist = [1, 1]
    s._width = 2
    points = np.array([[0, 0], [2, 0], [2, 2], [0, 2], [1, 1]])
    triangles_id = [[0, 1, 4], [1, 2, 4], [2, 3, 4], [0, 4, 3]]

    # the point in which we change the geometry of the filter
    xc, yc = 1, 1

    # move of the architecture e.g h in computing derivative
    h = 0.001

    new_points = s.deform(triangles_id, points, xc, yc, h)

    # the points on border stay the same, only the middle
    # point change by the amout of h
    correct_points = np.array([[0, 0], [2, 0], [2, 2], [0, 2], [1, 1.001]])
    assert ((new_points == correct_points).all())


def test_deform_squere_4_trangles_yc_point_smaller():
    s = solver.Solver(f1_target=0, f2_target=0)
    # make the max y and x = 2
    s._lslist = [1, 1]
    s._width = 2
    points = np.array([[0, 0], [2, 0], [2, 2], [0, 2], [1, 1]])
    triangles_id = [[0, 1, 4], [1, 2, 4], [2, 3, 4], [0, 4, 3]]

    # the point in which we change the geometry of the filter
    xc, yc = 1, 0.5

    # move of the architecture e.g h in computing derivative
    h = 0.001

    new_points = s.deform(triangles_id, points, xc, yc, h)

    # the points on border stay the same, only the middle
    # point change by the amout of h
    correct_points = np.array([[0, 0], [2, 0], [2, 2], [0, 2]])
    assert ((new_points[:-1, :] == correct_points).all())

    # the y in last point should move less than in the
    # test_deform_squere_4_trangles():
    assert (new_points[-1, 0] == 1)
    assert (new_points[-1, 1] > 1)
    assert (new_points[-1, 1] < 1.001)


def test_get_triangle_angles_right_triangle_case():
    triangles_ids = np.array([[0, 1, 2]])
    points = np.array([[0, 0], [1, 0], [0, 1]])
    s = solver.Solver(f1_target=0, f2_target=0)
    v = s.get_triangles_angles(triangles_ids, points)
    # Two angles are 45 deegrees
    assert (v[4] == 2)
    # One angle is 90 deegree
    assert (v[9] == 1)


def test_get_triangle_angles_triangle_case_21_34_123():
    triangles_ids = np.array([[0, 1, 2]])

    points = np.array([[0, 0], [1.70535, 0], [0.61477, 0.43046]])
    s = solver.Solver(f1_target=0, f2_target=0)
    v = s.get_triangles_angles(triangles_ids, points)
    # One degree is 21
    assert (v[2] == 1)
    # One degree is 34
    assert (v[3] == 1)
    # One angle is 123 deegree
    assert (v[12] == 1)


def test_check_how_visualy_looks_deformated_with_normal():
    assert (1 == 0)


def test_write_test_to_every_fucikin_function():
    assert (1 == 0)
