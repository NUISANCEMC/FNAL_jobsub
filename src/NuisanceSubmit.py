import pickle
import os
from datetime import datetime as date
import sys
from subprocess import call
import argparse
from JobHandler import *
from NuisCompJob import *
from NuisThrowJob import *
from NuisMinJob import *
from NuisSystJob import *
from GevGenJob import *
from NuisCompJob2 import *
from NuisMinJob2 import *
from NuisSystJob2 import *

def GetArguments():

     parser = argparse.ArgumentParser (description = "NUISANCE Job Handler @ FERMILAB",
                                       usage = "nuisance_jobsub <options>")

     required = parser.add_argument_group ("required arguments")
     required.add_argument ("--job", action = "store", dest = "job", metavar = "[TYPE OF NUIS]", required = True)     

     try:
          args, other = parser.parse_known_args()
          nuisargs = ' '.join(other)
     except:
          print ""
          print "#############################################"
          parser.print_help()
          print "#############################################"
          print ""
          print "Possible job types:"
          print "nuisance_jobsub --job nuiscomp <arguments>"
          print "nuisance_jobsub --job nuismin <arguments>"
          print "nuisance_jobsub --job nuissyst <arguments>"
          print ""
          print "To see job specific arguments, run without arguments."
          print ""
          print "e.g. Print nuiscomp commands"
          print "$ nuisance_jobsub --job nuiscomp"
          print ""
          print "#############################################"
          sys.exit(0)
     
     return args, nuisargs 

if __name__=="__main__":

    args, other = GetArguments()
    
    job = None

    if args.job == "nuiscomp":
         job = NuisCompJob2(args, other)
         job.MakeScript()
         job.MakeSubmissionScript()
         job.MakeFetchScript()
    elif args.job == "nuismin":
         job = NuisMinJob2(args, other)
         job.MakeScript()
         job.MakeSubmissionScript()
         job.MakeFetchScript()
    elif args.job == "nuissyst":
         job = NuisSystJob2(args, other)
         job.MakeScript()
         job.MakeSubmissionScript()
         job.MakeFetchScript()
    
