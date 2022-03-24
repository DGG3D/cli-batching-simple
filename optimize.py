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
outputFormats      = ["glb", "gltf"]


# #############################################################################
# argument parsing
# #############################################################################

parser = ArgumentParser()

parser.add_argument("-i", "--inputDirectory",      help="input directory", default="input")
parser.add_argument("-o", "--outputDirectory",     help="output directory", default="output")
parser.add_argument("-c", "--configFile",          help="JSON config file for RapidCompact", default="")
parser.add_argument("-t", "--target",              help="target parameter to be used for RapidCompact -c command (example: 1MB, default: use decimation target from config file)", default="")
parser.add_argument("-s", "--suffix",              help="suffix to be used for output file name", default="_web")
parser.add_argument("-d", "--delete_output_first", help="if specified, content of the output directory will be deleted (cleaned up) before processing", action="store_true")
parser.add_argument("-r", "--rapidcompact_exe",    help="RapidCompact CLI executable", default="rpdx")

pArgs    = parser.parse_args()
argsDict = vars(pArgs)

inputDirectory  = argsDict["inputDirectory"]
outputDirectory = argsDict["outputDirectory"]
outputSuffix    = argsDict["suffix"]
configFile      = argsDict["configFile"]
compactTarget   = argsDict["target"]
outputSuffix    = argsDict["suffix"]
rpdxExe         = argsDict["rapidcompact_exe"]
cleanupFirst    = pArgs.delete_output_first


# #############################################################################
# delete content of output dir, if requested
# #############################################################################

if cleanupFirst:    
    if os.path.exists(outputDirectory):
        print("Cleaning up output directory")
        shutil.rmtree(outputDirectory)    
    else:
        print("Output directory doesn't exist yet, no cleanup necessary.")
else:
    print("No cleanup flag specified, using output directory as-is.")
    

# #############################################################################
# recursively collect input files
# #############################################################################

# specify all accepted extensions here (as lower case, other cases will be automatically accepted as well)
collectedExtensions = [".glb", ".gltf", ".stp", ".obj", ".ply", ".fbx"]

inputFiles = []

dirsToProcess = [inputDirectory]

while dirsToProcess:
    nextInputDir    = dirsToProcess.pop()
    allFilesAndDirs = os.listdir(nextInputDir)      
    for fileOrDir in allFilesAndDirs:
        name = fileOrDir
        combinedName = nextInputDir + "/" + name        
        # file
        if os.path.isfile(combinedName):            
            base, ext = os.path.splitext(combinedName) 
            ext = ext.lower()
            for cExt in collectedExtensions:
                if ext == cExt:
                    inputFiles.append(combinedName)
                    break
        # directory
        else:
            dirsToProcess.append(combinedName)
            
print("Collected " + str(len(inputFiles)) + " input files from input directory \"" + inputDirectory + "\".")


# #############################################################################
# process input files
# #############################################################################

i = 1

for inputFile in inputFiles:
    print("*************************************************************************")
    print("Processing Asset " + str(i) + " / " + str(len(inputFiles)) + ": \"" + inputFile + "\"")
    i += 1
    
    fnameStem = Path(inputFile).stem
    fnamePrefix, ext = os.path.splitext(inputFile)       
    fnameRel  = os.path.relpath(fnamePrefix, inputDirectory)    
    outFileprefixAux = os.path.join(outputDirectory, fnameRel)
    exportFile_statsExport = outFileprefixAux + outputSuffix + ".json"
    exportFile_rendering   = outFileprefixAux + outputSuffix + ".jpg"
    inputFile_statsExport  = outFileprefixAux + "_input.json"
    inputFile_rendering    = outFileprefixAux + "_input.jpg"
    
    cmdline = [rpdxExe]
    
    try:
    
        hasAllExports = True
        for outFileFormat in outputFormats:            
            exportFile = outFileprefixAux + outputSuffix + "-" + outFileFormat + "/" + fnameStem + outputSuffix + "." + outFileFormat       
            if not os.path.isfile(exportFile):
                hasAllExports = False
                break            
    
        # check if results already exist
        if os.path.isfile(inputFile_statsExport) and \
           os.path.isfile(inputFile_rendering)   and \
           os.path.isfile(exportFile_statsExport) and \
           os.path.isfile(exportFile_rendering  ) and \
           hasAllExports:           
           print("=> Results already exist, skipping.")
           continue
    
        # general settings
        if configFile != "":
            cmdline.append("--read_config")
            cmdline.append(configFile)
        
        # rendering settings
        cmdline.append("-s")
        cmdline.append("rendering:cameraViewVector")
        cmdline.append("\"0.5 -0.5 -1\"")
        cmdline.append("-s")
        cmdline.append("rendering:imageWidth")
        cmdline.append("512")
        cmdline.append("-s")
        cmdline.append("rendering:imageHeight")
        cmdline.append("512")
        cmdline.append("-s")
        cmdline.append("rendering:background")
        cmdline.append("vignette")
                 
        # import
        cmdline.append("-i")
        cmdline.append("\"" + inputFile + "\"")
        
        # write stats and rendering for input
        cmdline.append("--write_info")
        cmdline.append("\"" + inputFile_statsExport + "\"")
        cmdline.append("--render_image")
        cmdline.append("\"" + inputFile_rendering + "\"")
        
        # create atlas        
        cmdline.append("-c")
        cmdline.append(compactTarget)
        
        # write stats and rendering for output
        cmdline.append("--render_image")
        cmdline.append("\"" + exportFile_rendering + "\"")
        cmdline.append("--write_info")
        cmdline.append("\"" + exportFile_statsExport + "\"")

        # export to file(s)
        for outFileFormat in outputFormats:  
            exportFile = outFileprefixAux + outputSuffix + "-" + outFileFormat + "/" + fnameStem + outputSuffix + "." + outFileFormat       
            cmdline.append("-e")
            cmdline.append("\"" + exportFile + "\"")
     
        # run RapidCompact        
        jointCMD = " ".join(cmdline)
        out = subprocess.check_output(jointCMD)

    except Exception as e:        
        print("\nERROR: RapidCompact CLI could not be run successfully. Make sure it is installed and that the parameters are correct:\n")
        print("\n                       CLI Command:\n" + jointCMD)
        print("\n                       CLI Output:\n" + e.output.decode())        

print("*************************************************************************")
print("Done.")
