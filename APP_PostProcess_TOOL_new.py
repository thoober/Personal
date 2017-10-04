#-------------------------------------------------------------------------------
# Name:		APP_PostProcess.py
# Purpose:	This script prepares the pieces necessary for a data update. This script creates a folder, 
#					copies in the olde gdb and olde mxd from the GIS drive, copies the data handoff gdb from the ??? drive, 
#					creates and copies applicable feature datasets from the olde gdb to the handoff gdb, 
#					duplicates the handoff gdb to become the publish gdb, and then uses a template mxd to create a new publish gdb.
#					Lastly, this script opens up both the publish mxd and the olde mxd for comparison.		
# Authors:	Ross Carlson, Adam Potts, Landon Snyder, Nate Balding, Tom Hoober
# Created:	July 2014
# Updated:	Sept 2017
# Copyright:	2017 onXmaps
#-------------------------------------------------------------------------------

# Import system modules
import datetime				 					# A time clock
import arcpy										# Import geoprocessing module
from arcpy import env							# From Arcpy, import environmental variable
import os
import sys
arcpy.env.overwriteOutput = True		# Overwrite is turned ON for this script
arcpy.env.outputZFlag = "Disabled"		# Disables Z-values
arcpy.env.outputMFlag = "Disabled"		# Disables M-values

# PRIMARY variables, which must be changed/verified ahead of running this script
State= arcpy.GetParameterAsText(0) #CA
Version = arcpy.GetParameterAsText(1) #'160'
sdFile = arcpy.GetParameterAsText(2)#"D:\sd-files\live\20170801_SouthDakota_170.sd"

#FOR TESTING
##State= "CO"
##Version = "TESTING"
##sdFile = "D:\sd-files\staging\20170904_Colorado_1711.sd"


stateTar = {'AK': 'Alaska','AL': 'Alabama','AR': 'Arkansas','AS': 'AmericanSamoa','AZ': 'Arizona','CA': 'California','CO': 'Colorado','CT': 'Connecticut','DC': 'DistrictOfColumbia','DE': 'Delaware','FL': 'Florida','GA': 'Georgia','GU': 'Guam','HI': 'Hawaii','IA': 'Iowa','ID': 'Idaho','IL': 'Illinois','IN': 'Indiana','KS': 'Kansas','KY': 'Kentucky','LA': 'Louisiana','MA': 'Massachusetts','MD': 'Maryland','ME': 'Maine','MI': 'Michigan','MN': 'Minnesota','MO': 'Missouri','MP': 'NorthernMarianaIslands','MS': 'Mississippi','MT': 'Montana_Yellowstone','NA': 'National','NC': 'NorthCarolina','ND': 'NorthDakota','NE': 'Nebraska','NH': 'NewHampshire','NJ': 'NewJersey','NM': 'NewMexico','NV': 'Nevada','NY': 'NewYork','OH': 'Ohio','OK': 'Oklahoma','OR': 'Oregon','PA': 'Pennsylvania','PR': 'PuertoRico','RI': 'RhodeIsland','SC': 'SouthCarolina','SD': 'SouthDakota','TN': 'Tennessee','TX': 'Texas','UT': 'Utah','VA': 'Virginia','VI': 'VirginIslands','VT': 'Vermont','WA': 'Washington','WI': 'Wisconsin','WV': 'WestVirginia','WY': 'Wyoming_Yellowstone'}
StateFull=stateTar[State]
arcpy.AddMessage('--------------------------------')
arcpy.AddMessage("Processing "+StateFull.upper())
arcpy.AddMessage('--------------------------------')


appDirectory = sdFile.split("staging",1)[0:-1]
landHandoffDirectory = appDirectory[0]+"handoff\\lands\\"
gmuHandoffDirectory = appDirectory[0]+"handoff\\gmu\\"
oldExtractsDirectory = appDirectory[0]+"staging\\1lastpublish\\v101\\"
templateDirectory = appDirectory[0]+"mastertemplate\\"
stagingDirectory =appDirectory[0]+"staging\\"
stagingStatePath = stagingDirectory + State + '\\'

