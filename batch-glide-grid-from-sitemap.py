import glob
import os
import numpy as np

tryout = {
    "m-0178":"1",
    "m-0293":"3",
    "m-0576":"3",
    "m-0704":"2",
    "m-0752":"3",
    "m-0770":"1",
    "m-0839":"2",
    "m-0849":"2",
    "m-0876":"3",
    "m-0877":"1",
    "m-0944":"1",
    "m-1226":"1",
    "m-1360":"4",
    "m-1586":"1",
    "m-1654":"1",
    "m-1666":"1",
    "m-1700":"1",
    "m-2748":"1",
    "m-2893":"1",
    "m-2964":"1",
    "m-2974":"1",
}

for infile in sorted(glob.glob("sitemap/*_volpts.pdb")):
    c = os.path.basename(infile).split("_")
    rec, site = c[0], c[2]
    
    if not (rec in tryout and site == tryout[rec]) :
        continue

    with open(infile,"r") as pdbfile:
        xyz = []
        for line in pdbfile:
            if line.startswith("HETATM") or line.startswith("ATOM"):
                x = float(line[30:38].strip())
                y = float(line[38:46].strip())
                z = float(line[46:54].strip())
                xyz.append([x,y,z])
        
        coor = np.array(xyz, float)
        size_x = np.max(xyz[0])-np.min(xyz[0])
        size_y = np.max(xyz[1])-np.min(xyz[1])
        size_z = np.max(xyz[2])-np.min(xyz[2])
        center = np.mean(coor, 0)
        
        print(rec, site, center, f"{size_x:4.1f} {size_y:4.1f} {size_z:4.1f}")
        
        with open(f"glide-grid/glide-grid_{rec}_{site}.in","w") as outfile:
            outfile.write(f"GRID_CENTER  {center[0]}, {center[1]}, {center[2]}\n")
            outfile.write(f"GRIDFILE     glide-grid_{rec}_{site}.zip\n")
            outfile.write(f"INNERBOX     10,10,10\n")
            outfile.write(f"OUTERBOX     {size_x:.1f}, {size_y:.1f}, {size_z:.1f}\n")
            outfile.write(f"RECEP_FILE   ../{rec}.maegz\n")

        with open(f"glide-grid/glide-grid_{rec}_{site}.sh","w") as outfile:
            outfile.write("${SCHRODINGER}/glide glide-grid_"+f"{rec}_{site}.in -OVERWRITE -HOST localhost -TMPLAUNCHDIR")


