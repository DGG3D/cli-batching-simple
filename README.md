# cli-batching-simple
A simple batch processing script for RapidCompact CLI

This script allows you to use RapidCompact CLI on a batch of 3D models, in order to
* create optimized versions of the input models
* render images of input and output (for comparison)
* write JSON stats files of input and output (for comparison)
* can be used to prepare data for the qa-tool (qa-mode)

## Command line use
In case you are not familiar with using a command line, or with the RapidCompact CLI, here are some useful tips:
* On Windows, you can launch a command line window, called *Windows Power Shell*, in your current directory in the Windows explorer by right-clicking into the explorer Windows while pressing the SHIFT key. There should then be a context menu option called "Open PowerShell window here", which you can select to open the PowerShell window where you can type your commands.
* RapidCompact CLI is a powerful CLI tool for enterprise users of RapidCompact. Its documentation is accessible [here](https://rapidcompact.com/doc/cli/index.html).


## Requirements & basic usage

You will need Python 3.x installed to run this script. Note that, in case you have two installations running in parallel (Python 2.x and Python 3.x), all commands may need to be run with "python3" in the beginning, instead of just "python".

To *display help and available options*, use this command:

```
python optimize.py -h
```

To *run* this script, optimizing all assets within directory "input" with default parameters and exporting results to output directory "output", use the following command:
```
python optimize.py
```

### Deleting the output directory first (cleanup)

To start with a cleanup step that deletes the output directory, use the `-d` flag:
```
python optimize.py -d
```

### Using qa-mode to prepare data for the use in the qa-tool

By using the qa-mode the structure of the output directory will differ from the input directory structure (how it is usually). Also the output formats will alwqays be a single .glb file per asset. U can still use all the other settings. To generate these outputs, use the `-q` flag:
```
python optimize.py -q
```

### Creating and using a config file for RapidCompact

There are multiple ways of obtaining a config file for RapidCompact CLI. Basically, such a file is a JSON file that contains [settings](https://rapidcompact.com/doc/cli/latest/Configuration/index.html) for different parts of the 3D processing pipeline, including import / export, optimization, rendering, compression, and more. Depending on the CLI version you have, there may be different settings available, so it's useful to create a fresh config file using the CLI itself, using the following command:
```
rpdx --write_config
```
This will produce a config file called *rpd_config.json*. You can also create a config file and give it a custom name, like in the following example:
```
rpdx --write_config my_web_version_config.json
```
Once you have a config file, you can pass it to the batch process, which will then apply it for all processing runs inside the current batch. To do so, use the `-c` parameter:
```
python optimize.py -c my_web_version_config.json
```

### Advanced options
For an up-to-date listing of advanced parameters, use the following command:
```
python optimize.py -h
```

The list of parameters should be the following:
```
usage: optimize.py [-h] [-i INPUTDIRECTORY] [-o OUTPUTDIRECTORY] [-c CONFIGFILE] [-t TARGET] [-s SUFFIX] [-d] [-q]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUTDIRECTORY, --inputDirectory INPUTDIRECTORY
                        input directory
  -o OUTPUTDIRECTORY, --outputDirectory OUTPUTDIRECTORY
                        output directory
  -c CONFIGFILE, --configFile CONFIGFILE
                        JSON config file for RapidCompact
  -t TARGET, --target TARGET
                        target parameter to be used for RapidCompact -c command (example: 1MB, default: use decimation
                        target from config file)
  -s SUFFIX, --suffix SUFFIX
                        suffix to be used for output file name
  -d, --delete_output_first
                        if specified, content of the output directory will be deleted (cleaned up) before processing
  -q, --qa_mode         if specified, content of the output directory will be adjust to use as input for the qa-tool
```
