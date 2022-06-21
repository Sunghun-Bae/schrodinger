import sys
import os
import re
import shutil
import random
import argparse


"""
Parsing Desmond .msj and .cfg Ark format Syntax
===============================================

Ark uses a free format syntax, in that is there are no indentation or alignment requirements. 
Spaces (including some control characters, e.g., tab, return, new line.) are useful 
only for separating keys and values. The Ark format syntax is case-sensitive, 
so keys and values with different capitalization patterns are treated as distinct.

At the most basic level the syntax is the familiar key-value pair syntax of the form:
   key = value 
where key must be a non-empty string, and value must be one of the following 
three objects: atom, list, and map. A value of the atom type is one of the following: 
integer, floating number, string, boolean 
(true, false, yes, no, on, off are recognized as boolean values), or none (? is recognized as none). 
A value of the list of type is of the form: 
   [ value1 value2 ... ], 
in other words a list of one or more values wrapped within brackets [ ], 
and the elements value1, value2, ... are values of any type and are separated by spaces. 
Map type values generally look like:
   { key1 = value1
   key2 = value2
   ...
   }
where the value is wrapped with braces { }, and elements in the map are key-value pairs.

The form describe above is the canonical form of the syntax. 
Here is an example of this syntax with nested values:
a = {
    b = {
        c = [1 2 4]
    }
    d = string_value
}
Ark also supports the so-called “pathname” syntax, where nested keys are separated by a period. 
The pathname equivalent of the canonical example given above is:

a.b.c = [1 2 4]
a.d = string_value
"""

import pyparsing as pp
from pyparsing import pyparsing_common as ppc

EQ, LBRACKET, RBRACKET, LBRACE, RBRACE = map(pp.Suppress, "=[]{}")
variable = pp.Word(pp.alphanums + "._@")
string1  = pp.Word(pp.alphanums + "._/?@")
string2  = pp.quotedString() # OR pp.quotedString().setParseAction(pp.removeQuotes)
number   = ppc.number()
elements = pp.delimitedList( string1 | string2 | number, delim=r'\s+')
array    = pp.Forward() # recursive
array    <<= ( LBRACKET + pp.OneOrMore( elements | array ) + RBRACKET ) | ( pp.Literal("[]") )
expr     = pp.Forward() # recursive
expr_0   = ( variable + LBRACE + pp.ZeroOrMore(expr) + RBRACE )
expr_1   = ( variable + EQ + LBRACE + pp.ZeroOrMore(expr) + RBRACE )
expr_2   = ( variable + EQ + ( string1 | string2 | number | array ) )
expr     <<= pp.OneOrMore(pp.Dict(pp.Group( expr_0 | expr_1 | expr_2 )))
expr.ignore("#" + pp.restOfLine)


multisim = "{}/utilities/multisim".format(os.environ["SCHRODINGER"])

# desmond MD NPT relaxation protocol
desmond_md_msj = """# Desmond standard NPT relaxation protocol
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
   effect_if   = [["==" "-gpu" "@*.*.jlaunch_opt[-1]"] 'ensemble.method = Langevin']
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
   effect_if   = [["==" "-gpu" "@*.*.jlaunch_opt[-1]"] 'ensemble.method = Langevin']
   annealing   = off
   time        = 12
   temperature = 10.0
   restrain    = retain
   ensemble    = {
      class  = NPT
      method = Berendsen
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
   effect_if   = [["@*.*.annealing"] 'annealing = off temperature = "@*.*.temperature[0][0]"'
                  ["==" "-gpu" "@*.*.jlaunch_opt[-1]"] 'ensemble.method = Langevin']
   time        = 12
   restrain    = retain
   ensemble    = {
      class  = NPT
      method = Berendsen
      thermostat.tau = 0.1
      barostat  .tau = 50.0
   }

   randomize_velocity.interval = 1.0
   eneseq.interval             = 0.3
   trajectory.center           = []
}

simulate {
   title       = "NPT and no restraints, 24ps"
   effect_if   = [["@*.*.annealing"] 'annealing = off temperature = "@*.*.temperature[0][0]"'
                  ["==" "-gpu" "@*.*.jlaunch_opt[-1]"] 'ensemble.method = Langevin']
   time        = 24
   ensemble    = {
      class  = NPT
      method = Berendsen
      thermostat.tau = 0.1
      barostat  .tau = 2.0
   }

   eneseq.interval   = 0.3
   trajectory.center = solute
}

simulate {
   cfg_file = "desmond_md_job.cfg"
   jobname  = "$MASTERJOBNAME"
   dir      = "."
   compress = ""
}
"""


