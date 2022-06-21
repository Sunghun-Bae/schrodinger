export CUDA_VISIBLE_DEVICES="0"

cd /home2/shbae/SCOT/2020/1009-viltolarsen/md-mixed/r01/

j=desmond_md_job_01_viltolarsen-mixed-0-I
/home/shbae/local/schrodinger2020-2/desmond \
    -JOBNAME ${j} -HOST localhost -gpu -restore ${j}.cpt -in ${j}-in.cms -cfg mdsim.last_time=500000 -WAIT

j=desmond_md_job_01_viltolarsen-mixed-2-I
/home/shbae/local/schrodinger2020-2/desmond \
    -JOBNAME ${j} -HOST localhost -gpu -restore ${j}.cpt -in ${j}-in.cms -cfg mdsim.last_time=500000 -WAIT

cd /home2/shbae/SCOT/2020/1009-viltolarsen/md-mixed/r02/

j=desmond_md_job_02_viltolarsen-mixed-0-I
/home/shbae/local/schrodinger2020-2/desmond \
    -JOBNAME ${j} -HOST localhost -gpu -restore ${j}.cpt -in ${j}-in.cms -cfg mdsim.last_time=500000 -WAIT

j=desmond_md_job_02_viltolarsen-mixed-2-I
/home/shbae/local/schrodinger2020-2/desmond \
    -JOBNAME ${j} -HOST localhost -gpu -restore ${j}.cpt -in ${j}-in.cms -cfg mdsim.last_time=500000 -WAIT

cd /home2/shbae/SCOT/2020/1009-viltolarsen/md-mixed/r03/

j=desmond_md_job_03_viltolarsen-mixed-3-I
/home/shbae/local/schrodinger2020-2/desmond \
    -JOBNAME ${j} -HOST localhost -gpu -restore ${j}.cpt -in ${j}-in.cms -cfg mdsim.last_time=500000 -WAIT

cd /home2/shbae/SCOT/2020/1009-viltolarsen/md-mixed/r04/

j=desmond_md_job_04_viltolarsen-mixed-3-I
/home/shbae/local/schrodinger2020-2/desmond \
    -JOBNAME ${j} -HOST localhost -gpu -restore ${j}.cpt -in ${j}-in.cms -cfg mdsim.last_time=500000 -WAIT
