import numpy

from .._io.output import Output, read
from ..mesh import read as read_mesh

__all__ = [
    "extract",
]


def extract(argv=None):
    import os

    parser = _get_parser()
    args = parser.parse_args(argv)

    # Check that TOUGH output and MESH file exist
    if not os.path.isfile(args.infile):
        raise ValueError("TOUGH output file '{}' not found.".format(args.infile))
    if not os.path.isfile(args.mesh):
        raise ValueError("MESH file '{}' not found.".format(args.mesh))

    # Read MESH and extract X, Y and Z
    parameters = read_mesh(args.mesh, file_format="tough")
    if "elements" not in parameters.keys():
        raise ValueError("Invalid MESH file '{}'.".format(args.mesh))
    else:
        nodes = {k: v["center"] for k, v in parameters["elements"].items()}

    # Read TOUGH output file
    out = read(args.infile)
    if sorted(nodes.keys()) != sorted(out[0].labels):
        raise ValueError("Elements in '{}' and '{}' are not consistent.".format(args.infile, args.mesh))

    # Write TOUGH3 element output file
    headers = ["X", "Y", "Z"]
    if not args.split or len(out) == 1:
        with open(args.output_file, "w") as f:
            _write_header(f, headers, out[0])
            for data in out:
                _write_table(f, data, nodes)
    else:
        head, ext = os.path.splitext(args.output_file)
        for i, data in enumerate(out):
            with open("{}_{}{}".format(head, i + 1, ext), "w") as f:
                _write_header(f, headers, data)
                _write_table(f, data, nodes)


def _get_parser():
    import argparse

    # Initialize parser
    parser = argparse.ArgumentParser(
        description=(
            "Extract results from TOUGH main output file and reformat as a TOUGH3 element output file."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Input file
    parser.add_argument(
        "infile", type=str, help="TOUGH output file",
    )

    # Mesh file
    parser.add_argument(
        "mesh", type=str, help="TOUGH MESH file (can be INFILE)",
    )

    # Output file
    parser.add_argument(
        "--output-file",
        "-o",
        type=str,
        default="OUTPUT_ELEME.csv",
        help="TOUGH3 element output file",
    )

    # Split or not
    parser.add_argument(
        "--split",
        "-s",
        default=False,
        action="store_true",
        help="write one file per time step",
    )

    return parser


def _write_table(f, data, nodes):
    # Write time step
    f.write('"TIME [sec]  {:.8e}"\n'.format(data.time))

    # Loop over elements
    formats = ['"{:>18}"'] + (len(data.data.keys()) + 3) * ["  {:>.12e}"]
    for i, label in enumerate(data.labels):
        record = [label] + nodes[label] + [v[i] for v in data.data.values()]
        record = ",".join(fmt.format(rec) for fmt, rec in zip(formats, record)) + "\n"
        f.write(record)


def _write_header(f, headers, data):
    headers = ["ELEM"] + headers + list(data.data.keys())
    units = [""] + 3 * ["(M)"] + len(data.data.keys()) * ["(-)"]
    f.write(",".join('"{:>18}"'.format(header) for header in headers) + "\n")
    f.write(",".join('"{:>18}"'.format(unit) for unit in units) + "\n")
