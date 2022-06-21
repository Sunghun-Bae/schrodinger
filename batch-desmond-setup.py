import sys
import os
import re
import argparse

multisim = "{}/utilities/multisim".format(os.environ["SCHRODINGER"])

desmond_setup_msj = """task {
  task = "desmond:auto"
}
build_geometry {
  add_counterion = {
     ion = K
     number = neutralize_system
  }
  box = {
     shape = orthorhombic
     size = [10.0 10.0 10.0 ]
     size_type = buffer
  }
  membrane_box = {
     lipid = POPC
     size = [10.0 10.0 10.0 ]
  }
  override_forcefield = S-OPLS
  rezero_system = true
  salt = {
     concentration = 0.15
     negative_ion = Cl
     positive_ion = K
  }
  solvent = SPC
}
assign_forcefield {
  forcefield = S-OPLS
}
"""

conc_ = re.compile(r'concentration = [.0-9]+')
#print(conc_.search(desmond_setup_msj))

dist_ = re.compile(r'size = \[[.0-9]+\s+[.0-9]+\s+[.0-9]+\s+\]')
#print(dist_.search(desmond_setup_msj))

ion_ = re.compile(r'ion = [a-zA-Z]+')
#print(ion_.search(desmond_setup_msj))

neg_ = re.compile(r'negative_ion = [a-zA-Z]+')
#print(neg_.search(desmond_setup_msj))

pos_ = re.compile(r'positive_ion = [a-zA-Z]+')
#print(pos_.search(desmond_setup_msj))

solvent_ = re.compile(r'solvent = [a-zA-Z0-9]+')
# print(solvent_.search(desmond_setup_msj))

lipid_ = re.compile(r'lipid = [a-zA-Z]+')
# print(lipid_.search(desmond_setup_msj))

membrane_box_ = re.compile(r'membrane_box = {.*?}\n\s+', re.DOTALL) 
# by putting '?', we get the smallest match, i.e. just the membrane_box block
# print(membrane_box_.search(desmond_setup_msj))
# print(membrane_box_.sub('', desmond_setup_msj))
rezero_system_ = re.compile(r'rezero_system = [a-zA-Z]+')
override_forcefield_ = re.compile(r'override_forcefield = [-a-zA-Z0-9]+')
forcefield_ = re.compile(r'forcefield = [-a-zA-Z0-9]+')
# print(override_forcefield_.search(desmond_setup_msj))
# print(forcefield_.search(desmond_setup_msj))

parser = argparse.ArgumentParser(description="batch gdesmond md system setup",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-c','--conc', dest="conc", type=float, default=0.15, help="salt concentration in M")
parser.add_argument('-d','--dist', dest="dist", type=float, default=10.0, help="buffer distance in A")
parser.add_argument('-l','--lipid',  dest="lipid", default="", help="lipid bilayer")
parser.add_argument('--cpp', dest="cpp", default=False, action="store_true", help="CPP simulation setup")
parser.add_argument('-s','--solvent',  dest="solvent", default="SPC", help="solvent model")
parser.add_argument('-i','--counterion',  dest="counterion", default="K", help="neutralizing ion")
parser.add_argument('-n','--negative', dest="neg", default="Cl", help="negative salt ion")
parser.add_argument('-p','--positive', dest="pos", default="K", help="positive salt ion")
parser.add_argument('-f','--forcefield', dest="forcefield", default="S-OPLS", help="forcefield")
parser.add_argument('-j','--jobfile', dest="job_file", default="desmond_setup_1.sh", help="job filename")
parser.add_argument('-m','--msjfile', dest="msj_file", default="desmond_setup_1.msj", help="msj filename")
parser.add_argument('-a','--appendix', dest="appendix", default="", help="job name appendix")
parser.add_argument('mae', nargs="+", help="desmond mae file")
args = parser.parse_args()

if args.appendix:
    msj_file = args.msj_file[:-4] + "_" + args.appendix + ".msj"
else:
    msj_file = args.msj_file

if args.appendix:
    job_file = args.job_file[:-3] + "_" + args.appendix + ".sh"
else:
    job_file = args.job_file

# job file (.sh) and msj file (.msj) should match
while os.path.exists(job_file):
    splited = job_file.replace(".sh","").split("_")
    splited[-1] = str(int(splited[-1]) + 1)
    job_file = "_".join(splited) + ".sh"

while os.path.exists(msj_file):
    splited = msj_file.replace(".msj","").split("_")
    splited[-1] = str(int(splited[-1]) + 1)
    msj_file = "_".join(splited) + ".msj"

with open(msj_file, "w") as msj:
    desmond_setup_msj = solvent_.sub(f"solvent = {args.solvent}", desmond_setup_msj)
    desmond_setup_msj = ion_.sub(f"ion = {args.counterion}", desmond_setup_msj)
    desmond_setup_msj = conc_.sub(f"concentration = {args.conc}", desmond_setup_msj)
    desmond_setup_msj = dist_.sub(f"size = [ {args.dist} {args.dist} {args.dist} ]", desmond_setup_msj)
    desmond_setup_msj = neg_.sub(f"negative_ion = {args.neg}", desmond_setup_msj)
    desmond_setup_msj = pos_.sub(f"positive_ion = {args.pos}", desmond_setup_msj)
    
    if args.cpp:
        desmond_setup_msj = rezero_system_.sub(f"rezero_system = False", desmond_setup_msj)
        args.lipid = "POPC"
    
    if args.lipid:
        desmond_setup_msj = lipid_.sub(f"lipid = {args.lipid}", desmond_setup_msj)
    else:
        # remove membrane_box block
        desmond_setup_msj = membrane_box_.sub("", desmond_setup_msj)
    
    desmond_setup_msj = override_forcefield_.sub(f"override_forcefield = {args.forcefield}", desmond_setup_msj)
    desmond_setup_msj = forcefield_.sub(f"forcefield = {args.forcefield}", desmond_setup_msj)
    msj.write(desmond_setup_msj)


with open("README","a") as readme, open(job_file,"w") as job:
    readme.write(f"Force Field   = {args.forcefield}\n")
    readme.write(f"Solvent       = {args.solvent}\n")
    readme.write(f"Counter Ion   = {args.counterion}\n")
    readme.write(f"Positive Ion  = {args.pos}\n")
    readme.write(f"Negative Ion  = {args.neg}\n")
    readme.write(f"Concentration = {args.conc} (M)\n")
    readme.write(f"Size          = {args.dist} (A)\n")
    readme.write(f"Lipid         = {args.lipid}\n")
    readme.write(f"msjfile       = {msj_file}\n")
    readme.write(f"Jobfile       = {job_file}\n")
    readme.write(f"Input structure(s):\n")

    for i, infile in enumerate(args.mae):
        prefix = os.path.basename(infile).split(".")[0]
        job_name = f"desmond_setup-{prefix}"
        if args.appendix:
            job_name += f"-{args.appendix}"
        cms_file = f"{job_name}-out.cms"
        job.write(f"if [ ! -f {cms_file} ]\n")
        job.write(f"then\n")
        job.write(f"{multisim} \\\n")
        job.write(f"  -JOBNAME {job_name} \\\n")
        job.write(f"  -m {msj_file} {os.path.abspath(infile)} \\\n") 
        job.write(f"  -o {cms_file} \\\n")
        job.write(f"  -HOST localhost:20 -maxjob 20 -WAIT\n")
        job.write(f"fi\n")
        readme.write(f"[{i+1:02d}] {infile}\n")
    readme.write("\n\n")

os.chmod(job_file, 0o777)