# desmond MD production protocol
cfg_template = expr.parseString("""annealing = false
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
meta = false
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
time = 100000.0
timestep = [0.002 0.002 0.006 ]
trajectory = {
   center = []
   first = 0.0
   format = dtr
   frames_per_file = 250
   interval = 50.0
   name = "$JOBNAME$[_replica$REPLICA$]_trj"
   periodicfix = true
   write_velocity = false
}
""").asDict()


def write_formatted_cfg(d, fo, depth=0, indent=4):
    for k, v in d.items():
        spc = ' '*indent*depth
        if v :
            if isinstance(v, dict):
                fo.write(spc + k + " = {\n")
                write_formatted_cfg(v, fo, depth=depth+1, indent=indent)
                fo.write(spc + "}\n")
            else:
                if isinstance(v, list):
                    fo.write(spc + k + " = ")
                    fo.write(str(v).replace("'","").replace(",","")) # remove terminal brackets
                    fo.write("\n")
                else:
                    fo.write(spc + k + " = " + str(v) +"\n")
        else:
            fo.write(spc + k + " = {\n")
            fo.write(spc + "}\n")


msj_  = re.compile(r'cfg_file = ["_.0-9a-zA-Z]+')

parser = argparse.ArgumentParser(description="batch gdesmond md jobs",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-g', dest="gpu_device", type=int, default=0, 
                    metavar="gpu_device", help="gpu device id")

parser.add_argument('-T', dest="temp", nargs="+", type=float, default=[300.0,], 
                    metavar="temperature", help="temperature in K")

parser.add_argument('-R', dest="ramp", nargs="+", type=float, default=[10.0,],
                    metavar="tempramp", help="heat and cool ramps in ps/K")

parser.add_argument('-t', dest="simulation_time", nargs="+", type=float, default=[100.0,],
                    metavar="simulation_time", help="simulation time in ns")

parser.add_argument('-i', dest="interval", type=float, default=100.0,
                    metavar="interval", help="frame interval in ps")

parser.add_argument('-p', dest="prefix", default="r", help="directory prefix")
parser.add_argument('-s', dest="start", type=int, default=1, help="directory start")
parser.add_argument('-r', dest="repeat", type=int, default=1, help="number of repeats")
parser.add_argument('-j', dest="job_file", default="desmond_md_job_1.sh", help="job filename")

parser.add_argument('cms', nargs="+", help="desmond cms file")
args = parser.parse_args()

try:
    cms_files = [os.path.abspath(f) for f in args.cms]
    assert(len(cms_files) > 0)
except:
    print(".cms file(s) not found")
    sys.exit(0)

opt  = '-HOST localhost -maxjob 1 -cpu 1 -mode umbrella '
opt += '-set stage[1].set_family.md.jlaunch_opt=["-gpu"] -lic "DESMOND_GPGPU:16"'



job_file = args.job_file
while os.path.exists(job_file):
    splited = job_file.replace(".sh","").split("_")
    splited[-1] = str(int(splited[-1]) + 1)
    job_file = "_".join(splited) + ".sh"

if len(args.temp) > 1:
    try:
        assert len(args.temp) == len(args.simulation_time)
        assert len(args.temp) == (len(args.ramp) + 1)
    except:
        print("For a variable temperature simulaton, the number of temperatures and simulation times ")
        print("should match and temperature ramp(s) (ps/K) should be given between temperatures.")
        print("Please check -T, -t and -R options")
        sys.exit(0)
else:
    args.ramp = [] # not used


