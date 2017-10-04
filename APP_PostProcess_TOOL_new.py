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
##State= arcpy.GetParameterAsText(0) #CA
Version = arcpy.GetParameterAsText(0) #'160'
sdFile = arcpy.GetParameterAsText(1)#"D:\sd-files\live\20170801_SouthDakota_170.sd"

#FOR TESTING
##State= "CO"
##Version = "TESTING"
##sdFile = "C:\sd-files\staging\20170725_Wyoming_Yellowstone_1711.sd"

sdState= sdFile.split('_')[1]
##arcpy.AddMessage(sdState)
##print sdState
if sdState == "Wyoming":
	StateFull = 'Wyoming_Yellowstone'
else:
	StateFull = sdState
arcpy.AddMessage("Target State is "+StateFull)
##print StateFull

##stateTar = {'AK': 'Alaska','AL': 'Alabama','AR': 'Arkansas','AS': 'AmericanSamoa','AZ': 'Arizona','CA': 'California','CO': 'Colorado','CT': 'Connecticut','DC': 'DistrictOfColumbia','DE': 'Delaware','FL': 'Florida','GA': 'Georgia','GU': 'Guam','HI': 'Hawaii','IA': 'Iowa','ID': 'Idaho','IL': 'Illinois','IN': 'Indiana','KS': 'Kansas','KY': 'Kentucky','LA': 'Louisiana','MA': 'Massachusetts','MD': 'Maryland','ME': 'Maine','MI': 'Michigan','MN': 'Minnesota','MO': 'Missouri','MP': 'NorthernMarianaIslands','MS': 'Mississippi','MT': 'Montana','NA': 'National','NC': 'NorthCarolina','ND': 'NorthDakota','NE': 'Nebraska','NH': 'NewHampshire','NJ': 'NewJersey','NM': 'NewMexico','NV': 'Nevada','NY': 'NewYork','OH': 'Ohio','OK': 'Oklahoma','OR': 'Oregon','PA': 'Pennsylvania','PR': 'PuertoRico','RI': 'RhodeIsland','SC': 'SouthCarolina','SD': 'SouthDakota','TN': 'Tennessee','TX': 'Texas','UT': 'Utah','VA': 'Virginia','VI': 'VirginIslands','VT': 'Vermont','WA': 'Washington','WI': 'Wisconsin','WV': 'WestVirginia','WY': 'Wyoming_Yellowstone'}
stateDic = { 'Alaska':'AK', 'Alabama':'AL', 'Arkansas':'AR', 'AmericanSamoa':'AS', 'Arizona':'AZ', 'California':'CA', 'Colorado':'CO', 'Connecticut':'CT', 'DistrictOfColumbia':'DC', 'Delaware':'DE', 'Florida':'FL', 'Georgia':'GA', 'Guam':'GU', 'Hawaii':'HI', 'Iowa':'IA', 'Idaho':'ID', 'Illinois':'IL', 'Indiana':'IN', 'Kansas':'KS', 'Kentucky':'KY', 'Louisiana':'LA', 'Massachusetts':'MA', 'Maryland':'MD', 'Maine':'ME', 'Michigan':'MI', 'Minnesota':'MN', 'Missouri':'MO', 'NorthernMarianaIslands':'MP', 'Mississippi':'MS', 'Montana':'MT', 'National':'NA', 'NorthCarolina':'NC', 'NorthDakota':'ND', 'Nebraska':'NE', 'NewHampshire':'NH', 'NewJersey':'NJ', 'NewMexico':'NM', 'Nevada':'NV', 'NewYork':'NY', 'Ohio':'OH', 'Oklahoma':'OK', 'Oregon':'OR', 'Pennsylvania':'PA', 'PuertoRico':'PR', 'RhodeIsland':'RI', 'SouthCarolina':'SC', 'SouthDakota':'SD', 'Tennessee':'TN', 'Texas':'TX', 'Utah':'UT', 'Virginia':'VA', 'VirginIslands':'VI', 'Vermont':'VT', 'Washington':'WA', 'Wisconsin':'WI', 'WestVirginia':'WV', 'Wyoming_Yellowstone':'WY'}
stateAbbr=stateDic[StateFull]

arcpy.AddMessage('--------------------------------')
arcpy.AddMessage("Processing "+StateFull.upper())
arcpy.AddMessage('--------------------------------')

