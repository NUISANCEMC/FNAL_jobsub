#!/bin/sh

# Setup JOB PATH
export NUISANCE_JOB_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
alias nuisance_jobsub="python $NUISANCE_JOB_PATH/src/NuisanceSubmit.py"

# Setup CVFMS Apps (ENV variables required by jobsub scripts)
export NUISANCE_SETUP="/cvmfs/minerva.opensciencegrid.org/minerva/NUISANCE_080117/nuisance/v2r6/builds/genie2126-nuwrov11qrw/Linux/setup.sh"
export NUISANCE_CVMFS_SETUP="source $NUISANCE_SETUP"
source $NUISANCE_SETUP

export NUISANCE_IFDHC_SETUP="source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups.sh && setup ifdhc && export IFDH_CP_MAXRETRIES=1"
source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups.sh && setup ifdhc && IFDH_CP_MAXRETRIES=1

export NUISANCE_JOBSUB_SETUP="source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups.sh && setup jobsub_client"
source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups.sh && setup jobsub_client

export NUISANCE_SUBPREAMBLE="-G minerva -M --OS=SL6"

# Tell JOBSUB where it should automatically put PNFS jobs if no output is given on the PNFS area even though its a GRID JOB
#export NUISANCE_PNFS_RESULTS_AREA="/pnfs/"

