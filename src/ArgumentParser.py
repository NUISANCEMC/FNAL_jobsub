import argparse

def CreateParser(desc, use, job):

    parser = argparse.ArgumentParser (description = desc,
                                      usage = use)
                                      

    reqargs = parser.add_argument_group ("JOB TYPE")
    reqargs.add_argument ("--job",   action="store",  dest="job", metavar=": " + job, required=True)

    jobargs = parser.add_argument_group ("optional job arguments <Default Value if none given>")
    jobargs.add_argument ("--tag", action="store", dest="tag",      
                          help="[ Unique ID Tag ]", metavar="<nuiscomp>",  required=False)
    
    jobargs.add_argument ("--input", action="append", dest="inp",      
                          help="[ Optional input files ]", metavar="<path to input>",  required=False)

    jobargs.add_argument( "--verbose",  action="store_true", dest="verb", 
                          help="[ Extra logging in nuisance_jobsub ]", required=False)

    jobargs.add_argument ("--resource", action="store",      dest="resource", 
                          help="[ Change condor resource ]", metavar="<DEDICATED>", required=False)

    jobargs.add_argument ("--log",      action="store",      dest="log",      
                          metavar="<output.log>", help="[ Set internal logfile name ]", required=False)

    jobargs.add_argument ("--memory",   action="store",      dest="memory",   
                          metavar="<2500MB>", help="[ Condor memory request ]",  required=False)

    jobargs.add_argument ("--time",     action="store",      dest="time",     
                          metavar="<24h>", help="[ Condor time request ]", required=False)

    jobargs.add_argument ("--auto",     action="store_true", dest="auto",     
                          help="[ Auto-run the *.jobsub scripts created. ]", required=False)

    return parser
