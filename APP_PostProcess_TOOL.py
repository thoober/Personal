#-------------------------------------------------------------------------------
# Name:		APP_PostProcess.py
# Purpose:	This script prepares the pieces necessary for a data update. This script creates a folder, 
#					copies in the olde gdb and olde mxd from the GIS drive, copies the data handoff gdb from the ??? drive, 
#					creates and copies applicable feature datasets from the olde gdb to the handoff gdb, 
#					duplicates the handoff gdb to become the publish gdb, and then uses a template mxd to create a new publish gdb.
#					Lastly, this script opens up both the publish mxd and the olde mxd for comparison.		
# Authors:	Ross Carlson, Adam Potts, Landon Snyder, Nate Balding, Tom Hoober
# Created:	July 2014
# Updated:	September 2016
# Copyright:	2016 onXmaps
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
##State= arcpy.GetParameterAsText(0) #CA
##Version = arcpy.GetParameterAsText(1) #'160'
##sdFile = arcpy.GetParameterAsText(2)#"D:\sd-files\live\20170801_SouthDakota_170.sd"

#FOR TESTING
State= "CO"
Version = "TESTING"
sdFile = "D:\sd-files\live\20170904_Colorado_1711.sd"


stateTar = {'AK': 'Alaska','AL': 'Alabama','AR': 'Arkansas','AS': 'AmericanSamoa','AZ': 'Arizona','CA': 'California','CO': 'Colorado','CT': 'Connecticut','DC': 'DistrictOfColumbia','DE': 'Delaware','FL': 'Florida','GA': 'Georgia','GU': 'Guam','HI': 'Hawaii','IA': 'Iowa','ID': 'Idaho','IL': 'Illinois','IN': 'Indiana','KS': 'Kansas','KY': 'Kentucky','LA': 'Louisiana','MA': 'Massachusetts','MD': 'Maryland','ME': 'Maine','MI': 'Michigan','MN': 'Minnesota','MO': 'Missouri','MP': 'NorthernMarianaIslands','MS': 'Mississippi','MT': 'Montana_Yellowstone','NA': 'National','NC': 'NorthCarolina','ND': 'NorthDakota','NE': 'Nebraska','NH': 'NewHampshire','NJ': 'NewJersey','NM': 'NewMexico','NV': 'Nevada','NY': 'NewYork','OH': 'Ohio','OK': 'Oklahoma','OR': 'Oregon','PA': 'Pennsylvania','PR': 'PuertoRico','RI': 'RhodeIsland','SC': 'SouthCarolina','SD': 'SouthDakota','TN': 'Tennessee','TX': 'Texas','UT': 'Utah','VA': 'Virginia','VI': 'VirginIslands','VT': 'Vermont','WA': 'Washington','WI': 'Wisconsin','WV': 'WestVirginia','WY': 'Wyoming_Yellowstone'}
StateFull=stateTar[State]
arcpy.AddMessage('--------------------------------')
arcpy.AddMessage("Processing "+StateFull.upper())
arcpy.AddMessage('--------------------------------')

appDirectory = sdFile.split("live",1)[0:-1]
landHandoffDirectory = appDirectory[0]+"handoff\\lands\\"
gmuHandoffDirectory = appDirectory[0]+"handoff\\gmu\\"
oldExtractsDirectory = appDirectory[0]+"staging\\v101\\"
templateDirectory = appDirectory[0]+"mastertemplate\\"


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
arcpy.AddMessage ("\tOld GDB: "+OldePublishGDB)
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
arcpy.AddMessage ("\tOld MXD: "+OldePublishMXD)
##print "\tOld MXD: "+OldePublishMXD
OldePublishMXDpath = oldExtractsDirectory+OldePublishMXD

#finding master template info
templateList = os.listdir(templateDirectory)
for mTemplateMXD in sorted (templateList,reverse=True):
	if mTemplateMXD.endswith('.mxd'):
		Datestamp_MasterPublishTemplate = mTemplateMXD.split('_')[0]
		TemplateMXD = mTemplateMXD
		arcpy.AddMessage("\tMaster Template mxd located, datestamp : "+Datestamp_MasterPublishTemplate)
##		print "Master Template mxd located, datestamp : "+Datestamp_MasterPublishTemplate
		break
#Datestamp_MasterPublishTemplate = #'20160628' - OLD MANUAL ENTRY
arcpy.AddMessage ("MASTER TEMPLATE: "+mTemplateMXD)
##print "\tMASTER TEMPLATE MXD: "+mTemplateMXD
mTemplateMXDpath=templateDirectory+mTemplateMXD