appDirectory = sdFile.split("staging",1)[0:-1]
landHandoffDirectory = appDirectory[0]+"handoff\\lands\\"
gmuHandoffDirectory = appDirectory[0]+"handoff\\gmu\\" #for future gmu coying
stagingDirectory =appDirectory[0]+"staging\\"
oldExtractsDirectory = stagingDirectory+"1lastpublish\\v101\\" #eventually replace with unzipping code block that unzips to a last publish directory
templateDirectory = appDirectory[0]+"mastertemplate\\"
stagingStatePath = stagingDirectory + stateAbbr + '\\' #possibly replace with it own main directory - new publish?

#finding Handoff information for newest target state
landHandoffList = os.listdir(landHandoffDirectory) #list of files like 20170924_NE_Handoff.gdb
for handoffFile in sorted(landHandoffList,reverse=True):
	landTar = handoffFile.split('_')[1]
	if landTar.upper==stateAbbr: #if the handoff state abbreviation is equal to the state abbreviation of the SD file 
		DateStamp_HandoffGDB = handoffFile.split('_')[0]
		HandoffGDB = handoffFile#not a fully needed step really
		arcpy.AddMessage(stateAbbr+ " Handoff GDB located,datestamp : "+DateStamp_HandoffGDB)
##		print stateAbbr+ " Handoff GDB located,datestamp : "+DateStamp_HandoffGDB
		break
arcpy.AddMessage ("\tHANDOFF GDB: "+HandoffGDB)
##print "\tHANDOFF GDB: "+HandoffGDB
handoffGDBpath = landHandoffDirectory+HandoffGDB


gmuList = os.listdir(gmuHandoffDirectory) #list of files like 20170922_NE_GMU.gdb
for gmuFile in sorted(gmuList,reverse=True):
	gmuTar = gmuFile.split('_')[1]
	if gmuTar.upper==stateAbbr:
		DateStamp_GMUGDB = gmuFile.split('_')[0]
		gmuGDB=gmuFile
		arcpy.AddMessage(stateAbbr+ " GMU GDB located,datestamp : "+DateStamp_HandoffGDB)
		break
arcpy.AddMessage ("\tGMU GDB: "+gmuGDB)
gmuGDBpath = gmuHandoffDirectory+gmuGDB

#finding old GDB information
oldPubList = os.listdir(oldExtractsDirectory)
for oldPub in sorted(oldPubList,reverse=True):
	if oldPub.endswith(".gdb"):
		oldState = oldPub.split('_')[1]#20170828_ri_publish.gdb
		if oldState.upper()==stateAbbr:
			DateStamp_OldePublishGDB = oldPub.split('_')[0]
			OldePublishGDB = oldPub#not a fully needed step really
			arcpy.AddMessage(stateAbbr+ " Old Publish GDB located,datestamp : "+DateStamp_OldePublishGDB)
	##		print stateAbbr+ " Old Publish GDB located,datestamp : "+DateStamp_OldePublishGDB
			break
arcpy.AddMessage ("\tOLD GDB: "+OldePublishGDB)
##print "\tOld GDB: "+OldePublishGDB
OldePublishGDBpath = oldExtractsDirectory+OldePublishGDB


#finding old MXD information
oldPubList2 = os.listdir(oldExtractsDirectory)
for oldPub2 in sorted(oldPubList,reverse=True):
	if oldPub2.endswith(".mxd"):
		oldState2 = oldPub.split('_')[1]#20170828_RhodeIsland_1701
		if oldState2 == StateFull:
			DateStamp_OldePublishMXD = oldPub2.split(StateFull)[0]
			Version_OldePublishMXD = (oldPub2.split(StateFull)[1]).split('.')[0]
			OldePublishMXD = oldPub2#not a fully needed step really
			arcpy.AddMessage(StateFull+ " Old Publish MXD located,datestamp : "+DateStamp_OldePublishMXD+",version # : "+Version_OldePublishMXD)
##			print stateAbbr+ " Old Publish MXD located,datestamp : "+DateStamp_OldePublishMXD+",version # : "+Version_OldePublishMXD
			break
arcpy.AddMessage ("\tOLD MXD: "+OldePublishMXD)
##print "\tOld MXD: "+OldePublishMXD
OldePublishMXDpath = oldExtractsDirectory+OldePublishMXD


