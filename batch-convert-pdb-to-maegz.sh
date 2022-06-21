#!/usr/bin/bash
for pdb in $( ls *.pdb )
do
  maegz=${pdb::-4}.maegz
  echo $maegz
  $SCHRODINGER/utilities/structconvert $pdb $maegz
done