#finding Handoff information for newest target state
landHandoffFiles = os.listdir(landHandoffDirectory)
for targetFile in sorted(landHandoffFiles,reverse=True):
	stateTar = targetFile.split('_')[1]
	if stateTar==State: #if the handoff state is equal to the defined state
		DateStamp_HandoffGDB = targetFile.split('_')[0]
		HandoffGDB = targetFile
		arcpy.AddMessage(State+ " Handoff GDB located,datestamp : "+DateStamp_HandoffGDB)
##		print State+ " Handoff GDB located,datestamp : "+DateStamp_HandoffGDB
		break
#DateStamp_HandoffGDB = '20151104' - OLD MANUAL ENTRY
arcpy.AddMessage ("\tHANDOFF GDB: "+HandoffGDB)
##print "\tHANDOFF GDB: "+HandoffGDB
handoffGDBpath = landHandoffDirectory+HandoffGDB

#finding old GDB information
oldPubList = os.listdir(oldExtractsDirectory)
for oldPub in sorted(oldPubList,reverse=True):
	oldStates = oldPub.split('_')[1]
	if oldStates.upper()==State:
		DateStamp_OldePublishGDB = oldPub.split('_')[0]
		OldePublishGDB = oldPub
		arcpy.AddMessage(State+ " Old Publish GDB located,datestamp : "+DateStamp_OldePublishGDB)
##		print State+ " Old Publish GDB located,datestamp : "+DateStamp_OldePublishGDB
		break
arcpy.AddMessage ("\tOLD GDB: "+OldePublishGDB)
##print "\tOld GDB: "+OldePublishGDB
OldePublishGDBpath = oldExtractsDirectory+OldePublishGDB

#finding old MXD information
oldPubList = os.listdir(oldExtractsDirectory)
for oldPub in sorted(oldPubList,reverse=True):
	oldStates2 = oldPub.split('_')[1]
	if oldStates2==StateFull:
		DateStamp_OldePublishMXD = oldPub.split('_')[0]
		Version_OldePublishMXD = (oldPub.split('_')[2]).split('.')[0]
		OldePublishMXD = oldPub
		arcpy.AddMessage(State+ " Old Publish MXD located,datestamp : "+DateStamp_OldePublishMXD+",version # : "+Version_OldePublishMXD)
##		print State+ " Old Publish MXD located,datestamp : "+DateStamp_OldePublishMXD+",version # : "+Version_OldePublishMXD
		break
arcpy.AddMessage ("\tOLD MXD: "+OldePublishMXD)
##print "\tOld MXD: "+OldePublishMXD
OldePublishMXDpath = oldExtractsDirectory+OldePublishMXD

#finding master template info
templateList = os.listdir(templateDirectory)
for mTemplateMXD in sorted (templateList,reverse=True):
	if mTemplateMXD.endswith('.mxd'):
		Datestamp_MasterPublishTemplate = mTemplateMXD.split('_')[0]
		TemplateMXD = mTemplateMXD
		arcpy.AddMessage("Master Template mxd located, datestamp : "+Datestamp_MasterPublishTemplate)
##		print "Master Template mxd located, datestamp : "+Datestamp_MasterPublishTemplate
		break
#Datestamp_MasterPublishTemplate = #'20160628' - OLD MANUAL ENTRY
arcpy.AddMessage ("\tMASTER TEMPLATE MXD: "+mTemplateMXD)
##print "\tMASTER TEMPLATE MXD: "+mTemplateMXD
mTemplateMXDpath=templateDirectory+mTemplateMXD

for mTemplateGDB in sorted (templateList,reverse=True):
	if mTemplateGDB.endswith('.gdb'):
		Datestamp_MasterPublishTemplate = mTemplateGDB.split('_')[0]
		TemplateGDB = mTemplateGDB
		arcpy.AddMessage("Master Template gdb located, datestamp : "+Datestamp_MasterPublishTemplate)
##		print "Master Template gdb located, datestamp : "+Datestamp_MasterPublishTemplate
		break
#Datestamp_MasterPublishTemplate = #'20160628' - OLD MANUAL ENTRY
arcpy.AddMessage ("\tMASTER TEMPLATE GDB: "+mTemplateGDB)
##print "\tMASTER TEMPLATE GDB: "+mTemplateGDB
mTemplateGDBpath=templateDirectory+mTemplateGDB

today = datetime.date.today()
DateStamp_Today = today.strftime('%Y%m%d')