#finding master template info
templateList = os.listdir(templateDirectory)
for mTemplateMXD in sorted (templateList,reverse=True):
	if mTemplateMXD.endswith('.mxd'):
		Datestamp_MasterPublishTemplate = mTemplateMXD.split('_')[0]#20170516_MasterPublishTemplate
		TemplateMXD = mTemplateMXD#not a fully needed step really
		arcpy.AddMessage("Master Template mxd located, datestamp : "+Datestamp_MasterPublishTemplate)
##		print "Master Template mxd located, datestamp : "+Datestamp_MasterPublishTemplate
		break
#Datestamp_MasterPublishTemplate = #'20160628' - OLD MANUAL ENTRY
arcpy.AddMessage ("\tMASTER TEMPLATE MXD: "+TemplateMXD)
##print "\tMASTER TEMPLATE MXD: "+TemplateMXD
mTemplateMXDpath=templateDirectory+TemplateMXD


for mTemplateGDB in sorted (templateList,reverse=True):
	if mTemplateGDB.endswith('.gdb'):
		Datestamp_MasterPublishTemplate = mTemplateGDB.split('_')[0]
		TemplateGDB = mTemplateGDB#not a fully needed step really
		arcpy.AddMessage("Master Template gdb located, datestamp : "+Datestamp_MasterPublishTemplate)
##		print "Master Template gdb located, datestamp : "+Datestamp_MasterPublishTemplate
		break
#Datestamp_MasterPublishTemplate = #'20160628' - OLD MANUAL ENTRY
arcpy.AddMessage ("\tMASTER TEMPLATE GDB: "+TemplateGDB)
##print "\tMASTER TEMPLATE GDB: "+TemplateGDB
mTemplateGDBpath=templateDirectory+TemplateGDB


today = datetime.date.today()
DateStamp_Today = today.strftime('%Y%m%d')

# SECONDARY variables, which may need to changed/verified (but hopefully not) ahead of running this script
##NetworkDirectory = 'G:/Products/ArcServer/PRODUCTION_DATA/'
##network_path = NetworkDirectory + stateAbbr + '/'
##HandoffDirectory_Network = 'G:/Products/ArcServer/PRODUCTION_DATA/!Handoff/'
##scripting_directory = 'D:/APP/!Scripting/'
##maskclip_gdb = scripting_directory+'ClipMask/ClipMask_Tiger2013.gdb'
#LocalDirectory = 'D:/APP/' -- DEFINED ABOVE
#local_path = appDirectory[0] + stateAbbr + '\\' -- DEFINED ABOVE
##admin_bounds = maskclip_gdb+'/Clip/'+StateFull

# TERTIARY variables, which do not need to be changed/verified ahead of running this script
#OldePublishMXD_Network = oldExtractsDirectory+DateStamp_OldePublishMXD+'_'+StateFull+'_'+Version_OldePublishMXD+'.mxd'  -- NOT NEEDED
#OldePublishMXD = local_path+DateStamp_OldePublishMXD+'_'+StateFull+'_'+Version_OldePublishMXD+'.mxd'  -- DEFINED ABOVE
#OldePublishGDB_Network = oldExtractsDirectory+DateStamp_OldePublishGDB+'_'+stateAbbr+'_Publish.gdb'  -- NOT NEEDED
#OldePublishGDB = local_path+DateStamp_OldePublishGDB+'_'+stateAbbr+'_Publish.gdb'  -- DEFINED ABOVE
#HandoffGDB_Network = HandoffDirectory_Network+DateStamp_HandoffGDB+'_'+stateAbbr+'_Handoff.gdb' -- NOT NEEDED
#HandoffGDB = local_path+DateStamp_HandoffGDB+'_'+stateAbbr+'_Handoff.gdb'  -- DEFINED ABOVE
#TemplateGDB = LocalDirectory+'!MasterPublishTemplate/'+Datestamp_MasterPublishTemplate+'_MasterPublishTemplate.gdb' -- DEFINED ABOVE
#TemplateMXD = LocalDirectory+'!MasterPublishTemplate/'+Datestamp_MasterPublishTemplate+'_MasterPublishTemplate.mxd'  -- DEFINED ABOVE
##PublishGDB = stagingStatePath+DateStamp_Today+'_'+stateAbbr+'_Publish.gdb'
##PublishMXD = stagingStatePath+DateStamp_Today+'_'+StateFull+'_'+Version+'.mxd'


