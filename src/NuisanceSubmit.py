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

def GetArguments():

     parser = argparse.ArgumentParser (description = "NUISANCE Job Handler @ FERMILAB",
                                       usage = "./NuisanceSubmit.py <options>")

     required = parser.add_argument_group ("required arguments")
     required.add_argument ("-job",   action = "store", dest = "job", metavar = "[TYPE OF NUIS]", required = True)
     required.add_argument ("-card",   action = "store", dest = "card", metavar = "[PATH TO CARDFILE]", required = True)
     required.add_argument ("-out",    action = "store", dest = "out",  metavar = "[PATH TO OUTPUTFILE]", required = True)
     required.add_argument ("-tag",    action = "store", dest = "tag",  metavar = "[TAG TO IDENTIFY FIT]", required = True)
     required.add_argument ("-site",   action = "store", dest = "site", metavar = "[RUN SITE]", required = True)
     required.add_argument ("-inp",    action = "append", dest = "inp",   metavar = "[PATH TO INPUTFILES]", required = False)
     args, other = parser.parse_known_args()
     
     nuisargs = ' '.join(other)
     
     return args, nuisargs 

if __name__=="__main__":

    args, other = GetArguments()

    print args.card
    print args.out
    print args.tag
    print args.site
    print args.inp
    print other
    
    job = None

    if args.job == "nuiscomp":  job = NuisCompJob(args, other)
    elif args.job == "nuissyst": job = NuisSystJob(args, other)
    elif args.job == "nuismin": job = NuisMinJob(args, other)
    else:
         print "Unknown TYPE!"
         sys.exit(1)
         
    job.MakeScript()
    SubmitJob(job)
