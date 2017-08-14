import pickle
import os
from datetime import datetime as date
import sys
from subprocess import call
from CardParser import *

class NuisCompJob:

    InputFiles  = []
    MetaData    = []

    def __init__(self, args, nuisargs):

        self.CurDir      = os.getcwd()
        self.Site        = args.site
        self.Tag         = args.tag
        
        self.UID = "__NUISCOMP-" + self.Tag + "-" + date.now().strftime('%Y%m%d%H%M%S') + "-" + str(os.getpid())

        self.NUISANCESetupScript = os.environ["NUISANCE_CVMFS_SETUP"]
        self.IFDHCSetupScript = os.environ["NUISANCE_IFDHC_SETUP"]
        self.PNFS     = os.environ["NUISANCE_PNFS_RESULTS_AREA"] 

        # Setup Input Card
        self.CardPath    = os.path.abspath(args.card)
        call(["ifdh","cp",self.CardPath, self.CardPath + self.UID + ".xml"])
        self.CardPath    = self.CardPath + self.UID + ".xml"
        self.CardFile    = self.CardPath.split("/")[-1]
        self.CardDir     = self.CardPath.replace(self.CardFile,"")

        # Also append input files from card if on grid
        if self.Site == "GRID":
            newf = ParseInputFiles(self.CardPath)
            for fi in newf:
                if fi not in self.InputFiles:
                    self.InputFiles.append(fi)

            # Now that the input files have been removed, we
            # should make sure we make a -local card
            UpdatePaths(self.CardPath, self.CardPath.replace(".xml","") + "-local.xml")
            self.CardPath = self.CardPath.replace(".xml","") + "-local.xml"

        self.CardFile    = self.CardPath.split("/")[-1]
        self.CardDir     = self.CardPath.replace(self.CardFile,"")
        self.PNFSArea = self.PNFS + "/" + self.CardFile.replace(".xml","") + self.UID
        if  self.Site == "GRID" :
            if "/pnfs" not in self.CardPath:
                if self.PNFS != "NULL":
                    print "Saving job to : " + self.PNFSArea
                    
                    # Make Directory
                    call(["ifdh","mkdir",self.PNFSArea])

                    # Copy Card Across
                    call(["ifdh","cp",self.CardPath, self.PNFSArea + "/" + self.CardFile])
                    
                    # Update Card Paths
                    self.CardPath    = self.PNFSArea + "/" + self.CardFile
                    self.CardFile    = self.CardPath.split("/")[-1]
                    self.CardDir     = self.CardPath.replace(self.CardFile,"")

                else:
                    print "If running GRID job card file must be on the /pnfs/ area"
                    sys.exit(1)
            
    
        self.OutputPath  = os.path.abspath(args.out)
        self.OutputFile  = self.OutputPath.split("/")[-1]
        self.OutputDir   = self.OutputPath.replace(self.OutputFile,"")
        if  self.Site == "GRID" :
            if "/pnfs" not in self.OutputPath:
                if self.PNFS != "NULL":
                    print "Saving output to : " + self.PNFSArea
                    
                    # Make directory
                    call(["ifdh","mkdir",self.PNFSArea])
                    
                    # Update Output Paths
                    self.OutputPath = self.PNFSArea + "/" + self.OutputFile
                    self.OutputFile  = self.OutputPath.split("/")[-1]
                    self.OutputDir   = self.OutputPath.replace(self.OutputFile,"")
                else:
                    print "If running GRID job output MUST be on the /pnfs/ area!"
                    sys.exit(-1)


        self.Arguments = "-c " + self.CardFile + " -o " + self.OutputFile + " " + nuisargs

        if args.inp:
            for inps in args.inp:
                if inps not in self.InputFiles:
                    self.InputFiles.append(inps)
        if self.CardPath not in self.InputFiles:
            self.InputFiles.append(self.CardPath)

        self.NUISANCESetupScript = os.environ["NUISANCE_CVMFS_SETUP"]
        self.IFDHCSetupScript = os.environ["NUISANCE_IFDHC_SETUP"]
        self.PNFSArea = os.environ["NUISANCE_PNFS_RESULTS_AREA"]

        self.MetaData = ["NUISCOMP JOB"]

        self.ScriptFile  = self.CardFile + self.UID + ".sh"
        self.ScriptPath  = self.CurDir + "/" + self.ScriptFile
        self.ScriptDir   = self.ScriptPath.replace(self.ScriptFile,"")

        self.SubPreAmble = "-G minerva -M --OS=SL6"
        self.SubResource = "DEDICATED"
        self.SubLifeTime = "2h"
        self.SubMemory   = "2000MB"

    def MakeScript(self):
        
        # Open the script
        script = open(self.ScriptPath,"w")
        
        # Make submission Script
        script.write("#!/bin/sh\n")

        # NUISANCE_JOB
        script.write("# - CardFile    = " + self.CardFile + "\n")
        script.write("# - OutputFile  = " + self.OutputFile + "\n")
        script.write("# - Arguments   = " + self.Arguments + "\n")
        script.write("# - Site = " + self.Site + "\n")
        script.write("# - Tag  = " + self.Tag + "\n")
        script.write("# - ScriptFile = " + self.ScriptFile + "\n")
        for i, f in enumerate(self.InputFiles):
            script.write("# - File " + str(i) + " = " + f + "\n")            
        script.write("# - MetaData : \n")
        for m in self.MetaData:
            script.write("# - - " + m + "\n")
        script.write("\n")

        # Setup NUISANCE
        script.write("# Setup NUISANCE\n")
        script.write(self.NUISANCESetupScript + "\n")
        script.write("source $GENIE/setup.sh \n")
        script.write("source $NUWRO/setup.sh \n")
        script.write(self.IFDHCSetupScript + "\n")


        if self.Site == "GRID":
            
            # Make out directory
            script.write("# Make out directory\n")
            script.write("mkdir out\n")
            script.write("cd out\n")

            # Copy files here
            script.write("# Copy files here\n")
            for infile in self.InputFiles:
                if infile != infile.split("/")[-1]:
                    script.write("ifdh cp " + infile + " " + infile.split("/")[-1] + "\n")
        
        else:

            # Change to run area
            script.write("# Change to run area \n")
            script.write("cd " + self.CardDir + "\n")

        # Run Job
        script.write("# Run Job\n")
        script.write("nuiscomp " + self.Arguments + "\n")

        # Remove input files
        if self.Site == "GRID":
            # Copy files here
            script.write("# Remove inputs\n")
            for infile in self.InputFiles:
                script.write("rm " + infile.split("/")[-1] + "\n")

            # Copy output back
            script.write("# Copy output back\n")
            script.write("cd ../\n")
            script.write("for file in ./out/*\n")
            script.write("do\n")
            script.write("  echo Copying out : $file\n")
            script.write("  ifdh cp -D $file " + self.OutputDir + "\n")
            script.write("done\n")
        else:
            # CD BACK
            script.write("# CD BACK\n")
            script.write("cd -\n")

        script.close()

        # If running on the grid also copy the file to the /PNFS/area
        if not os.path.isfile(self.OutputDir + "/" + self.ScriptFile):
            call(["ifdh","cp",self.ScriptPath,(self.OutputDir + "/" + self.ScriptFile)])

    def Validate(self):
        # Check the input files are accessible if on grid
        if self.Site == "Grid":
            print "Validating"

    def AddInputFile(self,files):
        self.InputFiles.append(files)



# To do,
# - move this into NuisCompJob class file
# - Move SubmitJob And Pickle Job Functions into JobHandler.py
# - Make a main function which parses arguments and depending on type creates different jobs.
