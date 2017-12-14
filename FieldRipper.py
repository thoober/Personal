#Field List 
#script goes to local GMU folder
#logs all the Fields in file by the file name
#Tom Hoober - Dec 2017 - onXmaps

import arcpy, os, sys, datetime, logging, numpy

#Gather timestamps and old versions#
today = datetime.date.today()
dateStamp = today.strftime('%Y%m%d')
#DateStamp_Today = '20151110' - OLD MANUAL ENTRY

#set up loggging file
logging.basicConfig(level=logging.INFO,
                    filename=dateStamp+'_FieldRip.csv',
                    format=' %(asctime)s,%(levelname)s,%(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

logging.info("SCRIPT START")

folderDirectory = "D:\\GS-GMU-upload"
folderList = os.listdir(folderDirectory)
shpFileList = []

for tarState in folderList:
	if len(tarState)==2:
		#print tarState + " is equal to 2"
		statePath = folderDirectory+"\\"+tarState
##		print statePath+ " : Path to Raw files"
		fileList = os.listdir(statePath)
		for shpFile in fileList:
			if shpFile.endswith('.shp'):
##				print "\t"+shpFile
##				print "\t\t"+statePath+"\\"+shpFile
				shpFileList.append(statePath+"\\"+shpFile)
##print shpFileList

for shpFileObj in shpFileList:
	fieldNames = [f.name for f in arcpy.ListFields(shpFileObj)]
	fieldStrList=((str(fieldNames).strip('[]')).replace("u'","")).replace("'","")
##	print "These are the fields for "+shpFileObj
##	print "\t"+fieldStrList+"\n"
	logging.info("STATE :,"+str(shpFileObj.split('\\')[2]))
	logging.info("FILE :,"+shpFileObj.split('\\')[3])
	logging.info("FIELDS :,"+fieldStrList)
	logging.info('')

logging.info("SCRIPT STOP")
logging.shutdown()

