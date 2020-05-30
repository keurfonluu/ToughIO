import os
from copy import deepcopy

import numpy
import pytest

import helpers
import toughio

output_ref = {
    "element": {
        0: {"PRES": 9641264.130638, "TEMP": 149.62999493,},
        -1: {"PRES": 635804.12294844, "TEMP": 142.89449866,},
    },
    "connection": {
        0: {"HEAT": -1.64908253e-07, "FLOW": -2.85760551e-13,},
        -1: {"HEAT": -5.54750914e-08, "FLOW": -4.68234504e-14,},
    },
}


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


@pytest.mark.parametrize(
    "mesh_ref, from_, to_",
    [
        (helpers.tet_mesh, toughio.from_meshio, "to_meshio"),
        (helpers.tet_mesh, toughio.from_pyvista, "to_pyvista"),
        (helpers.hex_mesh, toughio.from_meshio, "to_meshio"),
        (helpers.hex_mesh, toughio.from_pyvista, "to_pyvista"),
    ],
)
def test_from_to(mesh_ref, from_, to_):
    mesh = from_(getattr(mesh_ref, to_)())

    helpers.allclose_mesh(mesh_ref, mesh)


def test_to_tough():
    with pytest.deprecated_call():
        helpers.hybrid_mesh.to_tough(helpers.tempdir("MESH"))


@pytest.mark.parametrize(
    "filename, file_type, time_step",
    [
        ("OUTPUT_ELEME.csv", "element", 0),
        ("OUTPUT_ELEME.csv", "element", -1),
        ("OUTPUT_CONNE.csv", "connection", 0),
        ("OUTPUT_CONNE.csv", "connection", -1),
    ],
)
def test_read_output(filename, file_type, time_step):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    mesh_filename = os.path.join(this_dir, "support_files", "outputs", "mesh.pickle")
    mesh = toughio.read_mesh(mesh_filename)
    filename = os.path.join(this_dir, "support_files", "outputs", filename)
    mesh.read_output(filename, time_step=time_step)

    for k, v in output_ref[file_type][time_step].items():
        assert numpy.allclose(v, mesh.cell_data[k].mean())


def test_add_point_data():
    mesh = deepcopy(helpers.hybrid_mesh)
    data = numpy.random.rand(mesh.n_points)
    mesh.add_point_data("a", data)

    assert numpy.allclose(data, mesh.point_data["a"])


def test_add_cell_data():
    mesh = deepcopy(helpers.hybrid_mesh)
    data = numpy.random.rand(mesh.n_cells)
    mesh.add_cell_data("a", data)

    assert numpy.allclose(data, mesh.cell_data["a"])


def test_set_material():
    dx = numpy.ones(10)
    dy = numpy.ones(10)
    dz = numpy.ones(10)
    mesh = toughio.meshmaker.structured_grid(dx, dy, dz, origin=numpy.zeros(3))
    mesh.set_material("test", xlim=(4.0, 6.0), ylim=(4.0, 6.0), zlim=(4.0, 6.0))

    assert (mesh.materials == "test").sum() == 8


def test_near():
    dx = numpy.ones(3)
    dy = numpy.ones(3)
    dz = numpy.ones(3)
    mesh = toughio.meshmaker.structured_grid(dx, dy, dz, origin=numpy.zeros(3))

    assert mesh.near((1.5, 1.5, 1.5)) == 13
