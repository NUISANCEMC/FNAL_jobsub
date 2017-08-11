#!/bin/sh

# Setup JOB PATH
export NUISANCE_JOB_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
alias nuisance_jobsub="python $NUISANCE_JOB_PATH/src/NuisanceSubmit.py"

# Setup CVFMS Apps (ENV variables required by jobsub scripts)
export NUISANCE_CVMFS_SETUP="source /cvmfs/minerva.opensciencegrid.org/minerva/NUISANCE_080117/nuisance/v2r6/builds/genie2126-nuwrov11qrw/Linux/setup.sh"
export NUISANCE_IFDHC_SETUP="source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups.sh && setup ifdhc"
export NUISANCE_JOBSUB_SETUP="source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups.sh && setup jobsub_client"
source /cvmfs/minerva.opensciencegrid.org/minerva/NUISANCE_080117/nuisance/v2r6/builds/genie2126-nuwrov11qrw/Linux/setup.sh
source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups.sh && setup ifdhc
source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups.sh && setup jobsub_client

# Tell JOBSUB where it should automatically put PNFS jobs if no output is given on the PNFS area even though its a GRID JOB
export NUISANCE_PNFS_RESULTS_AREA=""
#=/pnfs/minerva/persistent/users/jstowell/NUISANCEMC/minerva_tuning/jobsub-outputs/



