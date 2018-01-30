#!/usr/bin/env python

import configparser
import subprocess
import sys
import argparse
import os


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
		message_and_quit("%s is set to None !\n" % field)
	if not os.access(fileName, os.R_OK):
		message_and_quit("For field '%s': '%s' is not a file or is not readable !\n" % (field, repr(fileName)))

# This function check if "dirName" is a directory
# If not: print a message and exit
# "field" is here to tell the user which field or agument failed
def check_dir(dirName, field):
	if dirName is None:
		message_and_quit("%s is set to None !\n" % field)
	if not os.path.isdir(dirName):
		message_and_quit("For field '%s': '%s' is not a directory !\n" % (field, repr(dirName)))

# This method is used to deal with the optional fields in the "config.ini" file
# If a value is in the config file, it returns the value, or else, it returns the default value
def get_value_or_default(fieldName, default):
	# get() method from configparser allows a fallback value, here it is None
	# /!\ if the key is empty in config.ini the fallback is NOT called, however the prefix is still None because the key is empty
	value = tasselConfig.get(fieldName, None)
	if value == None:
		value = default
		print("No %s found, defaulting to '%s' ...\n" % (fieldName, default))
	return value

# ===============================================================
# 					Parsing the arguments
# ===============================================================
parser = argparse.ArgumentParser(description = 'From GBS to Linkage Map')
parser.add_argument("-c","--config_file",help="The config file containing all the parameters to use for the pipeline")
parser.add_argument("-p","--run_pipeline",help="Run tassel and MSTMap",action="store_true")
parser.add_argument("-t","--run_tassel",help="Run tassel only",action="store_true")

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
	print("Several --run_* arguments detected ! Choose only 1\n")
	sys.exit()
if nbRun < 1:
	print("No --run_* arguments detected ! Choose only 1\n")
	sys.exit()



# ===============================================================
# 					Parsing the config file
# ===============================================================
configParser.read(configFileName)
tasselConfig = configParser['tassel']

prefix = get_value_or_default('prefix', "GBS2LK_")

inputDirName = tasselConfig.get('inputdir', None)
check_dir(inputDirName, "inputdir")

keyFileName = tasselConfig.get('keyfile', None)
check_file(keyFileName, "keyfile")

enzyme = tasselConfig.get('enzyme', None)

minkmercount = int(get_value_or_default('minkmercount', 10))
minQS = int(get_value_or_default('minQS', 0))
kmerLength = int(get_value_or_default('kmerlength', 64))
minkmerlength = int(get_value_or_default('minkmerlength', 20))
maxkmernum = int(get_value_or_default('maxkmernum', 50000000))
batchsize = int(get_value_or_default('batchsize', 8))
