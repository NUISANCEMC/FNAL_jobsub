import xml.etree.ElementTree

NUISANCE_CARD_DIRLIST=["GENIE_DIR"]
NUISANCE_CARD_TYPES=["GENIE"]

def GetConfigs(e):
    configs = {}
    for atype in e.findall('config'):
        for child in atype.keys():
            configs[child] = atype.get(child)
    return configs

def GetInputs(e):
    inputs = {}
    for atype in e.findall('sample'):
        name   = atype.get("name")
        inputf = atype.get("input")
        inputs[name] = inputf
    return inputs

def UpdatePaths(cardfile,newname=""):

    tree = xml.etree.ElementTree.parse(cardfile)
    e    = tree.getroot()

    for atype in e.findall('sample'):
        name   = atype.get("name")
        inputf = atype.get("input")

        inputf = inputf.replace("\/\/","\/")
        inputf = inputf.replace("\/\/","\/")

        # If Joint
        if len(inputf.split(",")) > 1:
            print "JOINT ARG"

            type = inputf.split(":")[0]
            orig = inputf
            notype = inputf.replace(type + ":","")
            notype = notype.replace("(","")
            notype = notype.replace(")","")

            for arg in notype.split(","):
                full = arg
                base = arg.split("/")[-1]
                orig = orig.replace(full,base)

            atype.set("input",orig)

        # else single
        else:
            print "Single Arg"

            # Get full path

            # Replace with TYPE:BASE
            type   = inputf.split(":")[0]
            inputn = inputf.split(":")[1].split("/")[-1]

            atype.set("input", type + ":" + inputn)

    if newname == "":
        newname = cardfile + "-local.xml"
        
    tree.write(newname)

    return


def ParseInputFiles(cardfile):

    tree = xml.etree.ElementTree.parse(cardfile)
    
    e    = tree.getroot()
    conf = GetConfigs(e)
    inp  = GetInputs(e)

    inputfiles = {}
    for ikey in inp:
        jointfile = inp[ikey]
        jointfile = jointfile.replace("(","")
        jointfile = jointfile.replace(")","")
        jointfile = jointfile.replace(",",";")
        jointfile = jointfile.replace("\/\/","\/")
        jointfile = jointfile.replace("\/\/","\/")

        for fullfile in jointfile.split(";"):

            for dirs in NUISANCE_CARD_DIRLIST:
                if dirs in conf:
                    fullfile = fullfile.replace("@" + dirs, conf[dirs])
            for type in NUISANCE_CARD_TYPES:
                fullfile = fullfile.replace(type + ":", "")
            
            fullfile = fullfile.replace("//","/")
            fullfile = fullfile.replace("//","/")
            basefile = fullfile.split("/")[-1]
            inputfiles[fullfile] = basefile

    return inputfiles



