import re
import os
from subprocess import Popen, PIPE
import shlex
import sys


# Comments explaining each steps are coming from tassel bitbucket:
# https://bitbucket.org/tasseladmin/tassel-5-source/wiki/Tassel5GBSv2Pipeline/

# To add: log file to store errors and output

# Pipeline from GBS to SNPs discovery
def run_tassel(tasselValues, bowtie2Values, globalValues):
	global DB_NAME
	global FASTQ_NAME
	global SAM_NAME
	global QUAL_SCORE_NAME
	global JAVA_MEM
	global VCF_OUTPUT_NAME

	# Determine file names
	DB_NAME = tasselValues['prefix']+"_Tags.db"
	FASTQ_NAME = tasselValues['prefix']+"_Tags.fastq.gz"
	SAM_NAME = tasselValues['prefix']+"_TagsAligned.sam"
	QUAL_SCORE_NAME = tasselValues['prefix']+"_QualityScores.tsv"
	JAVA_MEM = "-Xmx" + globalValues['mem'] +"g"
	VCF_OUTPUT_NAME = tasselValues['prefix']+".vcf"

	# Tassel pipeline - from GBS to hapmap
	run_GBSSeqToTagDBPlugin(tasselValues)
	run_TagExportToFastqPlugin(tasselValues)
	run_bowtie(tasselValues, bowtie2Values, globalValues)
	run_SAMToGBSdbPlugin(tasselValues)
	run_DiscoverySNPCallerPluginV2(tasselValues, bowtie2Values)
	run_SNPQualityProfilerPlugin(tasselValues)
	run_UpdateSNPPositionQualityPlugin(tasselValues)
	run_ProductionSNPCallerPluginV2(tasselValues, globalValues)

	print("The pipeline is finished.\n")
	print("The database is stored in " + DB_NAME + "\n")
	print("The output file is " + VCF_OUTPUT_NAME + "\n")


def run_cmd(cmd):
	print("==> Running:\n" + cmd + "\n\n")
	# No need to specify the directory, because we should have cd to it before calling this module !
	with open('GBS2LK_commands.log', 'a') as commandsLog:
		commandsLog.write(cmd + "\n")

	p = Popen(shlex.split(cmd), shell = False)
	output, error = p.communicate()

	if p.returncode != 0:
		print("command failed: %d %s %s" % (p.returncode, output, error))
		print("The pipeline stops here")
		sys.exit()



# GBSSeqToTagDBPlugin takes fastQ files as input (from input folder), identifies tags and the taxa in which they appear, and stores this data to a local database.
# It keeps only good reads having a barcode and a cut site and no N in the useful part of the sequence.
# It trims off the barcodes and truncates sequences that: (1) have a second cut site or (2) read into the common adapter.
def run_GBSSeqToTagDBPlugin(tasselValues):
	global DB_NAME
	global JAVA_MEM
	cmd = "perl " + tasselValues['tasselpath'] + "/run_pipeline.pl " + JAVA_MEM + " -GBSSeqToTagDBPlugin" + \
		  " -e " + tasselValues['enzyme'] + \
		  " -i " + tasselValues['inputdir'] + \
		  " -db " + DB_NAME + \
		  " -k " + tasselValues['keyfile'] + \
		  " -c " + tasselValues['minkmercount'] + \
		  " -kmerLength " + tasselValues['kmerlength'] + \
		  " -minKmerL " + tasselValues["minkmerlength"] + \
		  " -mnQS " + tasselValues['minqs'] + \
		  " -mxKmerNum " + tasselValues['maxkmernum'] + \
		  " -batchSize " + tasselValues['batchsize'] + \
		  " -deleteOldData true -endPlugin"

	run_cmd(cmd)


# TagExportToFastqPlugin retrieves distinct tags stored in the database and reformats them to a FASTQ file that can be read by the Bowtie2 or BWA aligner program. 
# This output file is input to the aligner, which creates a .sam file needed for calling SNPs further down in the GBS analysis pipeline.
# In this script BWA is not implemented yet
def run_TagExportToFastqPlugin(tasselValues):
	global DB_NAME
	global FASTQ_NAME
	cmd = "perl " + tasselValues['tasselpath'] + "/run_pipeline.pl -TagExportToFastqPlugin " + \
		  " -db " + DB_NAME+ \
		  " -c " + tasselValues['minkmercount'] + \
		  " -o " + FASTQ_NAME
	run_cmd(cmd)



# Aligns the Tags in Fastq format to the reference chosen by the user
def run_bowtie(tasselValues, bowtie2Values, globalValues):
	global FASTQ_NAME
	global SAM_NAME

	# Use regex to remove .fasta, or .fa or .fasta.gz
	refName = bowtie2Values['reference']

	# The index is the fasta file name without the extension
	fastaPattern = re.compile("\.fa.*$")
	extensionPosition = fastaPattern.search(refName).start()
	indexName = refName[0:extensionPosition]

	cmdIndex = bowtie2Values['bowtie2path'] + "/bowtie2-build " + bowtie2Values['reference'] + " " + indexName
	run_cmd(cmdIndex)

	cmdAlign = bowtie2Values['bowtie2path']+"/bowtie2 " + \
		  " -p " + globalValues['nbthreads'] + \
		  " --very-sensitive " + \
		  " -x " + indexName + \
		  " -U " + FASTQ_NAME + \
		  " -S " + SAM_NAME
	run_cmd(cmdAlign)



