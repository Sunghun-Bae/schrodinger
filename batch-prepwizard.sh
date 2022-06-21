#!/usr/bin/bash
for infile in "$@"
do 
  outfile=${infile::-4}.maegz
  if [ ! -f $outfile ]; then
    echo Preparing $outfile from $infile
    ${SCHRODINGER}/utilities/prepwizard -rehtreat \
       -disulfides -fillsidechains $infile $outfile -NJOBS 4
  fi
done
exit

# Usage: $SCHRODINGER/utilities/prepwizard [options] inputfile outputfile
#     Input file should be in Maestro or PDB format.
#     Output file should be in Maestro or PDB format.

# Options:
#   -v, -version          Show the program's version and exit.
#   -h, -help             Show this help message and exit.
#   -nobondorders         Don't assign bond orders to het groups
#   -noccd                Don't use the Chemical Component Dictionary when
#                         assigning bond orders.
#   -nohtreat             Don't add hydrogens
#   -rehtreat             Delete and re-add hydrogens (will reset PDB atom
#                         names)
#   -noidealizehtf        Don't idealize added hydrogen temperature factors.
#   -addOXT               Add terminal oxygens to polypeptides when they are
#                         missing
#   -c, -captermini       Cap termini
#   -keepfarwat           Don't delete waters far from het groups
#   -watdist WATDIST      Distance threshold for 'far' waters (default 5A)
#   -nometaltreat         Don't treat metals (adding zero-order bonds, etc)
#   -disulfides           Create bonds to proximal Sulfurs (delete hydrogens as
#                         needed)
#   -glycosylation        Create bonds to N-linked and O-linked sugars (delete
#                         hydrogens as needed)
#   -palmitoylation       Create palmitoylation bonds even if not included in
#                         the CONNECT records ( delete hydrogens as needed)
#   -mse                  Convert Selenomethionine residues to Methionines
#   -fillsidechains       Fill missing side chains Prime
#   -fillloops            Fill missing loops with Prime
#   -fasta_file CUSTOM_FASTA_FILE
#                         If filling missing residues, the custom fasta file to
#                         use. If not specified, the fasta file will be
#                         generated from the sequence that was stored in the
#                         input structure when it was converted from the PDB
#                         format.
#   -noepik               Don't run Epik on het groups. By default Epik is ran
#                         on all het groups, and metal binding states are
#                         considered for hets that are within 5A of metal atoms.
#   -ms MAX_STATES        Maximum number of states to generate for each het
#                         group when running Epik.
#   -noprotassign         Don't run ProtAssign
#   -s, -samplewater        ProtAssign: sample waters
#   -xtal                   ProtAssign: Use crystal symmetry
#   -pH PH                  ProtAssign: Sample at given pH ('very_low', 'low',
#                         'neutral', 'high')
#   -propka_pH PROPKA_PH    ProtAssign: Run PROPKA at given pH value
#   -nopropka               ProtAssign: Do not use PROPKA for protonation states
#   -label_pkas             ProtAssign: Label residues with PROPKA pKas
#   -force FORCE_LIST       ProtAssign: Force a particular residue to adapt the
#                         specified state. Multiple -f specifications are
#                         permitted. See $SCHRODINGER/utilities/protassign help
#                         for more info.
#   -minimize_adj_h         ProtAssign: Minimize all adjustable hydrogens
#                         (titratable hydrogens, water hydrogens, hydroxyls,
#                         thiols, and ASN/GLN carboxamide hydrogens).
#   -epik_pH EPIK_PH      Epik target pH (Default 7.0)
#   -epik_pHt EPIK_PHT    Epik pH range for generated structures (Default 2.0)
#   -delwater_hbond_cutoff DELWATER_HBOND_CUTOFF
#                         If specified, delete waters that do not make at least
#                         this number H-bonds to non-waters. By default, this
#                         feature is disabled. This step is ran after
#                         ProtAssign.
#   -noimpref             Don't run a restrained minimization job
#   -r RMSD, -rmsd RMSD     Minimization: RMSD cuttoff (default 0.3)
#   -fix                    Minimization: Fix heavy atoms (minimize hydrogens
#                         only)
#   -f FORCE_FIELD          Minimization: Version of the OPLS force field to
#                         use. Options: 2005 or 3. Default is 2005.
#   -reference_st_file REFERENCE_ST_FILE
#                         File containing reference structure to align to.
#   -reference_pdbid REFERENCE_PDBID
#                         PDB ID of the structure to align to.
#   -j JOBNAME            Jobname to use. By default, jobname is based on the
#                         input file.
#   -NJOBS NJOBS          Number of jobs to create (default 1)

#   Job Control Options:
#     -HOST <hostname>    Run job remotely on the indicated host entry.
#     -WAIT               Do not return a prompt until the job completes.
#     -LOCAL              Do not use a temporary directory for job files. Keep
#                         files in the current directory.
#     -D, -DEBUG          Show details of Job Control operation.
#     -NOJOBID            Run the job directly, without Job Control layer.
