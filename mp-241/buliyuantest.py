from ase import Atoms
from ase.io import read

def main():
    # Hardcoded XYZ file content
    xyz_content = """3
    XYZ file example
    H  0.0  0.0  0.0
    O  0.0  0.0  1.0
    H  0.0  1.0  0.0
    """

    # Create a temporary file and write the XYZ content to it
    with open('POSCAR.xyz', 'w') as f:
        f.write(xyz_content)

    try:
        # Use the read function to read the atomic structure from the temporary file
        atoms = read('POSCAR.xyz')

        # Set periodic boundary conditions and cell vectors explicitly
        atoms.set_pbc(True)
        atoms.set_cell([[10.0, 0.0, 0.0],
                        [0.0, 10.0, 0.0],
                        [0.0, 0.0, 10.0]])

        # Print some information about the read structure
        print("Number of atoms:", len(atoms))
        print("Cell vectors:")
        print(atoms.get_cell())
        print("Atomic positions:")
        print(atoms.get_positions())

        # Calculate and print bandpath information
        bandpath = atoms.cell.bandpath()
        print("Bandpath:")
        print(bandpath)
        print("Special points:")
        print(bandpath.special_points)

        bandpath.plot()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Remove the temporary file
        import os
        os.remove('temp.xyz')

if __name__ == "__main__":
    main()
