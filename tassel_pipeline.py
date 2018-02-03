# DB name = tasselValues['prefix'] + "Tags.db"
# Fastq name = tasselValues['prefix'] + "Tags.fastq.gz"

import re
import subprocess


def run_tassel(tasselValues, bowtie2Values, globalValues):
	run_GBSSeqToTagDBPlugin(tasselValues)
	run_TagExportToFastqPlugin(tasselValues)
	run_bowtie(tasselValues, bowtie2Values, globalValues)


def run_GBSSeqToTagDBPlugin(tasselValues):
	cmd = tasselValues['tasselpath'] + " -Xmx"+tasselValues['xmx']+" -GBSSeqToTagDBPlugin" + \
		  " -e " + tasselValues['enzyme'] + \
		  " -i " + tasselValues['inputdir'] + \
		  " -db " + tasselValues['prefix'] + "Tags.db" + \
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



def run_TagExportToFastqPlugin(tasselValues):
	cmd = tasselValues['tasselpath'] + \
		  " -db " + tasselValues['prefix'] + "Tags.db" + \
		  " -c " + tasselValues['minkmercount'] + \
		  " -o " + tasselValues['prefix'] + "Tags.fastq.gz"
	run_cmd(cmd)

	

def run_bowtie(tasselValues, bowtie2Values, globalValues):
	# Use regex to remove .fasta, or .fa or .fasta.gz
	refName = bowtie2Values['reference']
	
	fastaPattern = re.compile("\.fa.*")
	extensionPosition = fastaPattern.search(refName).start()
	indexName = refName[0:extensionPosition]
	
	cmdIndex = bowtie2Values['bowtie2path'] + "/bowtie2-build --threads " + globalValues['nbthreads'] + " " + bowtie2Values['reference'] + " " + indexName
	run_cmd(cmdIndex)
	
	cmdAlign = bowtie2Values['bowtie2path'] + \
		  " -p " + globalValues['nbthreads'] + \
		  " --very-sensitive " + \
		  " -x " + indexName + \
		  " -U " + tasselValues['prefix']+"Tags.fastq.gz" + \
		  " -S " + tasselValues['prefix']+"TagsAligned.sam"
	run_cmd(cmdAlign)
	
	
def run_cmd(cmd):
	print(cmd + "\n")