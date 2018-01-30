# DB name = cfgValues['prefix'] + "Tags.db"

def run_GBSSeqToTagDBPlugin(cfgValues, tasselPath):
	cmd = tasselPath+"run_pipeline.pl -Xmx"+cfgValues['Xmx']+"G -GBSSeqToTagDBPlugin" + \
		  "	-e " + cfgValues['enzyme'] + \
		  " -i " + cfgValues['inputDir'] + \
		  " -db " + cfgValues['prefix'] + "Tags.db" + \
		  " -k " + cfgValues['keyfile'] + \
		  " -c " + cfgValues['minkmercount'] + \
		  " -kmerLength " + cfgValues['kmerlength'] + \
		  " -minKmerL " + cfgValues["minkmerlength"] + \
		  " -mnQS " + cfgValues['minqs'] + \
		  " -mxKmerNum " + cfgValues['maxkmernum'] + \
		  "-batchSize " + cfgValues['batchsize'] + \
		  " -deleteOldData " + \
		  " -endPlugin"
	print(cmd)


def run_tassel(cfgValues, tasselPath):
	run_GBSSeqToTagDBPlugin(cfgValues, tasselPath)

def run_MSTMap(cfgValues, tasselPath):
		print("placeholder MSTMap")

def run_pipeline(cfgValues, tasselPath):
	run_tassel(cfgValues, tasselPath)
	run_MSTMap(cfgValues, tasselPath)