# SECONDARY variables, which may need to changed/verified (but hopefully not) ahead of running this script
##NetworkDirectory = 'G:/Products/ArcServer/PRODUCTION_DATA/'
##network_path = NetworkDirectory + State + '/'
##HandoffDirectory_Network = 'G:/Products/ArcServer/PRODUCTION_DATA/!Handoff/'
##scripting_directory = 'D:/APP/!Scripting/'
##maskclip_gdb = scripting_directory+'ClipMask/ClipMask_Tiger2013.gdb'
#LocalDirectory = 'D:/APP/' -- DEFINED ABOVE
#local_path = appDirectory[0] + State + '\\' -- DEFINED ABOVE
##admin_bounds = maskclip_gdb+'/Clip/'+StateFull

# TERTIARY variables, which do not need to be changed/verified ahead of running this script
#OldePublishMXD_Network = oldExtractsDirectory+DateStamp_OldePublishMXD+'_'+StateFull+'_'+Version_OldePublishMXD+'.mxd'  -- NOT NEEDED
#OldePublishMXD = local_path+DateStamp_OldePublishMXD+'_'+StateFull+'_'+Version_OldePublishMXD+'.mxd'  -- DEFINED ABOVE
#OldePublishGDB_Network = oldExtractsDirectory+DateStamp_OldePublishGDB+'_'+State+'_Publish.gdb'  -- NOT NEEDED
#OldePublishGDB = local_path+DateStamp_OldePublishGDB+'_'+State+'_Publish.gdb'  -- DEFINED ABOVE
#HandoffGDB_Network = HandoffDirectory_Network+DateStamp_HandoffGDB+'_'+State+'_Handoff.gdb' -- NOT NEEDED
#HandoffGDB = local_path+DateStamp_HandoffGDB+'_'+State+'_Handoff.gdb'  -- DEFINED ABOVE
#TemplateGDB = LocalDirectory+'!MasterPublishTemplate/'+Datestamp_MasterPublishTemplate+'_MasterPublishTemplate.gdb' -- DEFINED ABOVE
#TemplateMXD = LocalDirectory+'!MasterPublishTemplate/'+Datestamp_MasterPublishTemplate+'_MasterPublishTemplate.mxd'  -- DEFINED ABOVE
PublishGDB = stagingStatePath+DateStamp_Today+'_'+State+'_Publish.gdb'
PublishMXD = stagingStatePath+DateStamp_Today+'_'+StateFull+'_'+Version+'.mxd'
WebMercator = arcpy.SpatialReference(3857)

arcpy.AddMessage('--------------------------------')
arcpy.AddMessage('FOLDERS AND GEODATABASE CREATION; DATA COPYING')
# Create a folder in the local working directory for the state of interest, if it doesn't already exist
if not arcpy.Exists(stagingStatePath):
	arcpy.CreateFolder_management(stagingDirectory,State)
	arcpy.AddMessage(stagingStatePath+' DIRECTORY CREATED, because it did not exist previously')

# Copy OldePublishMXD from G:/ to local, if it doesn't exist already
if arcpy.Exists(OldePublishMXDpath):
	arcpy.AddMessage('\tOldePublishMXD already exists, cause it was extracted from SD file')
if not arcpy.Exists(OldePublishMXDpath): 
#	arcpy.Copy_management(OldePublishMXD_Network,OldePublishMXD)  -- should be extracted ahead of time
	arcpy.AddMessage('\tEXTRACT THE SD FILE BEFORE RUNNING THIS SCRIPT')
	
# Copy OldePublishGDB from G:/ to local, if it doesn't exist already
if arcpy.Exists(OldePublishGDBpath):
	arcpy.AddMessage('\tOldePublishGDB already exists, cause it was extracted from SD file')
if not arcpy.Exists(OldePublishGDBpath): 
#	arcpy.Copy_management(OldePublishGDB_Network,OldePublishGDB)  -- should be extracted ahead of time
	arcpy.AddMessage('\tEXTRACT THE SD FILE BEFORE RUNNING THIS SCRIPT')

# Copy the HandoffGDB_Network local to become the HandoffGDB, if it doesn't exist already
if arcpy.Exists(handoffGDBpath):
	arcpy.AddMessage('\tHandoffGDB already exists, caused it was synced by GSUTIL')