arcpy.AddMessage('--------------------------------')
arcpy.AddMessage('CHECKING PREREQUISITES AND CREATING NEW PUBLISH GEODATABASE')
# Create a folder in the local working directory for the state of interest, if it doesn't already exist
if not arcpy.Exists(stagingStatePath):
	arcpy.CreateFolder_management(stagingDirectory,stateAbbr)
	arcpy.AddMessage(stagingStatePath+' DIRECTORY CREATED, because it did not exist previously')

#create the new publish GDB
arcpy.CreateFileGDB_management(stagingStatePath,DateStamp_Today+'_'+stateAbbr+'_Publish.gdb')
PublishGDBpath = stagingStatePath+DateStamp_Today+'_'+stateAbbr+'_Publish.gdb'
PublishMXDpath = stagingStatePath+DateStamp_Today+'_'+StateFull+'_'+Version+'.mxd' #will be used down in arcpy mapping section

#make sure OldePublishMXD exists
if arcpy.Exists(OldePublishMXDpath):
	arcpy.AddMessage('\tOldePublishMXD already exists, cause it was extracted from SD file')
if not arcpy.Exists(OldePublishMXDpath): 
#	arcpy.Copy_management(OldePublishMXD_Network,OldePublishMXD)  -- should be extracted ahead of time
	arcpy.AddMessage('\tEXTRACT THE SD FILE BEFORE RUNNING THIS SCRIPT') #eventually won't be needed because of unzip code
##	sys.exit()

#make sure OldePublishGDB exists
if arcpy.Exists(OldePublishGDBpath):
	arcpy.AddMessage('\tOldePublishGDB already exists, cause it was extracted from SD file')
if not arcpy.Exists(OldePublishGDBpath): 
#	arcpy.Copy_management(OldePublishGDB_Network,OldePublishGDB)  -- should be extracted ahead of time
	arcpy.AddMessage('\tEXTRACT THE SD FILE BEFORE RUNNING THIS SCRIPT')#eventually won't be needed because of unzip code
##	sys.exit()

#make sure HandoffGDB exists
if arcpy.Exists(handoffGDBpath):
	arcpy.AddMessage('\tHandoffGDB already exists, caused it was synced by GSUTIL')
if not arcpy.Exists(handoffGDBpath): 
##	arcpy.Copy_management(HandoffGDB_Network,HandoffGDB)
	arcpy.AddMessage('\tPlease pull down the newest Handoff Files from GOOGLE STORAGE')
##	sys.exit()
	# Delete HandoffGDB_Network in the future after it is copied local? Just an idea; throwing it out there.

arcpy.AddMessage('CHECKING PREREQUISITES AND CREATING NEW PUBLISH GEODATABASE COMPLETE')
arcpy.AddMessage('--------------------------------')

arcpy.AddMessage('--------------------------------')
arcpy.AddMessage('FEATURE DATASET CREATION')


# Define the feature datasets from the OldePublishGDB which you desire to copy into the HandoffGDB:  ## this should be done in to the new Publish GDB leaving the handoff raw
WebMercator = arcpy.SpatialReference(3857)

### /GMUs/ --- maybe use * in path designation to get both?
##GMUs_OldePublishGDB = OldePublishGDBpath+ '/GMUs' 
##if arcpy.Exists(GMUs_OldePublishGDB):
##	arcpy.CreateFeatureDataset_management(PublishGDBpath, "GMUs", WebMercator)
##	arcpy.AddMessage('/GMUs feature dataset created, becasue it exists in the OldePublishGDB')
####	print '/GMUs feature dataset created, becasue it exists in the OldePublishGDB'
##if not arcpy.Exists(GMUs_OldePublishGDB):
####	print 'No /GMUs found for '+StateFull
##	arcpy.AddMessage('\tNo /GMUs feature dataset (note the "s") found for '+StateFull)
##
### /GMU/
##GMU_OldePublishGDB = OldePublishGDBpath+ '/GMU' 
##if arcpy.Exists(GMU_OldePublishGDB):
##	arcpy.CreateFeatureDataset_management(PublishGDBpath, 'GMUs', WebMercator)
##	arcpy.AddMessage('/GMU feature dataset created, becasue it exists in the OldePublishGDB')
####	print '/GMU feature dataset created, becasue it exists in the OldePublishGDB'
##if not arcpy.Exists(GMU_OldePublishGDB):
##	arcpy.AddMessage('\tNo /GMU feature dataset (note the "s" or lack of) found for '+StateFull)
####	print 'No /GMU found for '+StateFull
##
### /Other/
##Other_OldePublishGDB = OldePublishGDBpath+ '/Other' 
##if arcpy.Exists(Other_OldePublishGDB):
##	arcpy.CreateFeatureDataset_management(PublishGDBpath, "Other", WebMercator)
##	arcpy.AddMessage('/Other feature dataset created, becasue it exists in the OldePublishGDB')
####	print '/Other feature dataset created, becasue it exists in the OldePublishGDB'
##if not arcpy.Exists(Other_OldePublishGDB):
##	arcpy.AddMessage('\tNo /Other feature dataset found for '+StateFull)
####	print 'No /Other found for '+StateFull

