#!/usr/bin/python

import os
import subprocess
import sys
import shutil
from pathlib import Path
from argparse import ArgumentParser


# #############################################################################
# static variables
# #############################################################################

rpdxExe            = "rpdx"
#outputFormats      = ["glb", "gltf"]


# #############################################################################
# argument parsing
# #############################################################################



parser = ArgumentParser()

parser.add_argument("-i", "--inputDirectory",      help="input directory", default="input")
parser.add_argument("-o", "--outputDirectory",     help="output directory", default="output")
parser.add_argument("-c", "--configFile",          help="JSON config file for RapidCompact", default="", required=True)
parser.add_argument("-d", "--delete_output_first", help="if specified, content of the output directory will be deleted (cleaned up) before processing", action="store_true")

pArgs    = parser.parse_args()
argsDict = vars(pArgs)

inputDirectory  = argsDict["inputDirectory"]
outputDirectory = argsDict["outputDirectory"]
configFile      = argsDict["configFile"]
configFilePath  = Path(configFile)
configName     = configFilePath.stem
cleanupFirst    = pArgs.delete_output_first

def cleanUp(outputDirectory):
    if os.path.exists(outputDirectory):
        print("Cleaning up output directory")
        shutil.rmtree(outputDirectory)    
    else:
        print("Output directory doesn't exist yet, no cleanup necessary.")

# #############################################################################
# delete content of output dir, if requested
# #############################################################################
    

# #############################################################################
# recursively collect input files
# #############################################################################

# specify all accepted extensions here (as lower case, other cases will be automatically accepted as well)
collectedExtensions = [".glb", ".gltf", ".stp", ".obj", ".ply", ".fbx", ".usd", ".usdc", ".usda", ".usdz"]

inputFiles = []

for root, dirs, files in os.walk(inputDirectory):
    for file in files:
        if any(map(file.lower().endswith, collectedExtensions)):
            filepath = os.path.join(root, file)
            inputFiles.append(filepath)
            
print("Collected " + str(len(inputFiles)) + " input files from input directory \"" + inputDirectory + "\".")


# #############################################################################
# process input files
# #############################################################################

i = 1

for inputFile in inputFiles:
    print("*************************************************************************")
    print("Processing Asset " + str(i) + " / " + str(len(inputFiles)) + ": \"" + inputFile + "\"")
    i += 1

    fnameStem = Path(inputFile).stem                                                #teapot
    fnamePrefix, ext = os.path.splitext(inputFile)                                  #input/subdir/teapot, .glb
    fnameRel  = os.path.relpath(fnamePrefix, inputDirectory)                        #subdir/teapot
    outFileprefixAux = os.path.join(outputDirectory, fnameRel)                      #output/subdir/teapot
    cmdline = [rpdxExe]

    jointCMD = ""
    errStr   = ""

    try:
        # general settings
        if configFile != "":
            cmdline.append("--read_config")
            cmdline.append(configFile)
                 
        # import
        cmdline.append("-i")
        cmdline.append("\"" + inputFile + "\"")   
        cmdline.append("-o")
        jointOutDirectory = os.path.join(outputDirectory, fnameStem, configName)
        cmdline.append(jointOutDirectory)
        cmdline.append("-r")
     
        # run RapidCompact        
        jointCMD = " ".join(cmdline)
        print(jointCMD)

        if cleanupFirst:
            cleanUp(jointOutDirectory)
        else:
            print("No cleanup flag specified, using output directory as-is.")
        out    = subprocess.run(jointCMD, capture_output=True)
        errStr = out.stderr

    except Exception as e:        
        errStr = e.output.decode()
        print("\n                       CLI Command:\n" + jointCMD)        
        print("\n                       CLI Output:\n"  + errStr)        

    # if process had errors, show them in error log directory
    if "ERROR:" in str(errStr):
        errFileName = inputFile.replace("/", "~").replace("\\", "~").replace(".", "~")
        if not os.path.exists("_errors"):
            os.makedirs("_errors")        
        f = open("_errors/" + errFileName + ".txt", "w")
        f.write(errStr.decode("utf-8"))
        f.close()

print("*************************************************************************")
print("Done.")