# SAMToGBSdbPlugin reads a SAM file to determine the potential positions of Tags against the reference genome.
# The plugin updates the current database with information on tag cut positions.
# It will throw an error if there are tags found in the SAM file that can not be matched to tags in the database.
def run_SAMToGBSdbPlugin(tasselValues):
	global SAM_NAME
	global DB_NAME

	cmd = "perl " + tasselValues['tasselpath'] + "/run_pipeline.pl -SAMToGBSdbPlugin " + \
		  " -aLen " + tasselValues['alen'] + \
		  " -aProp " + tasselValues['aprop'] + \
		  " -minMAPQ " + tasselValues['minmapq'] + \
		  " -i " + SAM_NAME + \
		  " -db " + DB_NAME + \
		  " -deleteOldData true -endPlugin"
	run_cmd(cmd)


# DiscoverySNPCallerPluginV2 takes a GBSv2 database file as input and identifies SNPs from the aligned tags.
# Tags positioned at the same physical location are aligned against one another, SNPs are called from the aligned tags,
# and the SNP position and allele data are written to the database.
def run_DiscoverySNPCallerPluginV2(tasselValues, bowtie2Values):
	global JAVA_MEM
	global DB_NAME

	cmd = "perl " + tasselValues['tasselpath'] + "/run_pipeline.pl " + JAVA_MEM + " -DiscoverySNPCallerPluginV2 " + \
		  " -db " + DB_NAME + \
		  " -maxTagsCutSite " + tasselValues['maxtagscutsite'] + \
		  " -mnLCov " + tasselValues['mnlcov'] +  \
		  " -mnMAF " + tasselValues['mnmaf'] + \
		  " -ref  " + bowtie2Values['reference'] + \
		  " -deleteOldData true -endPlugin "
	run_cmd(cmd)



# This plugin scores all discovered SNPs for various coverage, depth and genotypic statistics for a given set of taxa. 
# If no taxa are specified, the plugin will score all taxa currently stored in the data base.
# If no taxa file is specified, the plugin uses the taxa stored in the database.
def run_SNPQualityProfilerPlugin(tasselValues):
	global DB_NAME
	global QUAL_SCORE_NAME

	cmd = "perl " + tasselValues['tasselpath'] + "/run_pipeline.pl -SNPQualityProfilerPlugin " + \
		  " -db " + DB_NAME + \
		  " -statFile " + QUAL_SCORE_NAME

	# With taxa file : using only a subset of the taxas (if no taxa file : all the individuals are used, default)
	# -tname is the name in the database of the run with the taxa specified in the taxafile: we use the basename(filename)
	if tasselValues['taxafile'] is not None:
		cmd = cmd + " -taxa " + tasselValues['taxafile'] + \
			  " -tname " + os.path.basename(tasselValues['taxafile'])

	cmd = cmd + " -deleteOldData true -endPlugin"
	run_cmd(cmd)


# UpdateSNPPositionQualityPlugin reads a quality score file to obtain quality score data for positions stored in the snpposition table.
# The quality score file is a user created file that supplies quality scores for SNP positions.
# It is up to the user to determine what values should be associated with each SNP.
# SNPQualityProfilerPlugin output provides data for this analysis, or the user may base quality scores on other data of his/her choice.
def run_UpdateSNPPositionQualityPlugin(tasselValues):
	global DB_NAME
	global QUAL_SCORE_NAME

	cmd = "perl " + tasselValues['tasselpath'] + "/run_pipeline.pl -UpdateSNPPositionQualityPlugin " + \
		  " -db " + DB_NAME + \
		  " -qsFile " + QUAL_SCORE_NAME + \
		  " -endPlugin"
	run_cmd(cmd)


# This plugin converts data from fastq and keyfile to genotypes, then adds these to a genotype file in VCF or HDF5 format. 
# VCF is the default output. An HDF5 file may be requested by using the suffix '.h5' on the file used in the output file parameter.
# Merging of samples to the same HDF5 output file may be accomplished by using the '-ko' option described below. 
def run_ProductionSNPCallerPluginV2(tasselValues, globalValues):
	global DB_NAME
	global JAVA_MEM
	global VCF_OUTPUT_NAME

	cmd = "perl " + tasselValues['tasselpath'] + "/run_pipeline.pl " + JAVA_MEM + " -ProductionSNPCallerPluginV2 " + \
		  " -batchSize " + tasselValues['batchsize'] + \
		  " -db " + DB_NAME + \
		  " -e " + tasselValues['enzyme'] + \
		  " -d " + tasselValues['maxdivergence'] + \
		  " -eR " + tasselValues['avseqerrorrate'] + \
		  " -i " + tasselValues['inputdir'] + \
		  " -k " + tasselValues['keyfile'] + \
		  " -kmerLength " + tasselValues['kmerlength'] + \
		  " -minPosQS " + tasselValues['minposqs'] + \
		  " -mnQS " + tasselValues['minqs'] + \
		  " -o " + VCF_OUTPUT_NAME + \
		  " -endPlugin "
	run_cmd(cmd)
