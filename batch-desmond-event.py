""" Extract RMSD and RMSF from ...-out.eaf file(s) """

import re
import sys
import os
import pandas as pd
import argparse

ASL = re.compile(r"""\s+ASL\s+=\s+\"(?P<asl>[A-Za-z0-9\s.()]+)\"""")
FitBy = re.compile(r"""\s+FitBy\s+=\s+\"(?P<fitby>[A-Za-z0-9\s.()]+)\"""")
ProteinResidues = re.compile(r"""\s+ProteinResidues\s+=\s+\[(?P<resid>[":A-Z0-9_\s]+)\s+\]""")
Result = re.compile(r"""\s+Result\s+=\s+\[(?P<value>[\d\s.]+)\s+\]""")
SelectionType = re.compile(r"""\s+SelectionType\s+=\s+(?P<select>[a-zA-Z"\s]+)$""")

parser = argparse.ArgumentParser(description="batch gdesmond event analysis",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('eaf', nargs="+", help="-out.eaf file(s)")
args = parser.parse_args()

RMSD_dataframes = []
RMSF_dataframes = []

for filename in sys.argv[1:] :
    with open(filename, "r") as f:
        data = {"RMSD":{}, "RMSF":{}}
        read = None
        asl = None
        fitby = None
        residues = None
        for line in f:
            if "RMSD" in line:
                read = "RMSD"
                continue
            if "RMSF" in line:
                read = "RMSF"
                continue
            
            m = ProteinResidues.match(line)
            if read == "RMSF" and m:
                # ['A:GLN_20', ...] ---> [20, ...]
                residues = [ int(v.split("_")[-1]) for v in m.group("resid").replace('"','').split() ] 
            
            # m = ASL.match(line)
            # if m:
            #     asl = m.group("asl").strip()
            
            m = FitBy.match(line)
            if m:
                fitby = m.group("fitby").strip()
            
            m = Result.match(line)
            if read and m:
                values = [ float(v) for v in m.group("value").split() ]
            
            m = SelectionType.match(line)
            if read and m:
                column = m.group("select").strip().replace('"','').replace(' ','_').lower()
                if read == "RMSD":
                    if values and (column not in data["RMSD"]):
                        if column == "ligand" :
                            if fitby:
                                data["RMSD"][column] = values
                        else:
                            data["RMSD"][column] = values
                    if "frame" not in data["RMSD"]:
                        data["RMSD"]["frame"] = list(range(1, len(values)+1))
                elif read == "RMSF":
                    if residues and ("Residue" not in data["RMSF"]):
                        data["RMSF"]["Residue"] = residues
                    if values and (column not in data["RMSF"]):
                        data["RMSF"][column] = values
                
                read = None
                fitby = None
                asl = None
                residues = None

        df = pd.DataFrame(data["RMSD"])
        df["name"] = os.path.basename(filename).replace("-out.eaf","")
        RMSD_dataframes.append(df)
        df = pd.DataFrame(data["RMSF"])
        df["name"] = os.path.basename(filename).replace("-out.eaf","")
        RMSF_dataframes.append(df)

pd.concat(RMSD_dataframes).to_csv("rmsd.csv", index=False)
pd.concat(RMSF_dataframes).to_csv("rmsf.csv", index=False)
