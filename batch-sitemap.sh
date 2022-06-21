#!/usr/bin/bash
pwd=$( pwd )

if [ ! -d sitemap ]; then
      mkdir sitemap
fi
cd sitemap
for infile in $( ls ../*.maegz )
do 
    jobname=$( basename $infile .maegz )  
    $SCHRODINGER/sitemap -ffield OPLS4 -keepvolpts yes -j $jobname -prot $infile
done
cd $pwd


# usage: 
#         $SCHRODINGER/sitemap [options] -j <jobname> -prot <file.mae>
#     or
#         $SCHRODINGER/sitemap [options] <input_file.in>

# $SCHRODINGER/sitemap carries out a site-finding job, then calculates SiteMaps
# for each qualifying site-point grouping, and finally evaluates the SiteMap
# results and summarizes the characteristics of the sites in a series of Maestro
# properties. SiteMap can be invoked from Maestro or can be run from the command
# line.

# positional arguments:
#   input_file            A file with lines such as "KEYWORD value", which are
#                         equivalent to "-keyword value" command-line arguments.
#                         (Except for job control options such as -HOST)

# optional arguments:
#   -j <jobname>, -job <jobname>, -jobname <jobname>
#                         A unique descriptor for this data set, used to make
#                         some file names unique. Required when not using an
#                         input file.
#   -h, -help             Show this help message and exit.

# Job Control Options:
#   -HOST <hostname>      Run job remotely on the indicated host entry.

# Common SiteMap Options:
#   -prot <file.mae> [<file.mae>...], -protein <file.mae> [<file.mae>...]
#                         A required protein file in Maestro format. Multiple
#                         such options may be specified to run multiple jobs.
#   -lig <file>, -ligmae <file>, -ligsdf <file>
#                         include optional ligand file in Maestro or SD format
#   -siteasl <asl>        ASL expression used instead of a ligand to restrict
#                         the site-finding step.
#   -sitebox <dist>       If an optional ligand file or ASL expression is
#                         specified, restrict the site-finding step to a box
#                         placed around the ligand plus a margin of <dist> (no
#                         default)
#   -addsp [yes|no]       Add additional "extend" site points to the site-point
#                         set if they fall in regions that satisfy the threshold
#                         criteria for phobicity or philicity (default, "yes")
#   -xcent XCENT          X coordinate of grid center, to be used instead of
#                         ligand-, receptor-, or ASL-based centroid
#   -ycent <float>        Y coordinate of grid center
#   -zcent <float>        Z coordinate of grid center
#   -xrange <float>       X size of grid box, to be used instead of receptor-,
#                         or ASL-based box size
#   -yrange <float>       Y size of grid box
#   -zrange <float>       Z size of grid box
#   -reportsize <size>    Minimum number of site points needed to report a site
#                         grouping (default, 15)
#   -maxsites <max>       Find/report up to this number of sites (default, 5)
#   -modphobic {0|1|2|3}  Set definition to be used in defining hydrophobic
#                         regions (default, 3)
#   -grid <gridsize>      Grid size to be used in the SiteMap calculations
#                         (default, 0.7 A)
#   -resolution <val>     Alternative means for specifying the grid size
#                         (<val>="low" for 1.0 A, "standard" for 0.7 A or "high"
#                         for 0.35 A)
#   -mapdist <dist>       Restrict displayed SiteMaps to <dist> from the nearest
#                         site point (default, 4 A). Can be overriden, up to the
#                         "-margin <margin>" distance, by using the Surface
#                         Limit facility
#   -ffield <OPLS version>
#                         Version of OPLS to use (default, OPLS_2005)
#   -extend <intdist>     In evaluating exposure in site-evaluation stage, try
#                         adding additional site points at grid points +/-
#                         <intdist> from an original site point (default, 3 A)
#   -cleanup [yes|no]     Retain intermediate files (*.grd, *_volpts.pdb)
#   -compress [yes|no]    Compress the final _out.mae file using gzip. (default,
#                         "yes")
#   -keepvolpts [yes|no]  keeps pdb-format files that contain the points that
#                         are summed to compute the volume property assigned for
#                         the site (default, "no")
#   -writepot [yes|no]    writes (x,y,z,potential) files that specify the
#                         phobic, philic, donor, acceptor, vdW, electrostatic,
#                         and surface potentials computed by SiteMap (default,
#                         "no")
#   -keepvdw [yes|no]     computes and keeps grid-format file of vdW potentials
#                         computed by SiteMap (default, "no")
#   -keepelec [yes|no]    computes and keeps grid-format file of electrostatic
#                         potentials computed by SiteMap (default, "no")
#   -writestructs [yes|no]
#                         include a copy of the receptor structure (and ligand,
#                         if any) in the output file (default, "yes")
#   -writevis [yes|no]    write .vis and .smap files for surface visualization
#                         (default, "yes")
#   -writegrids [yes|no]  write all .grd files (default, "no")

# Additional Options:
#   -enclosure <fraction>
#                         Fraction of ray directions from a grid point that must
#                         intersect the protein within a specified distance for
#                         that grid point to be considered as a potential site
#                         point (default, 0.5)
#   -maxdist <dist>       Distance within which a directional ray from a
#                         candidate grid point must intersect the protein
#                         surface (default, 8 A)
#   -maxvdw <vdw-energy>  vdW interaction-energy threshold (kcal/mol) for a grid
#                         point to qualify as a potential site point (default,
#                         1.1). Note this quantity is the negative of the
#                         computed interaction energy, so that the argument
#                         supplied must be positive. A smaller positive value
#                         keeps more candidate site points
#   -verbosity {0|1|2|3}  Control level of detail in output log files (default,
#                         0)
#   -margin <margin>      Grid-box margin to be used in the SiteMap calculations
#                         (default, 6 A)
#   -addphob <thresh>     Set criterion for adding additional phobic points to
#                         <thresh> (default, -0.50 kcal/mol if modphobic
#                         argument is 2 or 3, otherwise -0.75 kcal/mol)
#   -addphil <thresh>     Set criterion for adding additional philic points
#                         (default, -8 kcal/mol)

# Advanced Options:
#   -dvscale <float>      When multiplied by the square of a protein-atom vdW
#                         radius, the argument sets the squared distance from a
#                         candidate site point to a protein atom for determining
#                         whether the site point is "inside" or "outside" the
#                         protein (default, 2.5)
#   -nthresh <int>        Minimum number of candidate site-point neighbors
#                         required to be within a distance of sqrt(d2thresh) for
#                         a candidate site point to be eligible for inclusion in
#                         a site-point grouping (default, 3)
#   -d2thresh <float>     Squared distance used in nthresh test (default 3.1
#                         A**2)
#   -kmax <int>           Maximum sum of differences in grid indices to nearest
#                         site point allowed to add a candidate site point to a
#                         site-point group (default, 3)
#   -kmax2 <int>          Maximum sum of squares of differences in grid indices
#                         to nearest site point allowed for a candidate site
#                         point to be added to a site-point group (default, 5)
#   -mingroup <int>       Minimum number of points in a site-point grouping
#                         required to constitute a site (default, 3)
#   -dthresh <float>      Maximum acceptable value for the minimum distance
#                         separating site points in two site-point groupings for
#                         them to be considered for merger into a single group
#                         (default, 6.5 A)
#   -rthresh <float>      Minimum acceptable ratio of the distance between the
#                         centroids of two site-point groups relative to the
#                         effective sizes of the groups (default, 5.)
#   -r2thresh <float>     Squared distance used in determining whether two site-
#                         point groupings being considered for merger have
#                         successfully been interconnected by solvent-exposed
#                         bridging points (default, 4.1 A**2)
#   -cutoff <cutdist>     The cutdist value restricts the calculation of vdW and
#                         electrostatic potentials to protein atoms that lie
#                         within this distance of a grid point (default, 20 A)
#   -modcharges [yes|no]  The default value of "yes" scales down formal-charge
#                         contributions to the protein partial atomic charges by
#                         50%
#   -nearres <float>      Maximum distance between sitepoints and residues to
#                         list in the s_sitemap_residues property (default, 3.5
#                         A).
