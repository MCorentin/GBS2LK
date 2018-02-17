import re
import subprocess



# Pipeline from GBS to SNPs discovery
def run_tassel(tasselValues, bowtie2Values, globalValues):

	# Determine file names
	DB_NAME = tasselValues['prefix']+"Tags.db"
	FASTQ_NAME = tasselValues['prefix']+"Tags.fastq.gz"
	SAM_NAME = tasselValues['prefix']+"TagsAligned.sam"
	QUAL_SCORE_NAME = tasselValues['prefix']+"_QualityScores.tsv"
	JAVA_MEM = "-Xmx " + globalValues['mem'] + "G"

	run_GBSSeqToTagDBPlugin(tasselValues)
	run_TagExportToFastqPlugin(tasselValues)
	run_bowtie(tasselValues, bowtie2Values, globalValues)
	run_SAMToGBSdbPlugin(tasselValues)
	run_QualityProfilerPlugin(tasselValues)

	
def run_cmd(cmd):
	print(cmd + "\n")


# Read a folder containing the GBS reads
# Creates the Tassel DB from it
def run_GBSSeqToTagDBPlugin(tasselValues):
	cmd = tasselValues['tasselpath'] + " " + JAVA_MEM + " -GBSSeqToTagDBPlugin" + \
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
		  " -deleteOldData " + \
		  " -endPlugin"
	run_cmd(cmd)


# Export the tags to fastq format (for alignment)
def run_TagExportToFastqPlugin(tasselValues):
	cmd = tasselValues['tasselpath'] + " -TagExportToFastqPlugin " + \
		  " -db " + DB_NAME+ \
		  " -c " + tasselValues['minkmercount'] + \
		  " -o " + FASTQ_NAME
	run_cmd(cmd)

	

# Aligns the Tags in Fastq format to the reference chosen by the user
def run_bowtie(tasselValues, bowtie2Values, globalValues):
	# Use regex to remove .fasta, or .fa or .fasta.gz
	refName = bowtie2Values['reference']
	
	# The index is the fasta file name without the extension
	fastaPattern = re.compile("\.fa.*")
	extensionPosition = fastaPattern.search(refName).start()
	indexName = refName[0:extensionPosition]
	
	cmdIndex = bowtie2Values['bowtie2path'] + "/bowtie2-build --threads " + globalValues['nbthreads'] + " " + bowtie2Values['reference'] + " " + indexName
	run_cmd(cmdIndex)
	
	cmdAlign = bowtie2Values['bowtie2path'] + \
		  " -p " + globalValues['nbthreads'] + \
		  " --very-sensitive " + \
		  " -x " + indexName + \
		  " -U " + FASTQ_NAME + \
		  " -S " + SAM_NAME
	run_cmd(cmdAlign)
	
	
# From tassel documentation:
# SAMToGBSdbPlugin reads a SAM file to determine the potential positions of Tags against the reference genome. 
# The plugin updates the current database with information on tag cut positions. 
# It will throw an error if there are tags found in the SAM file that can not be matched to tags in the database.
def run_SAMToGBSdbPlugin(tasselValues):
	print("ADD TO CONFIG INI the aLen, aProp and minMAPQ")
	cmd = tasselValues['tasselpath'] + " -SAMToGBSdbPlugin " + \
		  " -aLen " + \
		  " -aProp " + \
		  " -minMAPQ " + \
		  " -i " + SAM_NAME + \
		  " -db " + DB_NAME + \
		  " -deleteOldData true"
	run_cmd(cmd)	  


def run_QualityProfilerPlugin(tasselValues):
	cmd = tasselValues['tasselpath'] + "QualityProfilerPlugin"


# UpdateSNPPositionQualityPlugin reads a quality score file to obtain quality score data for positions stored in the snpposition table. 
# The quality score file is a user created file that supplies quality scores for SNP positions. 
# It is up to the user to determine what values should be associated with each SNP. 
# SNPQualityProfilerPlugin output provides data for this analysis, or the user may base quality scores on other data of his/her choice.
def run_UpdateSNPPositionQualityPlugin(tasselValues):
	cmd = tasselValues['tasselpath'] + " -UpdateSNPPositionQualityPlugin " + \
		  " -db " + DB_NAME + \
		  " -qsFile " + QUAL_SCORE_NAME + \
		  " -endPlugin "
	run_cmd(cmd)	  
 
  
# DiscoverySNPCallerPluginV2 takes a GBSv2 database file as input and identifies SNPs from the aligned tags. 		
# Tags positioned at the same physical location are aligned against one another, SNPs are called from the aligned tags, 
# and the SNP position and allele data are written to the database.
def run_DiscoverySNPCallerPluginV2(tasselValues, bowtie2Values):
	cmd = tasselValues['tasselpath'] + " " + JAVA_MEM + " -DiscoverySNPCallerPluginV2 " + \
		  " -db " + DB_NAME + \
		  " -deleteOldData -endPlugin "
		  # " -gapAlignRatio " + ADDINI + \
		  # " -maxTagsCutSite " + ADDINI + \
		  # " -mnLCov " + ADDINI +  \
		  # " -mnMAF " + ADDINI + \
		  # " -ref  " + bowtie2Values['reference'] + \
	run_cmd(cmd)