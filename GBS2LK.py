#!/usr/bin/env python

import configparser
import subprocess
import sys
import argparse
import os

import run_tassel

# ===============================================================
# 					Define the functions
# ===============================================================
def message_and_quit(message):
	print(message)
	sys.exit()

# This function check if "fileName" is a file and is readable
# If not: print a message and exit
# "field" is here to tell the user which field or agument failed
def check_file(fileName, field):
	if fileName is None:
		message_and_quit("%s is set to None !" % field)
	if not os.access(fileName, os.R_OK):
		message_and_quit("For field '%s': '%s' is not a file or is not readable !" % (field, repr(fileName)))

# This function check if "dirName" is a directory
# If not: print a message and exit
# "field" is here to tell the user which field or agument failed
def check_dir(dirName, field):
	if dirName is None:
		message_and_quit("%s is set to None !" % field)
	if not os.path.isdir(dirName):
		message_and_quit("For field '%s': '%s' is not a directory !" % (field, repr(dirName)))

# This method is used to deal with the optional fields in the "config.ini" file
# If a value is in the config file, it returns the value, or else, it returns the default value
def get_value_or_default(fieldName, default):
	# get() method from configparser allows a fallback value, here it is None
	# /!\ if the key is empty in config.ini the fallback is NOT called, however the prefix is still None because the key is empty
	value = tasselConfig.get(fieldName, None)
	if value == None:
		value = default
		print("No %s found, defaulting to '%s' ..." % (fieldName, default))
	return value

# ===============================================================
# 					Parsing the arguments
# ===============================================================
parser = argparse.ArgumentParser(description = 'From GBS to Linkage Map')
parser.add_argument("-c","--config_file",help="The config file containing all the parameters to use for the pipeline (must be in 'ini' format)")
parser.add_argument("-t", "--tassel_path",help="Path to tassel 'run_pipeline.pl' (eg /usr/bin/tassel-5-standalone/run_pipeline.pl)")
parser.add_argument("-b", "--bowtie2_path",help="Path to bowtie2 (eg /usr/bin/bowtie2)")
parser.add_argument("-rp","--run_pipeline",help="Run tassel and MSTMap",action="store_true")
parser.add_argument("-rt","--run_tassel",help="Run tassel only",action="store_true")

USAGE = parser.format_usage()
args = parser.parse_args()

configParser = configparser.ConfigParser(allow_no_value=True)
configFileName = ""

# Check if config file exists and is readable
if args.config_file:
	configFileName = args.config_file
else:
	print("--config_file argument is required ! Current value: %s" % args.config_file)
	print(USAGE)
	sys.exit()
check_file(configFileName, "--configFile")


# Check path to tassel 'run_pipeline.pl'
if args.tassel_path:
	tasselPath = args.tassel_path
else:
	print("--tassel_path argument is required ! Current value: %s" % args.tassel_path)
	print(USAGE)
	sys.exit()
check_file(tasselPath, "--tassel_path")


# Check path to bowtie2 
if args.bowtie2_path:
	bowtie2Path = args.bowtie2_path
else:
	print("--bowtie2_path argument is required ! Current value: %s" % args.bowtie2_path)
	print(USAGE)
	sys.exit()
check_dir(bowtie2Path, "--bowtie2_path")


# nbRun is here to check that the user only chose one "--run" method
runMode = ""
nbRun = 0
if args.run_pipeline:
	runMode = "PIPELINE"
	nbRun = nbRun + 1
if args.run_tassel:
	runMode = "TASSEL"
	nbRun = nbRun + 1
if nbRun > 1:
	print("Too many (%i) --run_* arguments detected ! Choose exactly one" % nbRun)
	sys.exit()
if nbRun < 1:
	print("No --run_* arguments detected ! Choose exactly one")
	sys.exit()



# ===============================================================
# 					Parsing the config file
# ===============================================================

print("Reading the config file: '%s'" % configFileName)

# cfgValues is a dictionary to to store all the values of the config file
cfgValues = {}

# confiparser library is used to read the .ini file
configParser.read(configFileName)
tasselConfig = configParser['tassel']

cfgValues['inputdir'] = tasselConfig.get('inputdir', None)
check_dir(cfgValues['inputdir'], "inputdir")

cfgValues['keyfile'] = tasselConfig.get('keyfile', None)
check_file(cfgValues['keyfile'], "keyfile")

# Check list of enzymes ? (what if new one appear ?)
cfgValues['enzyme'] = tasselConfig.get('enzyme', None)

# Deal with all the optional fields in the config file
listFields = ('prefix', 'minkmercount', 'minqs', 'kmerlength', 'minkmerlength', 'maxkmernum' ,'batchsize', 'xmx')
listDefaults = ('GBS2LK_', '10', '0', '64', '20', '50000000', '8', '10G')
for (f, d) in zip(listFields, listDefaults):
	cfgValues[f] = get_value_or_default(f, d)

print("\nValues for the pipeline: ")
for keys,values in cfgValues.items():
	print(str(keys) + ": " + str(values))
print("\n")
	
# ===============================================================
# 					Launching the pipeline
# ===============================================================
if runMode == "PIPELINE":
	run_tassel.run_pipeline(cfgValues, tasselPath, bowtie2Path)
elif runMode == "TASSEL":
	print("placeholder tassel")
else:
	print("Error ! runMode: %s not valid !" % runMode)