#Area Calculator
#script goes to G Production Data and opens parivate parcels, gov lands, possible access layers
#counts the private parcels and logs it
#sums the Area Acres field of gov lands and possible access and logs it
#Tom Hoober - Sept 2017

import arcpy, os, sys, datetime, logging, numpy

#Gather timestamps and old versions#
today = datetime.date.today()
dateStamp = today.strftime('%Y%m%d')
#DateStamp_Today = '20151110' - OLD MANUAL ENTRY

#set up loggging file
logging.basicConfig(level=logging.INFO,
                    filename=dateStamp+'_LandAcres.csv',
                    format=' %(asctime)s,%(levelname)s,%(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


# PRIMARY variables, which must be changed/verified ahead of running this script
#stateTar = ('AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY')
stateTar = ('ND','OK')
tarPath = 'G:/Products/ArcServer/PRODUCTION_DATA/_ToDelete'
tarStates = os.listdir(tarPath)
fullPathGDB = []

for state in stateTar:
	stateFolder=str(tarPath)+"/"+state
	stateFileList=os.listdir(stateFolder)
	for tarFile in stateFileList:
		if tarFile.endswith('.gdb'):
			fullPath = stateFolder+"/"+tarFile
			fullPathGDB.append(fullPath)

govLayers = ('GovLands_All','GovLands_Low','GovLands_Lower','GovLands_Medium')
posLayers = ('MiscAccess','NGO','TimberCompanyPermitAccess','TimberCompanyPublicAccess')
parLayers = ('PrivateParcels_Large','PrivateParcels_Medium','PrivateParcels_Small','PrivateParcels_Xsmall')


for gdb in fullPathGDB:
	logging.info(str(gdb))
	for tarPar in parLayers:
		prLayer = gdb+'/PrivateParcels/'+tarPar
		try:
			parCount=arcpy.GetCount_management(prLayer)
#			print "For "+str(gdb.split('/')[5])+"  "+str(tarPar)+" : "+str(parCount)
			logging.info(str(gdb.split('/')[5])+','+str(tarPar)+','+str(parCount)+',Total Parcels')
		except:
##			print str(gdb.split('/')[5])+"  "+str(tarPar)+"  not found"
			logging.info(str(gdb.split('/')[5])+','+str(tarPar)+ " not found")

logging.info('')
logging.info('SWITCH to GOV LANDS acreage count')
logging.info('')

for gdb in fullPathGDB:
	logging.info(str(gdb))
	for tarGov in govLayers:
		gLayer = gdb+'/GovLands/'+tarGov
		try:
			field = arcpy.da.TableToNumPyArray(gLayer,"AREA_ACRES",skip_nulls=True)
			gSum= field["AREA_ACRES"].sum()
#			print "For "+str(gdb.split('/')[5])+"  "+str(tarGov)+" : "+str(gSum)
		except:
			logging.info(str(gdb.split('/')[5])+','+str(tarGov)+ " not found")
		logging.info(str(gdb.split('/')[5])+','+str(tarGov)+','+str(gSum)+',Acres')

##print "\tSWITCH to Possible Access"
logging.info('')
logging.info('SWITCH to POSSIBLE ACCESS acreage count')
logging.info('')

for gdb in fullPathGDB:
	logging.info(str(gdb))
	for tarPos in posLayers:
		pLayer = gdb+'/PossibleAccess/'+tarPos
		try:
			field = arcpy.da.TableToNumPyArray(pLayer,"AREA_ACRES",skip_nulls=True)
			pSum= field["AREA_ACRES"].sum()
			print "For "+str(gdb.split('/')[5])+" "+str(tarPos)+" : "+str(pSum)
		except:
			logging.info(str(gdb.split('/')[5])+','+str(tarPos)+ " not found")
		logging.info(str(gdb.split('/')[5])+','+str(tarPos)+','+str(pSum)+',Acres')


logging.shutdown()
print "SCRIPT Finished"