for mTemplateGDB in sorted (templateList,reverse=True):
	if mTemplateGDB.endswith('.gdb'):
		Datestamp_MasterPublishTemplate = mTemplateGDB.split('_')[0]
		TemplateGDB = mTemplateGDB
		arcpy.AddMessage("\tMaster Template gdb located, datestamp : "+Datestamp_MasterPublishTemplate)
##		print "Master Template gdb located, datestamp : "+Datestamp_MasterPublishTemplate
		break
#Datestamp_MasterPublishTemplate = #'20160628' - OLD MANUAL ENTRY
arcpy.AddMessage ("MASTER TEMPLATE: "+mTemplateGDB)
##print "\tMASTER TEMPLATE GDB: "+mTemplateGDB
mTemplateGDB=templateDirectory+mTemplateGDB

today = datetime.date.today()
DateStamp_Today = today.strftime('%Y%m%d')

# SECONDARY variables, which may need to changed/verified (but hopefully not) ahead of running this script
##NetworkDirectory = 'G:/Products/ArcServer/PRODUCTION_DATA/'
##network_path = NetworkDirectory + State + '/'
##HandoffDirectory_Network = 'G:/Products/ArcServer/PRODUCTION_DATA/!Handoff/'
##scripting_directory = 'D:/APP/!Scripting/'
##maskclip_gdb = scripting_directory+'ClipMask/ClipMask_Tiger2013.gdb'
#LocalDirectory = 'D:/APP/' -- DEFINED ABOVE
local_path = appDirectory[0] + State + '\\'
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
PublishGDB = local_path+DateStamp_Today+'_'+State+'_Publish.gdb'
PublishMXD = local_path+DateStamp_Today+'_'+StateFull+'_'+Version+'.mxd'
WebMercator = arcpy.SpatialReference(3857)

arcpy.AddMessage('--------------------------------')
arcpy.AddMessage('FOLDERS AND GEODATABASE CREATION; DATA COPYING')
# Create a folder in the local working directory for the state of interest, if it doesn't already exist
if not arcpy.Exists(local_path):
	arcpy.CreateFolder_management(appDirectory[0],State)
	arcpy.AddMessage(local_path+' directory created, because it did not exist previously')

# Copy OldePublishMXD from G:/ to local, if it doesn't exist already
if arcpy.Exists(OldePublishMXD):
	arcpy.AddMessage('OldePublishMXD already exists, so there is no need to copy it local from the GIS drive')
if not arcpy.Exists(OldePublishMXD): 
#	arcpy.Copy_management(OldePublishMXD_Network,OldePublishMXD)  -- should be extracted ahead of time
	arcpy.AddMessage('Please Extract the SD FILES')
	
# Copy OldePublishGDB from G:/ to local, if it doesn't exist already
if arcpy.Exists(OldePublishGDB):
	arcpy.AddMessage('OldePublishGDB already exists, so there is no need to copy it local from the GIS drive')
if not arcpy.Exists(OldePublishGDB): 
#	arcpy.Copy_management(OldePublishGDB_Network,OldePublishGDB)  -- should be extracted ahead of time
	arcpy.AddMessage('Please Extract the SD FILES')

# Copy the HandoffGDB_Network local to become the HandoffGDB, if it doesn't exist already
if arcpy.Exists(HandoffGDB):
	arcpy.AddMessage('HandoffGDB already exists, so there is no need to copy it local from the GIS drive')
if not arcpy.Exists(HandoffGDB): 
##	arcpy.Copy_management(HandoffGDB_Network,HandoffGDB)
	arcpy.AddMessage('Please pull down the newest Handoff Files from google')
	# Delete HandoffGDB_Network in the future after it is copied local? Just an idea; throwing it out there.

arcpy.AddMessage('FOLDER AND GEODATABASE CREATION; DATA COPYING COMPLETE')
arcpy.AddMessage('--------------------------------')

arcpy.AddMessage('--------------------------------')
arcpy.AddMessage('FEATURE DATASET/FEATURE CLASS COPYING [OldePublishGDB -> HandoffGDB]')
# Define the feature datasets from the OldePublishGDB which you desire to copy into the HandoffGDB:
# /GMUs/
GMUs_OldePublishGDB = OldePublishGDB+ '/GMUs' 
if arcpy.Exists(GMUs_OldePublishGDB):
	arcpy.CreateFeatureDataset_management(HandoffGDB, "GMUs", WebMercator)
	arcpy.AddMessage('/"GMUs" feature dataset created, becasue it exists in the OldePublishGDB')
	print '/"GMUs" feature dataset created, becasue it exists in the OldePublishGDB'