if not arcpy.Exists(handoffGDBpath): 
##	arcpy.Copy_management(HandoffGDB_Network,HandoffGDB)
	arcpy.AddMessage('\tPlease pull down the newest Handoff Files from GOOGLE STORAGE')
	# Delete HandoffGDB_Network in the future after it is copied local? Just an idea; throwing it out there.

arcpy.AddMessage('FOLDER AND GEODATABASE CREATION; DATA COPYING COMPLETE')
arcpy.AddMessage('--------------------------------')

arcpy.AddMessage('--------------------------------')
arcpy.AddMessage('FEATURE DATASET/FEATURE CLASS COPYING [OldePublishGDB -> HandoffGDB]')
# Define the feature datasets from the OldePublishGDB which you desire to copy into the HandoffGDB:
# /GMUs/
GMUs_OldePublishGDB = OldePublishGDBpath+ '/GMUs' 
if arcpy.Exists(GMUs_OldePublishGDB):
	arcpy.CreateFeatureDataset_management(handoffGDBpath, "GMUs", WebMercator)
	arcpy.AddMessage('/GMUs feature dataset created, becasue it exists in the OldePublishGDB')
##	print '/GMUs feature dataset created, becasue it exists in the OldePublishGDB'
if not arcpy.Exists(GMUs_OldePublishGDB):
##	print 'No /GMUs found for '+StateFull
	arcpy.AddMessage('\tNo /GMUs feature dataset (note the "s") found for '+StateFull)

# /GMU/
GMU_OldePublishGDB = OldePublishGDBpath+ '/GMU' 
if arcpy.Exists(GMU_OldePublishGDB):
	arcpy.CreateFeatureDataset_management(handoffGDBpath, 'GMUs', WebMercator)
	arcpy.AddMessage('/GMU feature dataset created, becasue it exists in the OldePublishGDB')
##	print '/GMU feature dataset created, becasue it exists in the OldePublishGDB'
if not arcpy.Exists(GMU_OldePublishGDB):
	arcpy.AddMessage('\tNo /GMU feature dataset (note the "s" or lack of) found for '+StateFull)
##	print 'No /GMU found for '+StateFull

# /Other/
Other_OldePublishGDB = OldePublishGDBpath+ '/Other' 
if arcpy.Exists(Other_OldePublishGDB):
	arcpy.CreateFeatureDataset_management(handoffGDBpath, "Other", WebMercator)
	arcpy.AddMessage('/Other feature dataset created, becasue it exists in the OldePublishGDB')
##	print '/Other feature dataset created, becasue it exists in the OldePublishGDB'
if not arcpy.Exists(Other_OldePublishGDB):
	arcpy.AddMessage('\tNo /Other found for '+StateFull)
##	print 'No /Other found for '+StateFull


### /PLSS/ -> /Sections/
### If they exist, read from OldePublishGDB and write to HandoffGDB
##Sections_OldePublishGDB=OldePublishGDBpath+'/Sections'
##if arcpy.Exists(Sections_OldePublishGDB):
##	#Create a feature dataset to house the section lines and areas
##	arcpy.CreateFeatureDataset_management(handoffGDBpath,'Sections',WebMercator)
##	arcpy.AddMessage('/Sections feature dataset created, because it exists in the OldePublishGDB')
####		print '/Sections feature dataset created'
##	OldePublish_SectionBoundaries = OldePublishGDBpath+'/Sections/Section_Boundaries'
##	arcpy.FeatureClassToFeatureClass_conversion(OldePublish_SectionBoundaries, handoffGDBpath+'\\Sections\\','Section_Boundaries')
####		print 'SectionBoundaries feature class copied from OldePublishGDB to HandoffGDB'
##	arcpy.AddMessage('\tSectionBoundaries imported into the HandoffGDB from the Old Publish GDB')
##	OldePublish_SectionAreas = OldePublishGDBpath+'/Sections/Section_Areas'
##	arcpy.FeatureClassToFeatureClass_conversion(OldePublish_SectionAreas, handoffGDBpath+'\\Sections\\','Section_Areas')
####		print 'SectionAreas feature class copied from OldePublishGDB to HandoffGDB'
##	arcpy.AddMessage('\tSectionAreas imported into the HandoffGDB from the Old Publish GDB')
##if not arcpy.Exists(Sections_OldePublishGDB):
##	arcpy.AddMessage('\tNo /Sections found for '+StateFull)
##	arcpy.AddMessage('\t\tIs that correct for '+StateFull)
####	print 'No /Sections found for '+StateFull

