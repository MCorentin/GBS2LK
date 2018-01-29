#!/usr/bin/env python

import subprocess
import sys
import argparse
import os


# Add missing parameters + use config file instead of argparse ?
parser = argparse.ArgumentParser(description = 'From GBS to Linkage Map')
parser.add_argument("-r","--reads_folder",help="The folder containing the GBS reads (must be named FLowCellID_lane_.fastq.gz)")
parser.add_argument("-k","--keyfile",help="The GBS key file")
parser.add_argument("-e","--enzyme",help="The enzyme name")
parser.add_argument("-p","--prefix_name",help="The name of the  prefix (used for tassel database, stat file, tassel output)")
parser.add_argument("-l","--kmer_length",help="The length of the kmer to be used for GBSToTags")

args = parser.parse_args()


readsFolder = ""
prefix = "GBS2LK_"

# Argument : --reads_folder
try:
	# Check if argment value is null
	if args.reads_folder:
		readsFolder = args.reads_folder
	else:
		print_error_usage("Please specify the name of the folder containing the GBS reads (--reads_folder)", parser)
	# Check if value is a valid directory
	if not os.path.isdir(readsFolder):
		print_error_usage("Can not read folder: {0}".format(readsFolder), parser)
except TypeError as e:
	print_error_usage("TypeError with --reads_folder ! Is the argument an empty value ?", parser)


if args.prefix:
	prefix = args.prefix
else:
	print "No prefix found, default to " + prefix


# Print an error message and the usage from argparse, then exit:
def print_error_usage(errorMssge, parser):
	print errorMssge + "\n\n"
	print parser.format_usage()
	sys.exit()
