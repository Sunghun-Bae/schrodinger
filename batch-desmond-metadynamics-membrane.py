import sys
import os
import re
import shutil
import random
import argparse

multisim = "{}/utilities/multisim".format(os.environ["SCHRODINGER"])

desmond_cfg = """annealing = false
backend = {
}
bigger_rclone = false
box = ?
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
   center_atoms = solute
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
   write_last_vel = false
   write_velocity = false
}
"""

desmond_msj = """task {
  set_family = {
     desmond = {
        checkpt = {
           write_last_step = false
        }
     }
     simulate = {
        temperature = "300.0"
     }
  }
  task = "desmond:auto"
}

simulate {
  annealing = false
  backend = {
     mdsim = {
        plugin = {
           maeff_output = {
              nocenter = true
           }
        }
     }
  }
  ensemble = {
     brownie = {
        delta_max = 0.1
     }
     class = NVT
     method = Brownie
  }
  restraints = {
     new = [
        {atoms = solute
         force_constants = 50.0
         name = posre_harm
        }
     ]
  }
  temperature = 10.0
  time = 50
  timestep = [0.001 0.001 0.003 ]
  title = "Brownian Dynamics NVT, T = 10 K, small timesteps, and restraints on solute heavy atoms, 100ps"
}

simulate {
  backend = {
     force = {
        term = {
           GaussianForce = {
              A = [10.0 10.0 ]
              grp_energy = [1 1 ]
              mu = [-10.0 10.0 ]
              sigma = [0.5 0.5 ]
              type = GaussianForce
           }
           list = [GaussianForce ]
        }
     }
     mdsim = {
        plugin = {
           maeff_output = {
              nocenter = true
           }
        }
     }
  }
  ensemble = {
     barostat = {
        tau = 0.5
     }
     brownie = {
        delta_max = 0.5
     }
     class = NPT
     method = Brownie
     thermostat = {
        tau = 0.5
     }
  }
  pressure = 1000
  restraints = {
     new = [
        {atoms = "asl: (membrane ) AND NOT ((atom.ele H))"
         force_constants = [0.0 0.0 5.0 ]
         name = posre_harm
        }

        {atoms = solute_heavy_atom
         force_constants = 20.0
         name = posre_harm
        }
     ]
  }
  temperature = 100
  time = 20
  timestep = [0.002 0.002 0.004 ]
  title = "100 K, H2O Barrier, Browninan NPT, membrane restrained in z, protein restrained"
}

simulate {
  backend = {
     force = {
        term = {
           GaussianForce = {
              A = [10.0 10.0 ]
              grp_energy = [1 1 ]
              mu = [-10.0 10.0 ]
              sigma = [0.5 0.5 ]
              type = GaussianForce
           }
           list = [GaussianForce ]
        }
     }
     mdsim = {
        plugin = {
           maeff_output = {
              nocenter = true
           }
        }
     }
  }
  ensemble = {
     barostat = {
        tau = 2.0
     }
     class = NPgT
     method = MTK
     thermostat = {
        tau = 1.0
     }
  }
  pressure = 1000
  restraints = {
     new = [
        {atoms = "asl: (membrane and atom.ele P,N)"
         force_constants = [0.0 0.0 2.0 ]
         name = posre_harm
        }

        {atoms = solute_heavy_atom
         force_constants = 10.0
         name = posre_harm
        }
     ]
  }
  temperature = 100
  time = 100
  timestep = [0.002 0.002 0.004 ]
  title = "100 K, H2O Barrier, NPgT, membrane restrained in z, protein restrained"
}

simulate {
  annealing = true
  backend = {
     force = {
        term = {
           GaussianForce = {
              A = [2.0 ]
              grp_energy = [1 ]
              mu = [0.0 ]
              sigma = [5 ]
              type = GaussianForce
           }
           list = [GaussianForce ]
        }
     }
     integrator = {
        Multigrator = {
           barostat = {
              temperature = ?
           }
        }
     }
     mdsim = {
        plugin = {
           anneal = {
              interval = 0.09
           }
           list = ["!append!" posre_schedule ]
           maeff_output = {
              nocenter = true
           }
           posre_schedule = {
              schedule = {
                 time = [0 60 100 ]
                 value = [1.0 0.2 0.2 ]
              }
              type = posre_schedule
           }
        }
     }
  }
  ensemble = {
     barostat = {
        tau = 2.0
     }
     class = NPgT
     method = MTK
     thermostat = {
        tau = 0.1
     }
  }
  pressure = 100
  restraints = {
     new = [
        {atoms = "asl: (membrane and atom.ele P,N)"
         force_constants = [0.0 0.0 2.0 ]
         name = posre_harm
        }

        {atoms = solute_heavy_atom
         force_constants = 10.0
         name = posre_harm
        }
     ]
  }
  temperature = [
     [100 0 ]
     [200 100 ]
     [300 150 ]
  ]
  time = 150
  timestep = [0.002 0.002 0.004 ]
  title = "NPgT, Heating from 100 -> 300 K, H2O Barrier and gradual release of restrain"
}

simulate {
  ensemble = {
     class = NVT
     method = NH
     thermostat = {
        tau = 1
     }
  }
  restraints = {
     new = [
        {atoms = "asl: ((backbone or ligand) and not a.e H)"
         force_constants = 5.0
         name = posre_harm
        }
     ]
  }
  temperature = 300
  time = 50
  title = "NVT production remove all restraints"
}

simulate {
  ensemble = {
     class = NVT
     method = NH
     thermostat = {
        tau = 1
     }
  }
  temperature = "300.0"
  time = 50
  title = "NVT production remove all restraints"
}

simulate {
  backend = {
     force = {
        term = {
           ES = {
              interval = "@*.*.*.*.trajectory.interval"
           }
        }
     }
  }
  cfg_file = "____________.cfg"
  checkpt = {
     write_last_step = true
  }
  compress = ""
  dir = "."
  jobname = "$MASTERJOBNAME"
  meta = {
     cv = [
        {atom = ["res. UNK"]
         type = zdist
         width = 0.05
        }
     ]
     cv_name = "$JOBNAME$[_replica$REPLICA$].cvseq"
     first = 0.0
     height = 0.03
     interval = 0.09
     name = "$JOBNAME$[_replica$REPLICA$].kerseq"
  }
}


analysis {
    meta = { }
    dir = "."
    compress = ""
}
"""

