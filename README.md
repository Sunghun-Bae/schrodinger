# Schrodinger

- wrappers for Schrodinger tools
- requires proper installation of Schrodinger Suites

## example

```
$ $SCHRODINGER/run batch-desmond-setup.py --help
usage: batch-desmond-setup.py [-h] [-c CONC] [-d DIST] [-l LIPID] [--cpp] [-s SOLVENT] [-i COUNTERION] [-n NEG] [-p POS]
                              [-f FORCEFIELD] [-j JOB_FILE] [-m MSJ_FILE] [-a APPENDIX]
                              mae [mae ...]

batch gdesmond md system setup

positional arguments:
  mae                   desmond mae file

optional arguments:
  -h, --help            show this help message and exit
  -c CONC, --conc CONC  salt concentration in M (default: 0.15)
  -d DIST, --dist DIST  buffer distance in A (default: 10.0)
  -l LIPID, --lipid LIPID
                        lipid bilayer (default: )
  --cpp                 CPP simulation setup (default: False)
  -s SOLVENT, --solvent SOLVENT
                        solvent model (default: SPC)
  -i COUNTERION, --counterion COUNTERION
                        neutralizing ion (default: K)
  -n NEG, --negative NEG
                        negative salt ion (default: Cl)
  -p POS, --positive POS
                        positive salt ion (default: K)
  -f FORCEFIELD, --forcefield FORCEFIELD
                        forcefield (default: S-OPLS)
  -j JOB_FILE, --jobfile JOB_FILE
                        job filename (default: desmond_setup_1.sh)
  -m MSJ_FILE, --msjfile MSJ_FILE
                        msj filename (default: desmond_setup_1.msj)
  -a APPENDIX, --appendix APPENDIX
                        job name appendix (default: )
                        
$SCHRODINGER/run batch-desmond-md.py --help
usage: batch-desmond-md.py [-h] [-g gpu_device] [-T temperature [temperature ...]] [-R tempramp [tempramp ...]]
                           [-t simulation_time [simulation_time ...]] [-i interval] [-p PREFIX] [-s START] [-r REPEAT]
                           [-j JOB_FILE]
                           cms [cms ...]

batch gdesmond md jobs

positional arguments:
  cms                   desmond cms file

optional arguments:
  -h, --help            show this help message and exit
  -g gpu_device         gpu device id (default: 0)
  -T temperature [temperature ...]
                        temperature in K (default: [300.0])
  -R tempramp [tempramp ...]
                        heat and cool ramps in ps/K (default: [10.0])
  -t simulation_time [simulation_time ...]
                        simulation time in ns (default: [100.0])
  -i interval           frame interval in ps (default: 100.0)
  -p PREFIX             directory prefix (default: r)
  -s START              directory start (default: 1)
  -r REPEAT             number of repeats (default: 1)
  -j JOB_FILE           job filename (default: desmond_md_job_1.sh)
```
