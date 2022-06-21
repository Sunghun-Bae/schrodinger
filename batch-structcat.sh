#!/bin/bash

for aso in $( ls init/MDN*.mae )
do
  prefix=$( basename ${aso} .mae )
  echo $prefix
  $SCHRODINGER/utilities/structcat -imae 2qk9-apo-chain-c.maegz $aso -omae init/2qk9-${prefix}.maegz
done