# /All the standard groups/

#logic for MT??? -- if stateAbbr.upper == MT: then create HD_Portions
#list all the datasets for the old publish and create them for the new one?

arcpy.CreateFeatureDataset_management(PublishGDBpath, "GMUs", WebMercator)
arcpy.CreateFeatureDataset_management(PublishGDBpath, "Other", WebMercator)
arcpy.CreateFeatureDataset_management(PublishGDBpath, "PrivateParcels", WebMercator)
arcpy.CreateFeatureDataset_management(PublishGDBpath, "GovLands", WebMercator)
arcpy.CreateFeatureDataset_management(PublishGDBpath, "PossibleAccess", WebMercator)
arcpy.AddMessage('/GMUs, /Other, /PrivateParcels, /Govlands and /PossibleAccess feature datasets were created')

arcpy.AddMessage('FEATURE DATASET CREATION COMPLETE')
arcpy.AddMessage('--------------------------------')



arcpy.AddMessage('--------------------------------')
arcpy.AddMessage('COPYING HANDOFF DATA TO THE NEW PUBLISH GDB')
arcpy.env.workspace = handoffGDBpath

parcelDataset = arcpy.ListDatasets('*Private*','feature')
for pParcels in parcelDataset:
	for parcelFeature in arcpy.ListFeatureClasses(feature_dataset=pParcels):
		path2Parcels = os.path.join(arcpy.env.workspace, pParcels, parcelFeature)
		arcpy.FeatureClassToGeodatabase_conversion(path2Parcels,PublishGDBpath+'\\PrivateParcels')
		arcpy.AddMessage('\tCopied Parcels from '+ handoffGDBpath+ ' to:\n'+path2Parcels)


govDataset = arcpy.ListDatasets('*Gov*','feature')
for govLands in govDataset:
	for govFeature in arcpy.ListFeatureClasses(feature_dataset=govLands):
		path2Govs = os.path.join(arcpy.env.workspace, govLands, govFeature)
		arcpy.FeatureClassToGeodatabase_conversion(path2Govs,PublishGDBpath+'\\GovLands')
		arcpy.AddMessage('\tCopied GovLands from '+ handoffGDBpath+ ' to:\n'+path2Govs)


posDataset = arcpy.ListDatasets('*Possible*','feature')
for posAccs in posDataset:
	for posFeature in arcpy.ListFeatureClasses(feature_dataset=posAccs):
		path2Poss = os.path.join(arcpy.env.workspace, posAccs, posFeature)
		arcpy.FeatureClassToGeodatabase_conversion(path2Poss,PublishGDBpath+'\\PossibleAccess')
		arcpy.AddMessage('\tCopied PossibleAccess from '+ handoffGDBpath+ ' to:\n'+path2Poss)


arcpy.AddMessage('COPYING HANDOFF DATA TO THE NEW PUBLISH GDB COMPLETE')
arcpy.AddMessage('--------------------------------')



arcpy.AddMessage('--------------------------------')
arcpy.AddMessage('COPYING HUNT DATA TO THE NEW PUBLISH GDB')
arcpy.env.workspace = handoffGDBpath

#find all the datasets in the GMU gdb and copy them into the dataset in the new publish GDB


arcpy.AddMessage('COPYING HUNT DATA TO THE NEW PUBLISH GDB COMPLETE')
arcpy.AddMessage('--------------------------------')



arcpy.AddMessage('--------------------------------')
arcpy.AddMessage('COPYING SECTIONS AND WILDERNESS FROM LAST PUBLISH')
arcpy.env.workspace = OldePublishGDBpath
##sectionFeatures = [''] + sectionFeatures if sectionFeatures is not None else []

