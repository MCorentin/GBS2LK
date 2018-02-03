#!/usr/bin/env python

import configparser
import sys
import argparse
import os

import tassel_pipeline

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
parser.add_argument("-c","--config_file",help="The configuration file containing all the parameters to use for the pipeline (must be in 'ini' format)")
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
	print(USAGE)
	sys.exit()
if nbRun < 1:
	print("No --run_* arguments detected ! Choose exactly one")
	print(USAGE)
	sys.exit()



# ===============================================================
# 					Parsing the config file
# ===============================================================
print("\n=============================================")
print("Reading the config file: '%s'" % configFileName)
print("=============================================")
configParser.read(configFileName)

#----------------------
# tassel Configuration
#----------------------
# tasselValues is a dictionary to to store all the values of the config file
tasselValues = {}

# configParser library is used to read the .ini file
tasselConfig = configParser['tassel']

tasselValues['tasselpath'] = tasselConfig.get('tasselpath', None)
check_file(tasselValues['tasselpath'], "run_pipeline.pl")

# Tassel Config
tasselValues['inputdir'] = tasselConfig.get('inputdir', None)
check_dir(tasselValues['inputdir'], "inputdir")

tasselValues['keyfile'] = tasselConfig.get('keyfile', None)
check_file(tasselValues['keyfile'], "keyfile")

# Check list of enzymes ? (what if new one appear ?)
tasselValues['enzyme'] = tasselConfig.get('enzyme', None)

# Deal with all the optional fields in the config file
listFields = ('prefix', 'minkmercount', 'minqs', 'kmerlength', 'minkmerlength', 'maxkmernum' ,'batchsize', 'xmx')
listDefaults = ('GBS2LK_', '10', '0', '64', '20', '50000000', '8', '10G')
for (f, d) in zip(listFields, listDefaults):
	tasselValues[f] = get_value_or_default(f, d)


#----------------------
# bowtie2 Configuration
#----------------------
bowtie2Values = {}
bowtie2Config = configParser['bowtie2']

bowtie2Values['bowtie2path'] = bowtie2Config.get('bowtie2path', None)
check_dir(bowtie2Values['bowtie2path'], "bowtie2path")

# Use biopython to check if fasta ? 
bowtie2Values['reference'] = bowtie2Config.get('reference', None)
check_file(bowtie2Values['reference'], "bowtie2 reference")

#----------------------
# global Configuration
#----------------------
globalValues = {}
globalConfig = configParser['global']

globalValues['nbthreads'] = globalConfig.get('nbThreads', 1)

print("Done !")

#----------------------
# Summary of values 
#----------------------
print("\n=============================================")
print("Summary of the values for the pipeline: ")
print("=============================================")
print("-tassel")
for keys,values in tasselValues.items():
	print("\t" + str(keys) + ": " + str(values))

print("-bowtie2")
for keys,values in bowtie2Values.items():
	print("\t" + str(keys) + ": " + str(values))
	
print("-global")
for keys,values in globalValues.items():
	print("\t" + str(keys) + ": " + str(values))

# ===============================================================
# 					Launching the pipeline
# ===============================================================
print("\n=============================================")
print("Starting the pipeline: ")
print("=============================================\n")
if runMode == "PIPELINE":
	tassel_pipeline.run_tassel(tasselValues, bowtie2Values, globalValues)
	#MSTMap_pipeline()
elif runMode == "TASSEL":
	tassel_pipeline.run_tassel(tasselValues, bowtie2Values, globalValues)
else:
	print("Error ! runMode: %s not valid !" % runMode)