import sys
import os
import re
import shutil
import random
import argparse

multisim = "{}/utilities/multisim".format(os.environ["SCHRODINGER"])

# desmond MD NPT relaxation protocol
desmond_metadynamics_msj = """# Desmond standard NPT relaxation protocol
# All times are in the unit of ps.
# Energy is in the unit of kcal/mol.
task {
   task = "desmond:auto"
   set_family = {
      desmond = {
         checkpt.write_last_step = no
      }
   }
}

simulate {
   title       = "Brownian Dynamics NVT, T = 10 K, small timesteps, and restraints on solute heavy atoms, 100ps"
   annealing   = off
   time        = 100
   timestep    = [0.001 0.001 0.003 ]
   temperature = 10.0
   ensemble = {
      class = "NVT"
      method = "Brownie"
      brownie = {
         delta_max = 0.1
      }
   }
   restrain = {
      atom = "solute_heavy_atom"
      force_constant = 50.0
   }
}

simulate {
   title       = "NVT, T = 10 K, small timesteps, and restraints on solute heavy atoms, 12ps"
   annealing   = off
   time        = 12
   timestep    = [0.001 0.001 0.003]
   temperature = 10.0
   restrain    = { atom = solute_heavy_atom force_constant = 50.0 }
   ensemble    = {
      class  = NVT
      method = Berendsen
      thermostat.tau = 0.1
   }

   randomize_velocity.interval = 1.0
   eneseq.interval             = 0.3
   trajectory.center           = []
}

simulate {
   title       = "NPT, T = 10 K, and restraints on solute heavy atoms, 12ps"
   annealing   = off
   time        = 12
   temperature = 10.0
   restrain    = retain
   ensemble    = {
      class  = NPT
      method = Langevin
      thermostat.tau = 0.1
      barostat  .tau = 50.0
   }

   randomize_velocity.interval = 1.0
   eneseq.interval             = 0.3
   trajectory.center           = []
}

solvate_pocket {
   should_skip = true
   ligand_file = ?
}

simulate {
   title       = "NPT and restraints on solute heavy atoms, 12ps"
   effect_if   = [["@*.*.annealing"] 'annealing = off temperature = "@*.*.temperature[0][0]"']
   time        = 12
   restrain    = retain
   ensemble    = {
      class  = NPT
      method = Langevin
      thermostat.tau = 0.1
      barostat  .tau = 50.0
   }

   randomize_velocity.interval = 1.0
   eneseq.interval             = 0.3
   trajectory.center           = []
}

simulate {
   title       = "NPT and no restraints, 24ps"
   effect_if   = [["@*.*.annealing"] 'annealing = off temperature = "@*.*.temperature[0][0]"']
   time        = 24
   ensemble    = {
      class  = NPT
      method = Langevin
      thermostat.tau = 0.1
      barostat  .tau = 2.0
   }

   eneseq.interval   = 0.3
   trajectory.center = solute
}

simulate {
   cfg_file = "desmond_metadynamics_job_1.cfg"
   jobname  = "$MASTERJOBNAME"
   dir      = "."
   compress = ""
   meta = {
      cv = [
         {atom = ["res. UNK" "res. 849" ]
          type = dist
          wall = 40
          width = 0.05
         }
      ]
      cv_name = "$JOBNAME$[_replica$REPLICA$].cvseq"
      first = 0.0
      height = 0.03
      interval = 0.09
      name = "$JOBNAME$[_replica$REPLICA$].kerseq"
   }
   backend ={
      # set cvseq interval to trajectory output
      force.term.ES.interval = '@*.*.*.*.trajectory.interval'
   }
   checkpt.write_last_step = yes
}
"""