# /PLSS/ -> /Sections/
# If they exist, read from OldePublishGDB and write to HandoffGDB
Sections_OldePublishGDB=OldePublishGDBpath+'/Sections'
if arcpy.Exists(Sections_OldePublishGDB):
	#Create a feature dataset to house the section lines and areas
	arcpy.CreateFeatureDataset_management(PublishGDBpath,'Sections',WebMercator)
	arcpy.AddMessage('/Sections feature dataset created, because it exists in the OldePublishGDB')
	sectionDataset = arcpy.ListDatasets('*Sections*','feature')
	for sections in sectionDataset:
		for sectionFeature in arcpy.ListFeatureClasses(feature_dataset=sections):
			path2Sections = os.path.join(arcpy.env.workspace, sections, sectionFeature)
##			print(path2Sections)
			arcpy.FeatureClassToGeodatabase_conversion(path2Sections,PublishGDBpath+'\\Sections')
			arcpy.AddMessage('\tCopied Sections from '+ OldePublishGDBpath+ ' to:\n'+path2Sections)
if not arcpy.Exists(Sections_OldePublishGDB):
	arcpy.AddMessage('\tNo /Sections found for '+StateFull)
	arcpy.AddMessage('\t\tIs that correct for '+StateFull)

# /Wilderness/
# If they exist, import the wilderness lines and areas into the HandoffGDB from the GIS drive
Wilderness_OldePublishGDB=OldePublishGDBpath+'/Wilderness'
if arcpy.Exists(Wilderness_OldePublishGDB):
	# Create a feature dataset to house the wilderness lines and areas
	arcpy.CreateFeatureDataset_management(PublishGDBpath,"Wilderness",WebMercator)
	arcpy.AddMessage('/Wilderness feature dataset created')
	wildernessDataset = arcpy.ListDatasets('*Wilderness*','feature')
	for wilderness in wildernessDataset:
		for wildernessFeature in arcpy.ListFeatureClasses(feature_dataset=wilderness):
			path2Wilderness = os.path.join(arcpy.env.workspace, wilderness, wildernessFeature)
##			print (path2Wilderness)
			arcpy.FeatureClassToGeodatabase_conversion(path2Wilderness,PublishGDBpath+'\\Wilderness')
			arcpy.AddMessage('\tCopied Wilderness from '+ OldePublishGDBpath+ ' to"\n '+path2Wilderness)
if not arcpy.Exists(Wilderness_OldePublishGDB):
	arcpy.AddMessage('\tNo /Wilderness found for '+StateFull)
	arcpy.AddMessage('\t\tIs that correct for '+StateFull)

arcpy.AddMessage('COPYING SECTIONS AND WILDERNESS FROM LAST PUBLISH COMPLETE')
arcpy.AddMessage('--------------------------------')


arcpy.AddMessage('--------------------------------')
arcpy.AddMessage('GEODATABASE REPLICATION; arcpy.mapping MAGICS')

# Duplicate the HandoffGDB to become the PublishGDB
arcpy.Copy_management(handoffGDBpath,PublishGDBpath)#will this work with an existing GDB there????
arcpy.AddMessage('HandoffGDB duplicated into PublishGDB')


# Arcpy.mapping, bitches!
mxd = arcpy.mapping.MapDocument(mTemplateMXDpath)
mxd.replaceWorkspaces(mTemplateGDBpath, "FILEGDB_WORKSPACE", PublishGDBpath, "FILEGDB_WORKSPACE")

if arcpy.Exists(handoffGDBpath+'/Wilderness/'):
	for lyr in arcpy.mapping.ListLayers(mxd):
		if lyr.name== "Wilderness Boundaries":
			lyr.replaceDataSource(PublishGDBpath, "FILEGDB_WORKSPACE", stateAbbr+'_Wilderness_Boundaries')
		if lyr.name== "Wilderness Areas":
			lyr.replaceDataSource(PublishGDBpath, "FILEGDB_WORKSPACE", stateAbbr+'_Wilderness_Areas')

if arcpy.Exists(handoffGDBpath+'/Sections/'):
	for layer in arcpy.mapping.ListLayers(mxd):
		if layer.name=="Section Boundaries":
			layer.replaceDataSource(PublishGDBpath, "FILEGDB_WORKSPACE",'Section_Boundaries')
		if layer.name=="Section Areas":
			layer.replaceDataSource(PublishGDBpath, "FILEGDB_WORKSPACE",'Section_Areas')

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
