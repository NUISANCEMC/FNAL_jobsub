import pickle
import os
from datetime import datetime as date
import sys
from subprocess import call
from CardParser import *
import hashlib
import argparse

def GetHash(s):
    return str(int(hashlib.sha256(s.encode('utf-8')).hexdigest(), 16) % 10**16)

class GevGenJob:

    InputFiles  = []
    MetaData    = []

    def GetArguments(self):

        parser = argparse.ArgumentParser (description = "NUISANCE Job Handler @ FERMILAB",
                                          usage = "./NuisanceSubmit.py <options>")

        required = parser.add_argument_group ("required arguments")
        required.add_argument ("-JOB",   action = "store", dest = "job", metavar = "[TYPE OF NUIS]", required = True)
        required.add_argument ("-TAG",     action = "store", dest = "tag",  metavar = "[TAG TO IDENTIFY FIT]", required = True)
        required.add_argument ("-SITE",  action = "store", dest = "site", 
                               metavar = "[RUN SITE]", required = True)
        required.add_argument ("-INPUT", action = "append", dest = "inp",
                               metavar = "[PATH TO INPUTFILES]", required = False)

        required.add_argument ("-out",     action = "store", dest = "out",  metavar = "[PATH TO OUTPUTFILE]", required = True)
        required.add_argument ("-run",     action = "store", dest = "run", metavar = "[RUN NUMBER]", required = True)
        required.add_argument ("-target",  action = "store", dest = "target", metavar = "[GEVGEN TARGET]", required = True)
        required.add_argument ("-flux",    action = "store", dest = "flux", metavar = "[GEVGEN FLUX]", required = True)
        required.add_argument ("-nevents", action = "store", dest = "nevents", metavar = "", required = True)
        required.add_argument ("-gxml", action = "store", dest = "xsecpath", metavar = "", required = True)
        required.add_argument ("-spline", action = "store", dest = "splinepath", metavar = "", required = True)
        required.add_argument ("-list", action = "store", dest = "generatorlist", metavar = "", required = True)
        required.add_argument ("-energy", action = "store", dest = "energy", metavar = "", required = True)
                
        args, other = parser.parse_known_args()

        nuisargs = ' '.join(other)
        
        return args, nuisargs


    def __init__(self, args, nuisargs):

        args, nuisargs = self.GetArguments()

        # Read CurDir
        self.CurDir      = os.getcwd()
        self.Site        = args.site
        self.Tag         = args.tag

        # GevGen Requirements
        # - Output Name
        # - Run Number (randomised)
        # - Target
        # - Flux
        # - NEvents
        # - Model MetaData 
        # - GXMLPATH
        # - Spline Path
        
        self.Out           = args.out
        self.RunNumber     = args.run
        self.Target        = args.target
        self.Flux          = args.flux
        self.NEvents       = args.nevents
        self.XSecPath      = args.xsecpath
        self.SplinePath    = args.splinepath
        self.GeneratorList = args.generatorlist
        self.Energy        = args.energy

        # Read setup paths
        self.NUISANCESetupScript = os.environ["NUISANCE_CVMFS_SETUP"]
        self.IFDHCSetupScript    = os.environ["NUISANCE_IFDHC_SETUP"]
        self.PNFS                = os.environ["NUISANCE_PNFS_RESULTS_AREA"]

        # Create a UniqueID
        self.UID = "__GEVGEN-" + date.now().strftime('%Y%m%d') + "-" + str(os.getpid())
        
        # Read output path
        self.OutputPath  = os.path.abspath(self.Out)
        self.OutputFile  = self.OutputPath.split("/")[-1]
        self.OutputDir   = self.OutputPath.replace(self.OutputFile,"")

        # If running on the grid make sure there is a place to store outputs.
        # This is saved to a hashed folder in the pnfs area.
        if self.Site == "GRID":
            self.OutputHash = GetHash(self.OutputDir)
            self.OriginalOutputPath = self.OutputPath
            self.OutputPath = (self.PNFS + "/output-" + 
                               self.OutputHash + "/" + self.OutputFile)
            self.OutputFile  = self.OutputPath.split("/")[-1]
            self.OutputDir   = self.OutputPath.replace(self.OutputFile,"")
            
            if not os.path.isdir(self.OutputDir):
                call(["mkdir", self.OutputDir])

        # Read the Spline Input File
        self.SplinePath = os.path.abspath(self.SplinePath)
        self.SplineFile = self.SplinePath.split("/")[-1]
        self.SplineDir  = self.SplinePath.replace(self.OutputFile,"")

        # Append any input files nad the xsec files
        if args.inp:
            # Add normal inputs
            for inps in args.inp:
                self.InputFiles.append(inps)
        # Add XSec Inputs
        self.InputFiles.append(self.SplinePath)

        # Setup the main arguments for gevgen
        self.Arguments = ("-r " + self.RunNumber + " " + 
                          "-n " + self.NEvents   + " " + 
                          "-t " + self.Target    + " " +
                          "-f " + self.Flux      + " " + 
                          "-e " + self.Energy    + " " + 
                          "--event-generator-list " + self.GeneratorList + " " + 
                          "--cross-sections " + self.SplineFile + " " + 
                          nuisargs)

        # Setup Scripts
        self.ScriptFile  = self.Tag + self.UID + ".sh"
        self.ScriptPath  = self.CurDir + "/" + self.ScriptFile
        self.ScriptDir   = self.ScriptPath.replace(self.ScriptFile,"")

        # Setup Standard Job Sub stuff
        self.MetaData = ["GEVGEN JOB"]
        self.SubPreAmble = "-G minerva -M --OS=SL6"
        self.SubResource = "DEDICATED"
        self.SubLifeTime = "24h"
        self.SubMemory   = "2500MB"
        self.CopyCommand = "ifdh cp -D "


    # Make Run Script
    def MakeScript(self):

        # Open the script
        script = open(self.ScriptPath,"w")
        script.write("#!/bin/sh\n")

        # Setup Options
        script.write("# Setup NUISANCE\n")
        script.write(self.NUISANCESetupScript + "\n")
        script.write("source $GENIE/setup.sh \n")
        script.write(self.IFDHCSetupScript + "\n")
        script.write("\n\n")

        # Add the input files
        script.write("# Make output directory\n")
        script.write("mkdir out\n")
        script.write("cd out\n")
        script.write("\n\n")

        # Copy input files
        if self.Site == "GRID":
            script.write("# Copy files here\n")
            for infile in self.InputFiles:
                if infile != infile.split("/")[-1]:

                    if infile.startswith("/pnfs"):
                        script.write(self.CopyCommand + " " +
                                     infile + " " + 
                                     infile.split("/")[-1] + "\n")
                    else:
                        script.write("cp " + 
                                     infile + " " +
                                     infile.split("/")[-1] + "\n")
            script.write("\n\n")

        else:
            # Change to run area
            script.write("# Change to run area \n")
            script.write("cd " + self.CardDir + "\n")
            script.write("\n\n")

        # Run Job
        script.write("# Run Job\n")
        script.write("export GXMLPATH=" + self.XSecPath + "\n")
        script.write("gevgen_nuisance " + self.Arguments + "\n")
        script.write("mv gntp." + self.RunNumber + ".ghep.root " + self.OutputFile + "\n")
        script.write("\n\n")

        # Copy the outputs
        if self.Site == "GRID":
            script.write("# Copy files back to /pnfs\n")
            script.write("outdir=" + self.OutputDir + "\n")
            script.write("cd out/ \n")
            script.write("for ofile in ./* \n")
            script.write("do\n")
            script.write("echo $ofile \n")
            script.write(self.CopyCommand + " $ofile $outdir/$ofile \n") 
            script.write("done\n")

        
    # Make Submission Script
    def MakeSubmissionScript(self):
        
        # Make submission command
        com = ""

        # If on grid, lots of stuff to setup...
        if self.Site == "GRID":
            com =  "jobsub_submit " + self.SubPreAmble
            com += " --resource-provides=usage_model=" + self.SubResource
            com += " --expected-lifetime=" + self.SubLifeTime
            com += " --memory=" + self.SubMemory
            com += " file://" + self.ScriptPath

        # If running local just source it
        elif self.Site == "LOCAL":
            com = "source " + self.ScriptPath
        
        # Else fail
        else:
            print "Job site not found!"
            sys.exit(1)
            
        # Setup submission script
        f = open(self.ScriptPath.replace(".sh","")+".jobsub","w")
        f.write("#!/bin/sh\n")
        f.write(os.environ['NUISANCE_JOBSUB_SETUP'] + "\n")
        f.write(com)
        f.close()
        
    # Fetch Script
    def MakeFetchScript(self):
        
        f = open(self.ScriptPath.replace(".sh","")+".fetch","w")
        f.write("#!/bin/sh \n")
        f.write("outdir=" + self.OutputDir + "\n")
        f.write("for file in $outdir/* \n")
        f.write("do \n")
        f.write(self.CopyCommand + " $file ./ \n")
        f.write("done \n")
        f.close()
