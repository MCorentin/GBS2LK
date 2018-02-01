# DB name = cfgValues['prefix'] + "Tags.db"
# Fastq name = cfgValues['prefix'] + "Tags.fastq.gz"

def run_GBSSeqToTagDBPlugin(cfgValues, tasselPath):
	cmd = tasselPath + " -Xmx"+cfgValues['xmx']+" -GBSSeqToTagDBPlugin" + \
		  "	-e " + cfgValues['enzyme'] + \
		  " -i " + cfgValues['inputdir'] + \
		  " -db " + cfgValues['prefix'] + "Tags.db" + \
		  " -k " + cfgValues['keyfile'] + \
		  " -c " + cfgValues['minkmercount'] + \
		  " -kmerLength " + cfgValues['kmerlength'] + \
		  " -minKmerL " + cfgValues["minkmerlength"] + \
		  " -mnQS " + cfgValues['minqs'] + \
		  " -mxKmerNum " + cfgValues['maxkmernum'] + \
		  " -batchSize " + cfgValues['batchsize'] + \
		  " -deleteOldData " + \
		  " -endPlugin"
		  
	print('Running GBSSeqToTagDBPlugin...')
	print(cmd)
	print('\n')


def run_TagExportToFastqPlugi(cfgValues, tasselPath):
	cmd = tasselPath + \
		  " -db " + cfgValues['prefix'] + "Tags.db" + \
		  " -c " + cfgValues['minkmercount'] + \
		  " -o " + cfgValues['prefix'] + "Tags.fastq.gz" \

	print('Running TagExportToFastqPlugi...')
	print(cmd)
	print('\n')
	
def run_tassel(cfgValues, tasselPath, bowtie2Path):
	run_GBSSeqToTagDBPlugin(cfgValues, tasselPath)
	run_TagExportToFastqPlugi(cfgValues, tasselPath)
	

def run_MSTMap(cfgValues, tasselPath):
	print("placeholder MSTMap")

def run_pipeline(cfgValues, tasselPath):
	run_tassel(cfgValues, tasselPath)
	run_MSTMap(cfgValues, tasselPath)