# Job launching command:
# $SCHRODINGER/utilities/multisim \
#     -HOST localhost \
#     -maxjob 1 \
#     -cpu 1 \
#     -mode umbrella \
#     -lic DESMOND_GPGPU:16 \
#     -m CPP9_01.msj \
#     -c CPP9_01.cfg \
#     -JOBNAME CPP9_01 \
#     -description Metadynamics \
#     -o CPP9_01-out.cms \
#     CPP9_01.cms

seed_ = re.compile(r'seed = [0-9]+')
time_ = re.compile(r'[^_]time = [.0-9]+')
interval_ = re.compile(r'[^_]@interval = [.0-9]+')
cfg_  = re.compile(r'cfg_file = ["_.0-9a-zA-Z]+')

parser = argparse.ArgumentParser(description="batch gdesmond metadynamics jobs",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-g','--gpu', dest="gpu_device", type=int, default=0, help="gpu device id")
parser.add_argument('-t','--time', dest="simulation_time", type=float, default=100.0, help="simulation time in ns")
parser.add_argument('-i','--interval', dest="interval", type=float, help="frame interval in ps")
parser.add_argument('-p','--prefix', dest="prefix", default="metad", help="directory prefix")
parser.add_argument('-s','--start', dest="start", type=int, default=1, help="directory start")
parser.add_argument('-r','--repeat', dest="repeat", type=int, default=1, help="number of repeats")
parser.add_argument('-j','--jobfile', dest="job_file", default="desmond_metadynamics_job_1.sh", help="job filename")
parser.add_argument('cms', nargs="+", help="desmond cms file")
args = parser.parse_args()

try:
    cms_files = [os.path.abspath(f) for f in args.cms]
    assert(len(cms_files) > 0)
except:
    print(".cms file(s) not found")
    sys.exit(0)

opt = '-HOST localhost -maxjob 1 -cpu 1 -mode umbrella -lic "DESMOND_GPGPU:16" -description "metadynamics"'

if not args.interval:
    args.interval = args.simulation_time # it will save 1000 frames

job_file = args.job_file
while os.path.exists(job_file):
    splited = job_file.replace(".sh","").split("_")
    splited[-1] = str(int(splited[-1]) + 1)
    job_file = "_".join(splited) + ".sh"


with open("README","a") as readme, open(job_file,"w") as job:
    print(f"Job file = {job_file}")

    readme.write("="*40+"\n")
    readme.write(f"GPU device= {args.gpu_device}\n")
    readme.write(f"Time(ns)= {args.simulation_time}\n")
    readme.write(f"Trajectory interval(ps)= {args.interval}\n")
    readme.write(f"Repeat= {args.repeat}\n")
    readme.write(f"Jobfile= {job_file}\n\n")
    
    job.write(f'export CUDA_VISIBLE_DEVICES="{args.gpu_device}"\n\n')

    for i, infile in enumerate(cms_files):
        info = f"[{i+1}] {infile}"
        print(info)
        readme.write(info+"\n")
    dirs = [ f"{args.prefix}{n:02d}" for n in range(args.start, args.start+args.repeat) ]
    readme.write("directory = %s\n" % " ".join(dirs))
    readme.write("="*40+"\n\n")

    for n in range(args.start, args.start+args.repeat): 
        outdir = f"{args.prefix}{n:02d}"
        outdir_abspath = os.path.abspath(outdir)
        job.write(f"cd {outdir_abspath}/\n\n")
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        cfg_file = f"{outdir}/desmond_metadynamics_job_{n:02d}.cfg"
        msj_file = f"{outdir}/desmond_metadynamics_job_{n:02d}.msj"
        cfg_file_basename= os.path.basename(cfg_file)

        with open(cfg_file,"w") as cfg:
            # modify templates
            desmond_cfg = seed_.sub(f"seed = {random.randint(1000,9999)}", desmond_cfg)
            desmond_cfg = time_.sub(f"\ntime = {args.simulation_time*1000.}", desmond_cfg)
            desmond_cfg = interval_.sub(f" interval = {args.interval}", desmond_cfg)
            cfg.write(desmond_cfg)

        with open(msj_file,"w") as msj:
            # modify templates
            desmond_msj = cfg_.sub(f'cfg_file = "{cfg_file_basename}"', desmond_msj)
            msj.write(desmond_msj)
        
        for infile in cms_files:
            prefix_ = re.sub(r'desmond_setup[-_]','', os.path.basename(infile))
            prefix  = prefix_.replace("-out.cms","")
            
            job_name = f"desmond_metadynamics_job_{n:02d}_{prefix}"
            job.write('{} -JOBNAME {} -m {} -c {} {} {} -o {} -WAIT\n\n'.format(
                multisim, 
                job_name, 
                os.path.basename(msj_file),
                os.path.basename(cfg_file),
                opt,
                os.path.join("..",infile),
                f"{job_name}-out.cms",
            ))

os.chmod(job_file, 0o777)
