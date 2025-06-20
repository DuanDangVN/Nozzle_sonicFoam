import numpy as np
cell_z = 0.05
# Define file path
filename = "blockMeshDict.txt"
# Parameters
x_start = 0.0
x_throat = 1.5
x_end = 2.25
n_points_conv = 300
n_points_div = 200

# Define top wall curve function
def y_wall(x):
    return np.sqrt((1 + 2.2 * (x - 1.5) ** 2) / np.pi)

# Create interpolation points for spline edges
x_converge = np.linspace(x_start, x_throat, n_points_conv)
x_diverge = np.linspace(x_throat, x_end, n_points_div)[1:]

curve_converge = [(x, y_wall(x), 0) for x in x_converge]
curve_diverge = [(x, y_wall(x), 0) for x in x_diverge]

curve_converge_z1 = [(x, y, cell_z) for (x, y, z) in curve_converge]
curve_diverge_z1 = [(x, y, cell_z) for (x, y, z) in curve_diverge]

# Corner points
verts = [
    (0, 0, 0),        # 0
    (0, y_wall(0), 0),  # 1
    (1.5, 0, 0),      # 2
    (1.5, y_wall(1.5), 0),  # 3
    (2.25, 0, 0),     # 4
    (2.25, y_wall(2.25), 0),  # 5

    (0, 0, cell_z),        # 6
    (0, y_wall(0), cell_z),  # 7
    (1.5, 0, cell_z),      # 8
    (1.5, y_wall(1.5), cell_z),  # 9
    (2.25, 0, cell_z),     # 10
    (2.25, y_wall(2.25), cell_z),  # 11
]

def vector_str(v): return f"({v[0]:.4f} {v[1]:.4f} {v[2]:.4f})"

with open(filename, "w") as f:
    f.write("""FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}

convertToMeters 1;

vertices
(
""")
    for v in verts:
        f.write(f"    {vector_str(v)}\n")
    f.write(");\n\n")

    f.write("""blocks
(
    hex (0 2 3 1 6 8 9 7) (300 100 1) simpleGrading (2 1 1)
    hex (2 4 5 3 8 10 11 9) (200 100 1) simpleGrading (1 1 1)
);\n\n""")

    f.write("edges\n(\n")

    def spline_block(start, end, points):
        f.write(f"    spline {start} {end}\n    (\n")
        for pt in points:
            f.write(f"        {vector_str(pt)}\n")
        f.write("    )\n")

    spline_block(1, 3, curve_converge)
    spline_block(3, 5, curve_diverge)
    spline_block(7, 9, curve_converge_z1)
    spline_block(9, 11, curve_diverge_z1)

    f.write(");\n\n")

    f.write("""boundary
(
    inlet
    {
        type patch;
        faces
        (
            (0 1 7 6)
        );
    }

    outlet
    {
        type patch;
        faces
        (
            (4 5 11 10)
        );
    }

    bottom
    {
        type symmetryPlane;
        faces
        (
            (0 2 8 6)
            (2 4 10 8)
        );
    }

    top
    {
        type wall;
        faces
        (
            (1 3 9 7)
            (3 5 11 9)
        );
    }

    frontAndBack
    {
        type empty;
        faces
        (
            (0 2 3 1)
            (2 4 5 3)
            (6 8 9 7)
            (8 10 11 9)
        );
    }
);

mergePatchPairs ();
""")

print(f"✅ blockMeshDict successfully written to: {filename}")