# desmond MD production protocol
desmond_metadynamics_cfg = """annealing = false
backend = {
}
bigger_rclone = false
checkpt = {
   first = 0.0
   interval = 200.0
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
   barostat = {
      tau = 2.0
   }
   class = NPT
   method = MTK
   thermostat = {
      tau = 1.0
   }
}
glue = solute
maeff_output = {
   first = 0.0
   interval = 120.0
   name = "$JOBNAME$[_replica$REPLICA$]-out.cms"
   periodicfix = true
   trjdir = "$JOBNAME$[_replica$REPLICA$]_trj"
}
meta_file = ?
pressure = [1.01325 isotropic ]
randomize_velocity = {
   first = 0.0
   interval = inf
   seed = 2967
   temperature = "@*.temperature"
}
restrain = none
simbox = {
   first = 0.0
   interval = 1.2
   name = "$JOBNAME$[_replica$REPLICA$]_simbox.dat"
}
surface_tension = 0.0
taper = false
temperature = [
   [300.0 0 ]
]
time = 600.0
timestep = [0.002 0.002 0.006 ]
trajectory = {
   center = []
   first = 0.0
   format = dtr
   frames_per_file = 250
   @interval = 50.0
   name = "$JOBNAME$[_replica$REPLICA$]_trj"
   periodicfix = true
   write_velocity = false
}
"""

seed_ = re.compile(r'seed = [0-9]+')
#print(seed_.search(desmond_md_cfg))

time_ = re.compile(r'[^_]time = [.0-9]+')
#print(time_.search(desmond_md_cfg))

interval_ = re.compile(r'[^_]@interval = [.0-9]+')
#print(time_.search(desmond_md_cfg))

cfg_  = re.compile(r'cfg_file = ["_.0-9a-zA-Z]+')
#print(seed_.search(desmond_md_msj))

parser = argparse.ArgumentParser(description="Repeat MD jobs with different seed number",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-g','--gpu', dest="gpu_device", type=int, default=0, help="gpu device id")
parser.add_argument('-r','--repeat', dest="repeat", type=int, default=1, help="number of repeats")
parser.add_argument('-j','--jobfile', dest="job_file", default="desmond_md_job_1.sh", help="job filename")
parser.add_argument('job', help="template desmond job name")
args = parser.parse_args()

prefix = "_".join(args.job.split("_")[:3])
job_start = int(args.job.split("_")[-1])+1

opt  = '-HOST localhost -maxjob 1 -cpu 1 -mode umbrella -lic DESMOND_GPGPU:16'

job_file = args.job_file
while os.path.exists(job_file):
    splited = job_file.replace(".sh","").split("_")
    splited[-1] = str(int(splited[-1]) + 1)
    job_file = "_".join(splited) + ".sh"

with open(job_file,"w") as job:
    job.write(f'export CUDA_VISIBLE_DEVICES="{args.gpu_device}"\n\n')
    for n in range(job_start, job_start+args.repeat):
        job_name = f"{prefix}_{n:02d}"
        out_cfg_file = f"{job_name}.cfg"
        out_msj_file = f"{job_name}.msj"
        out_cms_file = f"{job_name}-out.cms"

        with open(args.job+".cfg","r") as f:
            desmond_md_cfg = "".join(f.readlines())
        with open(out_cfg_file,"w") as cfg:
            desmond_md_cfg = seed_.sub(f"seed = {random.randint(1000,9999)}", desmond_md_cfg)
            cfg.write(desmond_md_cfg)

        with open(args.job+".msj","r") as f:
            desmond_md_msj = "".join(f.readlines())
        with open(out_msj_file,"w") as msj:
            desmond_md_msj = cfg_.sub(f'cfg_file = "{out_cfg_file}"', desmond_md_msj)
            msj.write(desmond_md_msj)
        
        job.write('{} -JOBNAME {} -m {} -c {} -description "{}" {} {} -o {} -WAIT\n\n'.format(
            multisim, 
            job_name, 
            os.path.basename(out_msj_file),
            os.path.basename(out_cfg_file),
            "GPU desmond MD",
            opt,
            os.path.join(args.job+".cms"),
            f"{job_name}-out.cms",
        ))

os.chmod(job_file, 0o777)
