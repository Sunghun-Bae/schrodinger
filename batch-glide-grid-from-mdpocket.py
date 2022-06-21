import glob
import os
import numpy as np

mdpocket_selected = "../mdpout_freq_iso_0_2_inside.pdb"
xyz = []
with open(mdpocket_selected,"r") as pdbfile:
    for line in pdbfile:
        if line.startswith("HETATM") or line.startswith("ATOM"):
            x = float(line[30:38].strip())
            y = float(line[38:46].strip())
            z = float(line[46:54].strip())
            xyz.append([x,y,z])
    coor = np.array(xyz, float)
    center = np.mean(coor, 0)
    print("grid center=", center)

for infile in sorted(glob.glob("*.maegz")):
    name = os.path.basename(infile).replace(".maegz","")
    with open(f"glide-grid/glide-grid_{name}.in","w") as outfile:
        outfile.write(f"GRID_CENTER  {center[0]}, {center[1]}, {center[2]}\n")
        outfile.write(f"GRIDFILE     glide-grid_{name}.zip\n")
        outfile.write(f"INNERBOX     10,10,10\n")
        outfile.write(f"OUTERBOX     30,30,30\n")
        outfile.write(f"RECEP_FILE   ../{name}.maegz\n")

    with open(f"glide-grid/glide-grid_{name}.sh","w") as outfile:
        outfile.write("${SCHRODINGER}/glide glide-grid_"+f"{name}.in -OVERWRITE -HOST localhost -TMPLAUNCHDIR")


