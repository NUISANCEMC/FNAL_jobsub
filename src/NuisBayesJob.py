import pickle
import os
from datetime import datetime as date
import sys
from subprocess import call, Popen, PIPE
from CardParser import *
import hashlib
import argparse
from ArgumentParser import *

def GetHash(s):
    return str(int(hashlib.sha256(s.encode('utf-8')).hexdigest(), 16) % 10**16)

class NuisBayesJob:

    InputFiles  = []
    MetaData    = []

    #________________________________________
    def GetArguments(self):

        parser = CreateParser( "NUISANCE nuisbayes Handler @ FERMILAB",
                               "nuisance_jobsub --job nuisbayes <options>",
                               "nuisbayes" )

        required=parser.add_argument_group ("required nuisbayes arguments")
        required.add_argument ("-c", action="store",  dest="card",    help="[ Input Cardfile ]",  required=True)
        required.add_argument ("-o", action="store",  dest="out",     help="[ Output Filename ]", required=True)

        optional=parser.add_argument_group ("optional nuisbayes arguments")
        optional.add_argument ("-q", action="append", dest="config",  help="[ Config override ]", required=False)
        optional.add_argument ("-f", action="store",  dest="routine", help="[ Routines override ]", required=False)
        optional.add_argument ("-n", action="store",  dest="nevents", help="[ NEvents Override ]", required=False)
        optional.add_argument ("-d", action="store",  dest="fakedt",  help="[ Fake Data Option ]", required=False)
        optional.add_argument ("-s", action="store",  dest="startthrow",  help="[ Start Throw (INT) ]", required=False)
        optional.add_argument ("-t", action="store",  dest="nthrows",  help="[ N Throws (INT) ]", required=False)
        optional.add_argument ("-p", action="store",  dest="throwstr",  help="[ Throw String ]", required=False)

        optional.add_argument ("--multiple", action="store", dest="multiple", help="[ Submits N multiple tunes ]", required = False)

        
        try:
            options=parser.parse_args()

        except:
            print ""
            print "#############################################"
            parser.print_help()
            print "#############################################"
            sys.exit(0)
            
        return options

    #________________________________________
    def __init__(self, args, nuisargs):

        # Read CurDir
        self.CurDir     =os.getcwd()

        # Read normal args
        args=self.GetArguments()
        self.Job=args.job
        self.Tag = self.Job
        if (args.tag): self.Tag += "_" + args.tag
        self.CustomInputs = args.inp
        self.Verbose = args.verb
        self.AutoSub = args.auto

        # NUISANCE Requirements
        # - Output Name
        # - Card File
        self.Out      = args.out
        self.Card     = args.card
        self.Configs  = args.config
        self.Routine  = args.routine
        self.NEvents  = args.nevents
        self.FakeData = args.fakedt
        self.StartThrow = args.startthrow
        self.NThrows = args.nthrows
        self.ThrowString = args.throwstr

        self.Multiple = int(args.multiple);

        # Read setup paths
        self.NUISANCESetupScript = os.environ["NUISANCE_CVMFS_SETUP"]
        self.IFDHCSetupScript    = os.environ["NUISANCE_IFDHC_SETUP"]
        self.PNFS                = os.environ["NUISANCE_PNFS_RESULTS_AREA"]
        self.SUBPREAMBLE         = os.environ["NUISANCE_SUBPREAMBLE"]

        # Setup Standard Job Sub stuff        
        self.SubResource = "DEDICATED"
        if args.resource: self.SubResource = args.resource

        self.SubLifeTime = "24h"
        if args.time: self.SubLifeTime = args.time

        self.SubMemory = "2500MB"
        if args.memory: self.SubMemory = args.memory

        self.LogFile = ""
        if args.log: self.LogFile = args.log

        # Create a UniqueID
        self.UID = "__" + self.Tag + "-"  + date.now().strftime('%Y%m%d') + "-" + str(os.getpid())
        
        # Read output path
        self.OutputPath  = os.path.abspath(self.Out)
        self.OutputFile  = self.OutputPath.split("/")[-1]
        self.OutputDir   = self.OutputPath.replace(self.OutputFile,"")

        # If running on the grid make sure there is a place to store outputs.
        # This is saved to a hashed folder in the pnfs area.
        self.OutputHash = GetHash(self.OutputDir)
        self.OriginalOutputPath = self.OutputPath
        self.OutputPath = (self.PNFS + "/output-" + 
                           self.OutputHash + "/" + self.OutputFile)
        self.OutputFile  = self.OutputPath.split("/")[-1]
        self.OutputDir   = self.OutputPath.replace(self.OutputFile,"")

        if not os.path.isdir(self.OutputDir):
            call(["mkdir", self.OutputDir])

        # Append any input files and the xsec files
        if args.inp:
            # Add normal inputs
            for inps in args.inp:
                self.InputFiles.append(inps)


        # Setup Input Card
        self.CardPath    = os.path.abspath(args.card)
        if (not self.CardPath.endswith(".xml")):
            print "Card file must be XML format!"
            sys.exit(1)

        self.CardFile    = self.CardPath.split("/")[-1]
        self.CardDir     = self.CardPath.replace(self.CardFile,"")

        # Also append input files from card 
        newf = ParseInputFiles(self.CardPath)
        for fi in newf:
            if fi not in self.InputFiles:
                self.InputFiles.append(fi)

        # Now that the input files have been removed, we
        # should make sure we make a -local card
        UpdatePaths(self.CardPath, self.CardPath.replace(".xml","") + "-local.xml")
        self.CardPath = self.CardPath.replace(".xml","") + "-local.xml"
        self.CardFile = self.CardPath.split("/")[-1]
        self.CardDir  = self.CardPath.replace(self.CardFile,"")

        # Now finally we have to update the card path to be on the PNFS area,
        # and we will edit the submission script to copy the card to the pnfs area when running.
        self.InputFiles.append(self.OutputDir + "/" + self.CardFile)

        # Update log file
        if (self.LogFile == ""):
            self.LogFile = self.CardFile.replace(".xml","") + "-output.log"

        # Append any input files and the xsec files
        if args.inp:
            # Add normal inputs
            for inps in args.inp:
                self.InputFiles.append(inps)

        # Setup the main arguments for nuisbayes
        self.Arguments = (" -c " + self.CardFile)
                 
        if self.Configs:
            for conf in self.Configs:
                self.Arguments += " -q " + conf
        
        if (self.Routine):    self.Arguments += " -f " + self.Routine
        if (self.NEvents):    self.Arguments += " -n " + self.NEvents
        if (self.FakeData):   self.Arguments += " -d " + self.FakeData
        
        if (self.StartThrow):  self.Arguments += " -s " + self.StartThrow
        if (self.NThrows):     self.Arguments += " -t " + self.NThrows
        if (self.ThrowString): self.Arguments += " -p " + self.ThrowString
        
        # Setup Scripts
        self.ScriptFile  = self.CardFile.replace(".xml","") + self.UID + ".sh"
        self.ScriptPath  = self.CurDir + "/" + self.ScriptFile
        self.ScriptDir   = self.ScriptPath.replace(self.ScriptFile,"")

        # Setup Standard Job Sub stuff
        self.MetaData.append(self.Job)
        self.MetaData.append(self.Tag)

    #________________________________________
    def LOG(self, out):
        if not self.Verbose: return
        print out

    #________________________________________
    def MakeScript(self):
        self.LOG("Creating setup script.")

        # Open the script
        script = open(self.ScriptPath,"w")
        script.write("#!/bin/sh\n")

        # Setup Options
        script.write("# Setup NUISANCE\n")
        script.write(self.NUISANCESetupScript + "\n")
        script.write(self.IFDHCSetupScript + "\n")
        script.write("\n\n")

        # Add the input files
        script.write("# Make output directory\n")
        script.write("mkdir out\n")
        script.write("cd out\n")
        script.write("\n\n")

        # Copy input files
        script.write("# Copy files here\n")
        for infile in self.InputFiles:
            if infile != infile.split("/")[-1]:
                
                if infile.startswith("/pnfs"):
                    script.write("echo 'Copying " + infile + "' \n")
                    script.write("ifdh cp " +
                                 infile + " ./" + 
                                 infile.split("/")[-1] + "\n")
                elif infile.startswith("/minerva/app"):
                    script.write("cp -v " + 
                                 infile + " ./" +
                                 infile.split("/")[-1] + "\n")

                    
        script.write("\n")
        script.write("# Check copy was okay \n")
        for infile in self.InputFiles:
            script.write("if [ ! -e " + infile.split("/")[-1] + " ]; then exit 1; fi;\n" )
        script.write("\n\n")

        # Run Job
        script.write("# Run Job\n")
        script.write("echo 'Starting nuisance job!' > " + self.LogFile + " \n")
        script.write("RUN=$1 \n")
        command = ("nuissyst " + self.Arguments + 
                   " -o " + self.OutputFile.replace(".root","") + "-$RUN.root" +
                   " >> " + self.LogFile.replace(".log","") + "-$RUN.log 2>&1 \n")
        script.write(command)
        script.write("ifdh cp -D " + self.LogFile.replace(".log","") + "$RUN.log " + self.OutputDir + " \n")
        script.write("\n\n")

        # Remove the input files instead of copying them back
        script.write("# Removing input files \n")
        for infile in self.InputFiles:
            if infile != infile.split("/")[-1]:
                script.write("rm -v " + infile.split("/")[-1] + " \n")

        # Copy the outputs
        script.write("# Copy files back to /pnfs\n")
        script.write("outdir=" + self.OutputDir + "\n")
        script.write("cd out/ \n")
        script.write("for ofile in ./* \n")
        script.write("do\n")
        script.write("echo $ofile \n")
        script.write("  ifdh cp -D  $ofile $outdir/$ofile \n") 
        script.write("done\n")

        
    #________________________________________
    def MakeSubmissionScript(self):
        self.LOG("Creating submission script.")

        # Make submission command
        com = ""

        # If on grid, lots of stuff to setup...
        com =  "jobsub_submit " + self.SUBPREAMBLE
        com += " --resource-provides=usage_model=" + self.SubResource
        com += " --expected-lifetime=" + self.SubLifeTime
        com += " --memory=" + self.SubMemory
        com += " file://" + self.ScriptPath
                    
        # Setup submission script
        subscript = self.ScriptPath.replace(".sh","")+".jobsub"
        f = open(subscript,"w")
        f.write("#!/bin/sh\n")
        f.write(os.environ['NUISANCE_JOBSUB_SETUP'] + "\n")
        f.write("rm -vf " + self.OutputDir + "/" + self.CardFile + " \n")
        f.write("ifdh cp -D " + self.CardPath + " " + self.OutputDir + " \n")
        for i in range(self.Multiple):
            f.write(com + " " + str(i) + "\n")
        f.close()

        # If auto submit run it
        if self.AutoSub:
        
            call(["chmod","+x",os.path.abspath(subscript)])
            proc = Popen([os.path.abspath(subscript)], stdout=PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode

            f =  open(self.ScriptPath.replace(".sh","")+".logsub","w")
            f.write("OUTPUT:\n")
            f.write(out)
            f.write("EXIT CODE:\n")
            f.write(str(exitcode))
            f.close()

        return

    #________________________________________
    def MakeFetchScript(self):
        self.LOG("Creating fetch script.")

        f = open(self.ScriptPath.replace(".sh","")+".fetch","w")
        f.write("#!/bin/sh \n")
        f.write(self.IFDHCSetupScript + "\n")
        f.write("outdir=" + self.OutputDir + "\n")
        f.write("for file in $outdir/* \n")
        f.write("do \n")
        f.write("  ifdh cp -D $file ./ \n")
        f.write("done \n")
        f.close()