# /GMU/
GMU_OldePublishGDB = OldePublishGDB+ '/GMU' 
if arcpy.Exists(GMU_OldePublishGDB):
	arcpy.CreateFeatureDataset_management(HandoffGDB, "GMUs", WebMercator)
	arcpy.AddMessage('/"GMU" feature dataset created, becasue it exists in the OldePublishGDB')
	print '/"GMU" feature dataset created, becasue it exists in the OldePublishGDB'

# /Other/
Other_OldePublishGDB = OldePublishGDB+ '/Other' 
if arcpy.Exists(Other_OldePublishGDB):
	arcpy.CreateFeatureDataset_management(HandoffGDB, "Other", WebMercator)
	arcpy.AddMessage('/"Other" feature dataset created, becasue it exists in the OldePublishGDB')
	print '/"Other" feature dataset created, becasue it exists in the OldePublishGDB'

# /PLSS/ -> /Sections/
# If they exist, read from OldePublishGDB and write to HandoffGDB
OldePublish_SectionLines = OldePublishGDB+'/PLSS/Section_Lines'
OldePublish_BoundaryLines = OldePublishGDB+'/PLSS/Section_Boundaries' #variable added 092016 to handle Boundary used in old data
Handoff_SectionLines  = HandoffGDB+'/Sections/Section_Boundaries'

if arcpy.Exists(OldePublish_SectionLines):
	# Create a feature dataset in the HandoffGDB named 'Sections' into which section areas and boundaries from the OldePublishGDB are going to be clipped
	arcpy.CreateFeatureDataset_management(HandoffGDB, "Sections", WebMercator)
	arcpy.AddMessage('/"Sections" feature dataset created')
	arcpy.FeatureClassToFeatureClass_conversion(OldePublish_SectionLines, HandoffGDB+'/Sections/','SectionBoundaries')
#	arcpy.Clip_analysis(OldePublish_SectionLines, admin_bounds, Handoff_SectionLines)  -- NO MORE CLIPPING
	arcpy.AddMessage('SectionLines feature class copied from OldePublishGDB to HandoffGDB')
	print 'SectionLines feature class copied from OldePublishGDB to HandoffGDB'
if not arcpy.Exists(OldePublish_SectionLines):
	arcpy.AddMessage('\tA "Section" line feature in a "PLSS" feature dataset does not exist in the old GDB.')

if arcpy.Exists(OldePublish_BoundaryLines):    #code block added 092016 to handle Boundary used in old data
	# Create a feature dataset in the HandoffGDB named 'Sections' into which section areas and boundaries from the OldePublishGDB are going to be clipped
	arcpy.CreateFeatureDataset_management(HandoffGDB, "Sections", WebMercator)
	arcpy.FeatureClassToFeatureClass_conversion(OldePublish_BoundaryLines, HandoffGDB+'/Sections/','SectionBoundaries')
	arcpy.AddMessage('/"Sections" feature dataset created')
#	arcpy.Clip_analysis(OldePublish_BoundaryLines, admin_bounds, Handoff_SectionLines)  -- NO MORE CLIPPING
	arcpy.AddMessage('BoundaryLines feature class copied from OldePublishGDB to HandoffGDB')
	print 'BoundaryLines feature class copied from OldePublishGDB to HandoffGDB'
if not arcpy.Exists(OldePublish_BoundaryLines):
	arcpy.AddMessage('\tA "Boundary" line feature in a "PLSS" feature dataset does not exist in the old GDB.')

# If they exist, clip the section boundaries to the state clipping boundary, reading from OldePublishGDB and writing to HandoffGDB
OldePublish_SectionAreas = OldePublishGDB+'/PLSS/Section_Areas'
Handoff_SectionAreas = HandoffGDB+'/Sections/Section_Areas'

if arcpy.Exists(OldePublish_SectionAreas):
	arcpy.CreateFeatureDataset_management(HandoffGDB, "Sections", WebMercator)
	arcpy.AddMessage('/"Sections" feature dataset created')
	arcpy.FeatureClassToFeatureClass_conversion(OldePublish_SectionAreas, HandoffGDB+'/Sections/','SectionAreas')
	print 'SectionAreas feature class copied from OldePublishGDB to HandoffGDB'
#	arcpy.Clip_analysis(OldePublish_SectionAreas, admin_bounds, Handoff_SectionAreas)  -- NO MORE CLIPPING
	#arcpy.AddMessage('SectionAreas feature class copied from OldePublishGDB to HandoffGDB')

