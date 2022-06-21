#!/bin/bash
for cms in $( find ../md/r01 -name \*-out.cms )
do
  echo $cms
  outdcd=$( basename $cms .cms )
  outdcd="${outdcd}-nowat.dcd"
  if [ ! -f $outdcd ]; then
    vmd -dispdev text -e $HOME/bucket/vmd/vmd_desmond.tcl -args $cms
  fi
done

for pdb in $( find -name \*-nowat.pdb )
do
  newpdb="${pdb::-4}-segid.pdb"
  if [ ! -f $newpdb ]; then 
    echo $pdb
    $HOME/bucket/pdb/pdb-segid $pdb > ${pdb::-4}-segid.pdb
  fi
done

exit
