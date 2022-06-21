import os
import sys
import argparse
import subprocess


from schrodinger.application.desmond.packages import topo, traj, traj_util
run = os.environ["SCHRODINGER"]+"/run"

excluded_residues = ["POPC", "SPC", "TIP3P", "TIP4P", "NA", "K", "CL"]

parser = argparse.ArgumentParser(description="batch gdesmond md jobs",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-p','--protein', dest="protein", default="", help="protein ASL")
parser.add_argument('-l','--ligand', dest="ligand", default="", help="ligand ASL")
parser.add_argument('cms', nargs="+", help="...-out.cms file")
args = parser.parse_args()

# ex. md_1/r00/desmond_md_job_00_md2_m_naloxone-out.cms
# mandatory input
if not args.cms :
    parser.print_help()
    sys.exit(0)

# provide options if protein and ligand ASL are not given
if not (args.protein and args.ligand):
    ASL_choice = []
    protein_asl_index = None
    ligand_asl_index = None

    # read .cms and its associated trajectory file: <jobname>-out.cms, <jobname>_trj
    input_cms = args.cms[0]
    try:
        (msys_model, cms_model, trj) = traj_util.read_cms_and_traj(input_cms)
    except:
        (msys_model, cms_model) = topo.read_cms(input_cms)
        try:
            trj_path = topo.find_traj_path(cms_model)  # or
        except:
            try:
                trj_path = topo.find_traj_path_from_cms_path(input_cms)
            except:
                trj_path = input_cms.replace("-out.cms","_trj")
        trj = traj.read_traj(trj_path)
        
    print()
    print("Title:", cms_model.title)
    print("Excluded residues:", ",".join(excluded_residues))
    print()
    
    # chain based ASL choices
    for chain in cms_model.chain:
        # r and s for the first and last residues
        for r in chain.residue:
            break
        res = [ s for s in chain.residue if s.molecule_number == r.molecule_number ]
        s = res[-1]
        if chain.name.strip() :
            ASL_choice.append((
                f"mol. {r.molecule_number} and chain. {chain.name}",
                f"{len(res):6d} residues ({r.pdbres}{r.resnum}...{s.pdbres}{s.resnum})",
                ))
        else: # if chain.name is blank
            ASL_choice.append((
                f"mol. {r.molecule_number}",
                f"{len(res):6d} residues ({r.pdbres}{r.resnum}...{s.pdbres}{s.resnum})",
                ))

    # molecule based ASL choices
    for molecule in cms_model.molecule:
        r = None # first residue
        s = None # last residue
        for s in molecule.residue:
            if not r:
                r = s
            pass
        if r.pdbres.strip() in excluded_residues :
            continue
        ASL_choice.append((
            f"mol. {molecule.number}",
            f"{len(molecule.residue):6d} residues ({r.pdbres}{r.resnum}...{s.pdbres}{s.resnum})",
            ))

    # sort by ASL expression text
    ASL_choice = sorted(ASL_choice)
    ASL_choice.append(("none", ""))

    # show choices
    for idx, (asl, info) in enumerate(ASL_choice):
        print(f"[{idx:2d}] {asl:20s} {info}")
        # default
        if asl == "mol. 1" :
            protein_asl_index = idx
        if asl == "mol. 2" :
            ligand_asl_index = idx

    # wait for user input
    print()
    ret = input(f'Enter protein of interest [{protein_asl_index:2d}]: ')
    if ret:
        protein_asl_index = int(ret)
    print(f"  -prot {ASL_choice[protein_asl_index][0]}")
    ret = input(f'Enter ligand  of interest [{ligand_asl_index:2d}]: ')
    if ret:
        ligand_asl_index = int(ret)
    print(f"  -lig {ASL_choice[ligand_asl_index][0]}")

    # set protein and ligand ASL
    args.protein = ASL_choice[protein_asl_index][0]
    args.ligand = ASL_choice[ligand_asl_index][0]


for cms_file in args.cms :
    cms_base = os.path.basename(cms_file).replace("-out.cms","")
    cms_prefix = cms_file[:-8]
    trj_dir  = f"{cms_prefix}_trj"
    name = cms_base.replace("desmond_md_job_","")

    subprocess.run([run,"event_analysis.py", "analyze",
        cms_file, 
        "-prot", args.protein, 
        "-lig", args.ligand, 
        "-out", f"{name}", 
        ])

    subprocess.run([run,"analyze_simulation.py", 
        cms_file, 
        trj_dir,
        f"{name}-out.eaf",
        f"{name}-in.eaf",
        ])

    subprocess.run([run,"event_analysis.py", "report",
        "-pdf", 
        f"report_{name}.pdf",
        f"{name}-out.eaf",
        ])
