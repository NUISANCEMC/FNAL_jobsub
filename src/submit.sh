export GXMLPATH=/minerva/app/users/jstowell/NUISANCEMC/event_generator/genie/splines/Official-R-2_12_0/ValenciaQEBergerSehgalCOHRES/data/

nuisance_jobsub -JOB gevgen -SITE GRID -TAG gevtest \
    -out gntp.MINERvA_fhc_numu.CH.2500.ghep.root \
    -run 1 \
    -target CH \
    -flux MINERvA_fhc_numu \
    -nevents 2500 \
    -gxml $GXMLPATH \
    -spline $GXMLPATH/gxspl-FNALsmall.xml \
    -energy 0.0,100.0 \
    -list Default+MEC

