#!/usr/bin/python

import os
import subprocess
import sys
import shutil
from pathlib import Path
from argparse import ArgumentParser
import json

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
parser.add_argument("-s", "--suffix",              help="suffix to be used for output file name", default="_web")
parser.add_argument("-d", "--delete_output_first", help="if specified, content of the output directory will be deleted (cleaned up) before processing", action="store_true")
parser.add_argument("-r", "--rapidcompact_exe",    help="RapidCompact CLI executable", default="rpdx")

pArgs    = parser.parse_args()
argsDict = vars(pArgs)

inputDirectory  = argsDict["inputDirectory"]
outputDirectory = argsDict["outputDirectory"]
outputSuffix    = argsDict["suffix"]
configFile      = argsDict["configFile"]
configFilePath  = Path(configFile)
configName     = configFilePath.stem
cleanupFirst    = pArgs.delete_output_first


def findGltfOutput(outputDir):
    for root, dirs, files in os.walk(outputDir):
        for f in files:
            if Path(f).suffix in ['.gltf', '.glb']:
                return os.path.join(root, f)
    return None


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
collectedExtensions = [".glb", ".gltf", ".vrm", ".stp", ".obj", ".ply", ".fbx", ".usd", ".usdc", ".usda", ".usdz"]

inputFiles = []

for root, dirs, files in os.walk(inputDirectory):
    for file in files:
        if any(map(file.lower().endswith, collectedExtensions)):
            filepath = os.path.join(root, file)
            inputFiles.append(filepath)
            
print("Collected " + str(len(inputFiles)) + " input files from input directory \"" + inputDirectory + "\".")


# rendering configuration
renderConf = {
    "output": {
        "singleImage": {
            "cameraViewVector": [0.5, -0.5, -1]
        }
    },
    "imageWidth": 512,
    "imageHeight": 512,
    "background": "white"
}

#TODO: this may need to be written to a temp folder
with open("render.json", "w") as f:
    json.dump(renderConf, f)

# #############################################################################
# process input files
# #############################################################################

i = 1

for inputFile in inputFiles:
    print("*************************************************************************")
    print("Processing Asset " + str(i) + " / " + str(len(inputFiles)) + ": \"" + inputFile + "\"")
    i += 1

    fpath = Path(inputFile)
    fnameStem = fpath.stem                                           #teapot
    fnamePrefix, ext = os.path.splitext(inputFile)                   #input/subdir/teapot, .glb
    fnamePrefix += outputSuffix
    fnameRel  = os.path.relpath(fnamePrefix, inputDirectory)         #subdir/teapot
    outputDir = os.path.join(outputDirectory, fnameRel)              #output/subdir/teapot
    inputInfoPath  = os.path.join(outputDirectory, fnameRel, fnameStem + '_input.json')
    outputInfoPath = os.path.join(outputDirectory, fnameRel, fnameStem + '_output.json')
    # path written by rpdx
    inputRenderSrcDir  = os.path.join(outputDirectory, fnameRel, 'renderings')
    inputRenderSrcPath = os.path.join(inputRenderSrcDir, 'image.png')
    # desired path
    inputRenderDstPath = os.path.join(outputDirectory, fnameRel, fnameStem + '_input.jpg')
    # path written by rpdx (just using the same as input)
    outputRenderSrcDir  = os.path.join(outputDirectory, fnameRel, 'renderings')
    outputRenderSrcPath = os.path.join(outputRenderSrcDir, 'image.png')
    # desired path
    outputRenderDstPath = os.path.join(outputDirectory, fnameRel, fnameStem + '_output.jpg')

    jointCMD = ""
    errStr   = ""

    try:
        cmdline = [rpdxExe]

        # general settings
        if configFile != "":
            cmdline.append("--read_config")
            cmdline.append(configFile)

        # import
        cmdline.append("-i")
        cmdline.append(inputFile)   
        cmdline.append("-o")
        cmdline.append(outputDir)
        cmdline.append("-r")
        cmdline.append("--write_info")
        cmdline.append(inputInfoPath)
        cmdline.append("--render")
        cmdline.append("render.json")

        # run RapidCompact        
        jointCMD = " ".join(cmdline)
        print(jointCMD)

        if cleanupFirst:
            cleanUp(outputDir)
        else:
            print("No cleanup flag specified, using output directory as-is.")
        out    = subprocess.check_output(cmdline, stderr=subprocess.STDOUT)

        # copy input file rendering
        if Path(inputRenderSrcPath).is_file():
            shutil.copy(inputRenderSrcPath, inputRenderDstPath)
            Path(inputRenderSrcPath).unlink()
            Path(inputRenderSrcDir).rmdir()

    except Exception as e:        
        errStr = e.output.decode()
        print("\n                       CLI Command:\n" + jointCMD)        
        print("\n                       CLI Output:\n"  + e.output.decode())        

    # if process had errors, show them in error log directory
    if "ERROR:" in str(errStr):
        errFileName = inputFile.replace("/", "~").replace("\\", "~").replace(".", "~")
        if not os.path.exists("_errors"):
            os.makedirs("_errors")        
        f = open("_errors/" + errFileName + ".txt", "w")
        f.write(errStr)
        f.close()

    gltfOutputFile = findGltfOutput(outputDir)
    if not gltfOutputFile:
        raise Exception("Could not find gltf output for rendering")

    # Render Output
    try:
        
        cmdline = [rpdxExe]
        cmdline.append("-i")
        cmdline.append(gltfOutputFile)   
        cmdline.append("-o")
        cmdline.append(outputDir)
        cmdline.append("-r")
        cmdline.append("--write_info")
        cmdline.append(outputInfoPath)
        cmdline.append("--render")
        cmdline.append("render.json")

        # run RapidCompact        
        jointCMD = " ".join(cmdline)
        print(jointCMD)

        out    = subprocess.check_output(cmdline, stderr=subprocess.STDOUT)

        # copy input file rendering
        if Path(outputRenderSrcPath).is_file():
            shutil.copy(outputRenderSrcPath, outputRenderDstPath)
            Path(outputRenderSrcPath).unlink()
            Path(outputRenderSrcDir).rmdir()


    except Exception as e:        
        errStr += e.output.decode()
        print("\n                       CLI Command:\n" + jointCMD)        
        print("\n                       CLI Output:\n"  + e.output.decode())        



print("*************************************************************************")
print("Done.")
