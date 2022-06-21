import sys
import os
import re
import shutil
import random
import argparse

multisim = "{}/utilities/multisim".format(os.environ["SCHRODINGER"])

# desmond MD NPT relaxation protocol
desmond_min_msj = """task { task = "desmond:auto" }
simulate { 
    cfg_file = "desmond_min_job_1.cfg" 
    jobname = "$MASTERJOBNAME" 
    dir = "." 
    compress = "" 
}
"""



desmond_min_cfg = """backend = {
}
bigger_rclone = false
checkpt = {
   first = 0.0
   interval = 240.06
   name = "$JOBNAME.cpt"
   write_last_step = true
}
cpu = 1
cutoff_radius = 9.0
elapsed_time = 0.0
energy_group = false
eneseq = {
   first = 0.0
   interval = 1.2
   name = "$JOBNAME$[_replica$REPLICA$].ene"
}
ensemble = {
   brownie = {
      delta_max = 0.1
   }
   class = NVT
   method = Brownie
   thermostat = {
      tau = 1.0
   }
}
glue = solute
maeff_output = {
   first = inf
   interval = 120.0
   name = "$JOBNAME-out.cms"
   periodicfix = true
   trjdir = "$JOBNAME$[_replica$REPLICA$]_trj"
}
meta = false
meta_file = ?
randomize_velocity = {
   first = 0.0
   interval = inf
   seed = 2007
   temperature = "@*.temperature"
}
restrain = none
simbox = {
}
taper = false
temperature = [
   [10.0 0 ]
]
time = 100.0
timestep = [0.001 0.001 0.003 ]
trajectory = {
   center = []
   first = 0.0
   format = dtr
   frames_per_file = 250
   interval = 4.8
   name = "$JOBNAME$[_replica$REPLICA$]_trj"
   periodicfix = true
   write_velocity = false
}
"""

seed_ = re.compile(r'seed = [0-9]+')
#print(seed_.search(desmond_min_cfg))

time_ = re.compile(r'[^_]time = [.0-9]+')
#print(time_.search(desmond_min_cfg))

#interval_ = re.compile(r'[^_]@interval = [.0-9]+')
#print(time_.search(desmond_min_cfg))

cfg_  = re.compile(r'cfg_file = ["_.0-9a-zA-Z]+')
#print(seed_.search(desmond_min_msj))

parser = argparse.ArgumentParser(description="batch desmond min jobs",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-g','--gpu', dest="gpu_device", type=int, default=0, help="GPU device")
parser.add_argument('-t','--time', dest="simulation_time", type=float, default=100.0, help="simulation time in ps")
#parser.add_argument('-i','--interval', dest="interval", type=float, help="frame interval in ps")
parser.add_argument('-p','--prefix', dest="prefix", default="r", help="directory prefix")
parser.add_argument('-s','--start', dest="start", type=int, default=1, help="directory start")
parser.add_argument('-r','--repeat', dest="repeat", type=int, default=1, help="number of repeats")
parser.add_argument('-j','--jobfile', dest="job_file", default="desmond_min_job_1.sh", help="job filename")
parser.add_argument('cms', nargs="+", help="desmond cms file")
args = parser.parse_args()

try:
    cms_files = sorted([os.path.abspath(f) for f in args.cms])
    assert(len(cms_files) > 0)
except:
    print(".cms file(s) not found")
    sys.exit(0)

opt  = '-HOST localhost -maxjob 1 -cpu 1 -mode umbrella '
opt += '-set stage[1].set_family.md.jlaunch_opt=["-gpu"] -lic "DESMOND_GPGPU:16"'

#if not args.interval:
#    args.interval = args.simulation_time # it will save 1000 frames

job_file = args.job_file
while os.path.exists(job_file):
    splited = job_file.replace(".sh","").split("_")
    splited[-1] = str(int(splited[-1]) + 1)
    job_file = "_".join(splited) + ".sh"


with open("README","a") as readme, open(job_file,"w") as job:

    dirs = [ f"{args.prefix}{n:02d}" for n in range(args.start, args.start+args.repeat) ]

    print(f"Job file = {job_file}")

    readme.write("="*40+"\n")
    readme.write(f"GPU device              = {args.gpu_device}\n")
    readme.write(f"Simulation Time (ps)    = {args.simulation_time}\n")
    #readme.write(f"Trajectory interval(ps) = {args.interval}\n")
    readme.write(f"Repeat                  = {args.repeat}\n")
    readme.write( "Directory               = %s\n" % " ".join(dirs))
    readme.write(f"Jobfile                 = {job_file}\n\n")

    job.write(f'export CUDA_VISIBLE_DEVICES="{args.gpu_device}"\n\n')

    for i, infile in enumerate(cms_files):
        info = f"[{i+1}] {infile}"
        print(info)
        readme.write(info+"\n")

    for n in range(args.start, args.start+args.repeat): 
        outdir = f"{args.prefix}{n:02d}"
        outdir_abspath = os.path.abspath(outdir)
        job.write(f"cd {outdir_abspath}/\n\n")
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        cfg_file = f"{outdir}/desmond_min_job_{n:02d}.cfg"
        msj_file = f"{outdir}/desmond_min_job_{n:02d}.msj"
        cfg_file_basename= os.path.basename(cfg_file)

        with open(cfg_file,"w") as cfg:
            # modify templates
            desmond_min_cfg = seed_.sub(f"seed = {random.randint(1000,9999)}", desmond_min_cfg)
            desmond_min_cfg = time_.sub(f"\ntime = {args.simulation_time}", desmond_min_cfg)
            #desmond_min_cfg = interval_.sub(f" interval = {args.interval}", desmond_min_cfg)
            cfg.write(desmond_min_cfg)

        with open(msj_file,"w") as msj:
            # modify templates
            desmond_min_msj = cfg_.sub(f'cfg_file = "{cfg_file_basename}"', desmond_min_msj)
            msj.write(desmond_min_msj)
        
        for infile in cms_files:
            #prefix = os.path.basename(infile).replace("desmond_setup-","").replace("-out.cms","")
            prefix_ = re.sub(r'desmond_setup[-_]','', os.path.basename(infile))
            prefix  = prefix_.replace("-out.cms","")
            
            job_name = f"desmond_min_job_{n:02d}_{prefix}"
            job.write('{} -JOBNAME {} -m {} -c {} -description "{}" {} {} -o {} -WAIT\n\n'.format(
                multisim, 
                job_name, 
                os.path.basename(msj_file),
                os.path.basename(cfg_file),
                "GPU desmond MD",
                opt,
                os.path.join("..",infile),
                f"{job_name}-out.cms",
            ))

os.chmod(job_file, 0o777)
