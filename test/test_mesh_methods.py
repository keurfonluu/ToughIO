import numpy

import toughio


def test_extrude_to_3d():
    # Create 2D mesh
    dx = numpy.random.rand(10)
    dy = numpy.random.rand(5)
    mesh_ref = toughio.meshmaker.structured_grid(dx, dy)
    mesh_ref.point_data["points"] = numpy.random.rand(mesh_ref.n_points)
    mesh_ref.cell_data["cells"] = numpy.random.rand(mesh_ref.n_cells)

    # Extrude mesh to 3D
    mesh = mesh_ref.extrude_to_3d(numpy.random.rand(5), axis=2, inplace=False)

    assert mesh.n_points == 6 * mesh_ref.n_points
    assert mesh.n_cells == 5 * mesh_ref.n_cells
    assert mesh.point_data["points"].size == 6 * mesh_ref.n_points
    assert mesh.cell_data["cells"].size == 5 * mesh_ref.n_cells

    for v in mesh.point_data["points"].reshape((6, mesh.n_points // 6)):
        assert numpy.allclose(mesh_ref.point_data["points"], v)

    for v in mesh.cell_data["cells"].reshape((5, mesh.n_cells // 5)):
        assert numpy.allclose(mesh_ref.cell_data["cells"], v)


def test_prune_duplicates():
    # Create mesh with duplicate points and cells
    points = numpy.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 1.0],
            [1.0, 1.0, 1.0],
            [0.0, 1.0, 1.0],
            [2.0, 0.0, 0.0],
            [2.0, 1.0, 0.0],
            [2.0, 0.0, 1.0],
            [2.0, 1.0, 1.0],
            [2.5, 0.5, 0.5],
            [2.5, 0.5, 0.5],
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 1.0],
            [1.0, 1.0, 1.0],
            [0.0, 1.0, 1.0],
        ]
    )
    cells = [
        ("tetra", numpy.array([[8, 12, 9, 10], [10, 13, 9, 11]])),
        (
            "wedge",
            numpy.array(
                [[1, 10, 5, 2, 11, 6], [1, 10, 5, 2, 11, 6], [1, 8, 10, 2, 9, 11]]
            ),
        ),
        (
            "hexahedron",
            numpy.array([[0, 1, 2, 3, 4, 5, 6, 7], [14, 15, 16, 17, 18, 19, 20, 21]]),
        ),
    ]
    mesh = toughio.Mesh(points, cells)
    mesh.point_data["points"] = numpy.random.rand(mesh.n_points)
    mesh.cell_data["cells"] = numpy.random.rand(mesh.n_cells)

    # Remove duplicate points and cells
    mesh.prune_duplicates()

    assert mesh.n_points == 13
    assert mesh.n_cells == 5
    assert mesh.point_data["points"].size == 13
    assert mesh.cell_data["cells"].size == 5