with open("README","a") as readme, open(job_file,"w") as job:
    print(f"Job file = {job_file}")

    dirs = [ f"{args.prefix}{n:02d}" for n in range(args.start, args.start+args.repeat) ]

    t_schedule = [ [ args.temp[0], 0.0 ], ]

    if len(args.temp) > 1 :

        elapsed = 0
        prev_temp = args.temp[0]
        idx = 0

        for (temp,simulation_time) in zip(args.temp, args.simulation_time):


            deltaT = abs(temp - prev_temp)

            if deltaT > 0.001: # ramp
                elapsed += args.ramp[idx] * deltaT # ramp: ps/K
                t_schedule.append([temp, elapsed])
                idx += 1

            elapsed += simulation_time * 1000. # ns -> ps
            t_schedule.append([temp, elapsed]) # ns -> ps
            prev_temp = temp
        total_simulation_time = elapsed # ps
    else:
        total_simulation_time = sum(args.simulation_time) * 1000.0 # ps

    if not args.interval:
        # args.simulation_time in ns and args.interval in ps
        # default: make 1000 frames
        args.interval = total_simulation_time / 1000.
     
    readme.write(f"GPU device              = {args.gpu_device}\n")
    readme.write(f"Temperature (K)         = {args.temp}\n")
    readme.write(f"Temperature Ramp (ps/K) = {args.ramp}\n")
    readme.write(f"Simulation Time (ns)    = {args.simulation_time}\n")
    readme.write(f"Temperature schedule    = {str(t_schedule)}\n")
    readme.write(f"Total Sim. Time (ns)    = {total_simulation_time/1000.0}\n")
    readme.write(f"Trajectory interval(ps) = {args.interval}\n")
    readme.write(f"Repeat                  = {args.repeat}\n")
    readme.write( "Directory               = %s\n" % " ".join(dirs))
    readme.write(f"Jobfile                 = {job_file}\n\n")
    
    for i, infile in enumerate(cms_files):
        info = f"[{i+1:02d}] {infile}"
        print(info)
        readme.write(info+"\n")
    readme.write("\n\n")

    job.write(f'export CUDA_VISIBLE_DEVICES="{args.gpu_device}"\n\n')

    for n in range(args.start, args.start+args.repeat): 
        outdir = f"{args.prefix}{n:02d}"
        outdir_abspath = os.path.abspath(outdir)
        job.write(f"cd {outdir_abspath}/\n\n")
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        msj_file = f"{outdir}/desmond_md_job_{n:02d}.msj"
        cfg_file = f"{outdir}/desmond_md_job_{n:02d}.cfg"
        cfg_file_basename= os.path.basename(cfg_file)
        
        with open(msj_file,"w") as msj:
            # modify desmond msj template
            desmond_md_msj = msj_.sub(f'cfg_file = "{cfg_file_basename}"', desmond_md_msj)
            msj.write(desmond_md_msj)

        with open(cfg_file,"w") as cfg:
            # modify desmond cfg template
            cfg_template["randomize_velocity"]["seed"] = random.randint(1000,9999)
            cfg_template["time"] = total_simulation_time
            cfg_template["temperature"] = t_schedule
            cfg_template["trajectory"]["interval"] = args.interval
            write_formatted_cfg(cfg_template, cfg)

        for infile in cms_files:
            prefix_ = re.sub(r'desmond_setup[-_]','', os.path.basename(infile))
            prefix  = prefix_.replace("-out.cms","")
            
            job_name = f"desmond_md_job_{n:02d}_{prefix}"
            job.write('if [ ! -f {}/{} ]\n'.format( outdir_abspath, f"{job_name}-out.cms",))
            job.write('then\n')
            job.write('{} -JOBNAME {} -m {} -c {} -description "{}" {} {} -o {} -WAIT\n'.format(
                multisim, 
                job_name, 
                os.path.basename(msj_file),
                os.path.basename(cfg_file),
                "GPU desmond MD",
                opt,
                os.path.join("..",infile),
                f"{job_name}-out.cms",
            ))
            job.write('fi\n\n')

os.chmod(job_file, 0o777)
