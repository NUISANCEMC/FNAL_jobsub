import pickle
import os
from datetime import datetime as date
import sys
from subprocess import call

def LoadJob(p):
    return pickle.load( open( p, "rb" ) )

def SaveJob(job,p=None):
    if p == None: pickle.dump( job, open(job.PicklePath,"wb"))
    else: pickle.dump( job, open(p,"wb"))

def SubmitJob(job):

    com = ""
    if job.Site == "GRID":
        com =  "jobsub_submit " + job.SubPreAmble
        com += " --resource-provides=usage_model=" + job.SubResource
        com += " --expected-lifetime=" + job.SubLifeTime
        com += " --memory=" + job.SubMemory
        com += " file://" + job.ScriptPath
    else:
        com = "source " + job.ScriptPath

    f = open(job.ScriptPath + "__submit.sh","w") 
    f.write("#!/bin/sh\n")
    f.write(os.environ['NUISANCE_JOBSUB_SETUP'] + "\n")
    f.write(com)
    f.close()

    if not os.path.isfile(job.OutputDir + "/" + job.ScriptFile + "__submit.sh"):
        f = open(job.OutputDir + "/" + job.ScriptFile +"__submit.sh","w")
        f.write("#!/bin/sh\n")
        f.write(os.environ['NUISANCE_JOBSUB_SETUP']+ "\n")
        f.write(com)
        f.close()