# /Wilderness/
# If they exist, import the wilderness lines and areas into the HandoffGDB from the GIS drive
Wilderness_OldePublishGDB=OldePublishGDBpath+'/Wilderness'
if arcpy.Exists(Wilderness_OldePublishGDB):
	# Create a feature dataset to house the wilderness lines and areas
	arcpy.CreateFeatureDataset_management(handoffGDBpath,"Wilderness",WebMercator)
	arcpy.AddMessage('/Wilderness feature dataset created')
##		print '/Wilderness feature dataset created'
	
	Wilderness_Lines_OldePublishGDB=Wilderness_OldePublishGDB+'/'+State+'_Wilderness_Boundaries'
	arcpy.FeatureClassToFeatureClass_conversion(Wilderness_Lines_OldePublishGDB, handoffGDBpath+'\\Wilderness\\', State+'_Wilderness_Boundaries')
	arcpy.AddMessage('\tWilderness lines imported into the HandoffGDB from the Old Publish GDB')
	Wilderness_Areas_OldePublishGDB = Wilderness_OldePublishGDB+'/'+State+'_Wilderness_Areas'
	arcpy.FeatureClassToFeatureClass_conversion(Wilderness_Areas_OldePublishGDB, handoffGDBpath+'\\Wilderness\\', State+'_Wilderness_Areas')
	arcpy.AddMessage('\tWilderness areas imported into the HandoffGDB from the Old Publish GDB')

if not arcpy.Exists(Wilderness_OldePublishGDB):
	arcpy.AddMessage('\tNo \Wilderness found for '+StateFull)
	arcpy.AddMessage('\t\tIs that correct for '+StateFull)
##	print 'No \Wilderness found for '+StateFull

arcpy.AddMessage('FEATURE DATASET/FEATURE CLASS COPYING [OldePublishGDB -> HandoffGDB] COMPLETE')
arcpy.AddMessage('--------------------------------')


arcpy.AddMessage('--------------------------------')
arcpy.AddMessage('GEODATABASE REPLICATION; arcpy.mapping MAGICS')

# Duplicate the HandoffGDB to become the PublishGDB
arcpy.Copy_management(handoffGDBpath,PublishGDB)
arcpy.AddMessage('HandoffGDB duplicated into PublishGDB')


# Arcpy.mapping, bitches!
mxd = arcpy.mapping.MapDocument(mTemplateMXDpath)
mxd.replaceWorkspaces(mTemplateGDBpath, "FILEGDB_WORKSPACE", PublishGDB, "FILEGDB_WORKSPACE")

if arcpy.Exists(handoffGDBpath+'/Wilderness/'):
	for lyr in arcpy.mapping.ListLayers(mxd):
		if lyr.name== "Wilderness Boundaries":
			lyr.replaceDataSource(PublishGDB, "FILEGDB_WORKSPACE", State+'_Wilderness_Boundaries')
		if lyr.name== "Wilderness Areas":
			lyr.replaceDataSource(PublishGDB, "FILEGDB_WORKSPACE", State+'_Wilderness_Areas')

##if arcpy.Exists(handoffGDBpath+'/Sections/'):
##	for layer in arcpy.mapping.ListLayers(mxd):
##		if layer.name=="Section Boundaries":
##			layer.replaceDataSource(PublishGDB, "FILEGDB_WORKSPACE",'Section_Boundaries')
##		if layer.name=="Section Areas":
##			layer.replaceDataSource(PublishGDB, "FILEGDB_WORKSPACE",'Section_Areas')

mxd.saveACopy(PublishMXD)
arcpy.AddMessage('TemplateMXD used to create the new PublishMXD for '+StateFull)
##print 'TemplateMXD used to create the new PublishMXD for '+StateFull

# Open that recently created PublishMXD to begin manual inspection of the data
# And the OldePublishMXD to compare the PublishMXD to
os.startfile(OldePublishMXDpath)
os.startfile(PublishMXD)
arcpy.AddMessage("Wasn't that sweet! Those ArcMaps opened magically all on their own, dude!")

arcpy.AddMessage('GEODATABASE REPLICATION; arcpy.mapping MAGICS COMPLETE')
arcpy.AddMessage('--------------------------------')
