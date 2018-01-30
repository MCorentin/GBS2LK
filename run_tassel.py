# DB name = cfgValues['prefix'] + "Tags.db"

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
		  "-batchSize " + cfgValues['batchsize'] + \
		  " -deleteOldData " + \
		  " -endPlugin"
		  
	print('\n')
	print(cmd)
	print('\n')


def run_tassel(cfgValues, tasselPath):
	run_GBSSeqToTagDBPlugin(cfgValues, tasselPath)

def run_MSTMap(cfgValues, tasselPath):
		print("placeholder MSTMap")

def run_pipeline(cfgValues, tasselPath):
	run_tassel(cfgValues, tasselPath)
	run_MSTMap(cfgValues, tasselPath)