# /Sections/ -> /Sections/
# If they exist, clip the section areas to the state clipping boundary, reading from OldePublishGDB and writing to HandoffGDB
OldePublish_SectionLines2 = OldePublishGDB+'/Sections/Section_Lines'
OldePublish_BoundaryLines2 = OldePublishGDB+'/Sections/Section_Boundaries' #variable added 092016 to handle Boundary used in old data
Handoff_SectionLines2  = HandoffGDB+'/Sections/Section_Boundaries'

if arcpy.Exists(OldePublish_SectionLines2):
	# Create a feature dataset in the HandoffGDB named 'Sections' into which section areas and boundaries from the OldePublishGDB are going to be clipped
	arcpy.CreateFeatureDataset_management(HandoffGDB, "Sections", WebMercator)
	arcpy.AddMessage('/"Sections" feature dataset created')
	arcpy.FeatureClassToFeatureClass_conversion(OldePublish_SectionLines2, HandoffGDB+'/Sections/','SectionBoundaries')
	#arcpy.Clip_analysis(OldePublish_SectionLines2, admin_bounds, Handoff_SectionLines2)  -- NO MORE CLIPPING
	arcpy.AddMessage('SectionLines feature class copied from OldePublishGDB to HandoffGDB')
	print 'SectionLines feature class copied from OldePublishGDB to HandoffGDB'
if not arcpy.Exists(OldePublish_SectionLines):
	arcpy.AddMessage('\tA "Section" line feature in a "Sections" feature dataset does not exist in the old GDB.')

if arcpy.Exists(OldePublish_BoundaryLines2):    #code block added 092016 to handle Boundary used in old data
	# Create a feature dataset in the HandoffGDB named 'Sections' into which section areas and boundaries from the OldePublishGDB are going to be clipped
	arcpy.CreateFeatureDataset_management(HandoffGDB, "Sections", WebMercator)
	arcpy.AddMessage('/"Sections" feature dataset created')
	arcpy.FeatureClassToFeatureClass_conversion(OldePublish_BoundaryLines2, HandoffGDB+'/Sections/','SectionBoundaries')
	#arcpy.Clip_analysis(OldePublish_BoundaryLines2, admin_bounds, Handoff_SectionLines2)  -- NO MORE CLIPPING
	arcpy.AddMessage('BoundaryLines feature class copied from OldePublishGDB to HandoffGDB')
	print 'BoundaryLines feature class copied from OldePublishGDB to HandoffGDB'
if not arcpy.Exists(OldePublish_BoundaryLines2):
	arcpy.AddMessage('\tA "Boundary" line feature in a "Sections" feature dataset does not exist in the old GDB.')


# If they exist, clip the section boundaries to the state clipping boundary, reading from OldePublishGDB and writing to HandoffGDB
OldePublish_SectionAreas2 = OldePublishGDB+'/Sections/Section_Areas'
Handoff_SectionAreas2 = HandoffGDB+'/Sections/Section_Areas'

if arcpy.Exists(OldePublish_SectionAreas2):
	arcpy.CreateFeatureDataset_management(HandoffGDB, "Sections", WebMercator)
	arcpy.AddMessage('/"Sections" feature dataset created')
	arcpy.FeatureClassToFeatureClass_conversion(OldePublish_SectionAreas2, HandoffGDB+'/Sections/','SectionAreas')
#	arcpy.Clip_analysis(OldePublish_SectionAreas2, admin_bounds, Handoff_SectionAreas2)  -- NO MORE CLIPPING
	arcpy.AddMessage('SectionAreas feature class copied from OldePublishGDB to HandoffGDB')
	print 'SectionAreas feature class copied from OldePublishGDB to HandoffGDB'


arcpy.AddMessage('FEATURE DATASET/FEATURE CLASS COPYING [OldePublishGDB -> HandoffGDB] COMPLETE')
arcpy.AddMessage('--------------------------------')

arcpy.AddMessage('--------------------------------')
arcpy.AddMessage('WILDERNESS AREAS/BOUNDARIES PROCESSING')

# /Wilderness/
# If they exist, import the wilderness lines and areas into the HandoffGDB from the GIS drive
##Wilderness_Lines = 'G:/Data_State/'+State+'/Wilderness/Complete/'+State+'_Wilderness_Boundaries.shp'
Wilderness_Lines_HandoffGDB = landHandoffDirectory+HandoffGDB+'/Wilderness/'+State+'_Wilderness_Boundaries'
Wilderness_Lines_OldePublishGDB = oldExtractsDirectory+OldePublishGDB+'/Wilderness/'+State+'_Wilderness_Boundaries'
if arcpy.Exists(Wilderness_Lines_OldePublishGDB):
	# Create a feature dataset to house the wilderness lines and areas
	arcpy.CreateFeatureDataset_management(landHandoffDirectory+HandoffGDB,"Wilderness",WebMercator)
	arcpy.AddMessage('/"Wilderness" feature dataset created')
	print "Wilderness feature dataset created"
	arcpy.FeatureClassToFeatureClass_conversion(Wilderness_Lines_OldePublishGDB, landHandoffDirectory+HandoffGDB+'/Wilderness/', State+'_Wilderness_Boundaries')
	arcpy.AddMessage('Wilderness lines imported into the HandoffGDB from the Old Publish GDB')
	print 'Wilderness lines imported into the HandoffGDB from the GIS drive from the Old Publish GDB'
if not arcpy.Exists(Wilderness_Lines_OldePublishGDB):
	arcpy.AddMessage('\tNo Wilderness Lines exist in the old GDB')
	
	
# If they exist, import the wilderness lines and areas into the HandoffGDB from the GIS drive
##Wilderness_Areas = 'G:/Data_State/'+State+'/Wilderness/Complete/'+State+'_Wilderness_Areas.shp'
Wilderness_Areas_HandoffGDB = HandoffGDB+'/Wilderness/'+State+'_Wilderness_Areas'
Wilderness_Areas_OldePublishGDB = OldePublishGDB+'/Wilderness/'+State+'_Wilderness_Areas'
# If they exist, import the wilderness lines and areas into the HandoffGDB from the GIS drive
if arcpy.Exists(Wilderness_Areas_OldePublishGDB):
	arcpy.FeatureClassToFeatureClass_conversion(Wilderness_Areas_OldePublishGDB, HandoffGDB+'/Wilderness/', State+'_Wilderness_Areas')
	arcpy.AddMessage('Wilderness areas imported into the HandoffGDB from the Old Publish GDB')
if not arcpy.Exists(Wilderness_Areas_OldePublishGDB):
	arcpy.AddMessage('\tNo Wilderness Areas exist in the old GDB')

arcpy.AddMessage('WILDERNESS AREAS/BOUNDARIES PROCESSING COMPLETE')
arcpy.AddMessage('--------------------------------')

arcpy.AddMessage('--------------------------------')
arcpy.AddMessage('GEODATABASE REPLICATION; arcpy.mapping MAGICS')

# Duplicate the HandoffGDB to become the PublishGDB
publishDirectory = appDirectory[0]+State
arcpy.Copy_management(landHandoffDirectory+HandoffGDB,PublishGDB)
arcpy.AddMessage('HandoffGDB duplicated into PublishGDB')
##
### Arcpy.mapping, bitches!
##mxd = arcpy.mapping.MapDocument(templateDirectory+mTemplateMXD)
##mxd.replaceWorkspaces(templateDirectory+mTemplateGDB, "FILEGDB_WORKSPACE", PublishGDB, "FILEGDB_WORKSPACE",False)
##
##if arcpy.Exists(HandoffGDB+'/Wilderness/')
##	for lyr in arcpy.mapping.ListLayers(mxd):
##		if lyr.name== "Wilderness Boundaries":
##		   lyr.replaceDataSource(PublishGDB, "FILEGDB_WORKSPACE", State+'_Wilderness_Boundaries')
##		if lyr.name== "Wilderness Areas":
##		   lyr.replaceDataSource(PublishGDB, "FILEGDB_WORKSPACE", State+'_Wilderness_Areas')
##
##if arcpy.Exists(HandoffGDB+'/Sections/')
##	for layer in arpy.mapping.ListLayers(mxd):
##		if layer.name=="Section_Boundaries":
##			layer.replaceDataSource(PublishGDB, "FILEGDB_WORKSPACE",Section_Boundaries)
##		if layer.name=="Section_Areas":
##			layer.replaceDataSource(PublishGDB, "FILEGDB_WORKSPACE",Section_Areas)
##
##mxd.saveACopy(PublishMXD)
##arcpy.AddMessage('TemplateMXD used to create the new PublishMXD for '+StateFull)
####print 'TemplateMXD used to create the new PublishMXD for '+StateFull
##
### Open that recently created PublishMXD to begin manual inspection of the data
### And the OldePublishMXD to compare the PublishMXD to
##os.startfile(oldExtractsDirectory+OldePublishMXD)
##os.startfile(PublishMXD)
##arcpy.AddMessage("Wasn't that sweet! Those ArcMaps opened magically all on their own, dude!")
##
##arcpy.AddMessage('GEODATABASE REPLICATION; arcpy.mapping MAGICS COMPLETE')
##arcpy.AddMessage('--------------------------------')
