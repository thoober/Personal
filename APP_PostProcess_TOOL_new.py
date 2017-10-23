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
Version = arcpy.GetParameterAsText(0) #'160'
sdFile = arcpy.GetParameterAsText(1)#"C:\onx-syncs\sd-files\live\20171017_Montana_171.sd"
today = datetime.date.today()
DateStamp_Today = today.strftime('%Y%m%d')

###FOR TESTING
##Version = "TESTING"
##sdFile = "C:\\onx-syncs\\sd-files\\live\\20171017_Montana_171.sd"

sdState= sdFile.split('_')[1]
if sdState == "Wyoming":
	StateFull = 'Wyoming_Yellowstone'
else:
	StateFull = sdState
arcpy.AddMessage("Target State is "+StateFull)
##print StateFull

##stateTar = {'AK': 'Alaska','AL': 'Alabama','AR': 'Arkansas','AS': 'AmericanSamoa','AZ': 'Arizona','CA': 'California','CO': 'Colorado','CT': 'Connecticut','DC': 'DistrictOfColumbia','DE': 'Delaware','FL': 'Florida','GA': 'Georgia','GU': 'Guam','HI': 'Hawaii','IA': 'Iowa','ID': 'Idaho','IL': 'Illinois','IN': 'Indiana','KS': 'Kansas','KY': 'Kentucky','LA': 'Louisiana','MA': 'Massachusetts','MD': 'Maryland','ME': 'Maine','MI': 'Michigan','MN': 'Minnesota','MO': 'Missouri','MP': 'NorthernMarianaIslands','MS': 'Mississippi','MT': 'Montana','NA': 'National','NC': 'NorthCarolina','ND': 'NorthDakota','NE': 'Nebraska','NH': 'NewHampshire','NJ': 'NewJersey','NM': 'NewMexico','NV': 'Nevada','NY': 'NewYork','OH': 'Ohio','OK': 'Oklahoma','OR': 'Oregon','PA': 'Pennsylvania','PR': 'PuertoRico','RI': 'RhodeIsland','SC': 'SouthCarolina','SD': 'SouthDakota','TN': 'Tennessee','TX': 'Texas','UT': 'Utah','VA': 'Virginia','VI': 'VirginIslands','VT': 'Vermont','WA': 'Washington','WI': 'Wisconsin','WV': 'WestVirginia','WY': 'Wyoming_Yellowstone'}
stateDic = { 'Alaska':'AK', 'Alabama':'AL', 'Arkansas':'AR', 'AmericanSamoa':'AS', 'Arizona':'AZ', 'California':'CA', 'Colorado':'CO', 'Connecticut':'CT', 'DistrictOfColumbia':'DC', 'Delaware':'DE', 'Florida':'FL', 'Georgia':'GA', 'Guam':'GU', 'Hawaii':'HI', 'Iowa':'IA', 'Idaho':'ID', 'Illinois':'IL', 'Indiana':'IN', 'Kansas':'KS', 'Kentucky':'KY', 'Louisiana':'LA', 'Massachusetts':'MA', 'Maryland':'MD', 'Maine':'ME', 'Michigan':'MI', 'Minnesota':'MN', 'Missouri':'MO', 'NorthernMarianaIslands':'MP', 'Mississippi':'MS', 'Montana':'MT', 'National':'NA', 'NorthCarolina':'NC', 'NorthDakota':'ND', 'Nebraska':'NE', 'NewHampshire':'NH', 'NewJersey':'NJ', 'NewMexico':'NM', 'Nevada':'NV', 'NewYork':'NY', 'Ohio':'OH', 'Oklahoma':'OK', 'Oregon':'OR', 'Pennsylvania':'PA', 'PuertoRico':'PR', 'RhodeIsland':'RI', 'SouthCarolina':'SC', 'SouthDakota':'SD', 'Tennessee':'TN', 'Texas':'TX', 'Utah':'UT', 'Virginia':'VA', 'VirginIslands':'VI', 'Vermont':'VT', 'Washington':'WA', 'Wisconsin':'WI', 'WestVirginia':'WV', 'Wyoming_Yellowstone':'WY'}
stateAbbr=stateDic[StateFull]
##arcpy.AddMessage(stateAbbr)

syncDirectory = sdFile.split("sd-files",1)[0] #C:\\onx-syncs\\
landHandoffDirectory = syncDirectory+"handoff\\lands\\"
gmuHandoffDirectory = syncDirectory+"handoff\\gmus\\" #for future gmu coying
templateDirectory = syncDirectory+"automation\\mastertemplate\\"
stagingDirectory ="D:\\"
##stagingDirectory="C:\\D\\" #in place for testing purposes, use line above for production
sdFolderExtractName = (sdFile.split('\\')[-1]).split(".")[0] #20171017_Ohio_171
oldExtractsDirectory = stagingDirectory+"extracted\\"+sdFolderExtractName+"\\V101\\"#eventually replace with unzipping code block that unzips to a last publish directory
stagingStatePath = stagingDirectory + stateAbbr + '\\' #possibly replace with it own main directory - new publish?

##print syncDirectory
##print landHandoffDirectory
##print gmuHandoffDirectory
##print templateDirectory
##print oldExtractsDirectory
##print stagingStatePath

arcpy.AddMessage('--------------------------------')
arcpy.AddMessage("Processing "+StateFull.upper())
arcpy.AddMessage('--------------------------------')

#finding Handoff information for newest target state
if arcpy.Exists(landHandoffDirectory):
	landHandoffList = os.listdir(landHandoffDirectory) #list of files like 20170924_NE_Handoff.gdb
	for handoffFile in sorted(landHandoffList,reverse=True):
		landTar = handoffFile.split('_')[1]
	#	arcpy.AddMessage (landTar+" is what is in the lands handoff")
	#	arcpy.AddMessage (stateAbbr+ " is what the target state is")
		if landTar.upper()==stateAbbr: #if the handoff state abbreviation is equal to the state abbreviation of the SD file 
			DateStamp_HandoffGDB = handoffFile.split('_')[0]
			arcpy.AddMessage(DateStamp_HandoffGDB)
			HandoffGDB = handoffFile
			arcpy.AddMessage ("\tHANDOFF GDB: "+HandoffGDB)
			arcpy.AddMessage(stateAbbr+ " Handoff GDB located,datestamp : "+DateStamp_HandoffGDB)
			##print stateAbbr+ " Handoff GDB located,datestamp : "+DateStamp_HandoffGDB
			break
arcpy.AddMessage ("\tHANDOFF GDB: "+HandoffGDB)
##print "\tHANDOFF GDB: "+HandoffGDB
handoffGDBpath = landHandoffDirectory+HandoffGDB
arcpy.AddMessage('\t\t'+handoffGDBpath)
##print "\t\t"+handoffGDBpath


##if arcpy.Exists(gmuHandoffDirectory):
##	gmuList = os.listdir(gmuHandoffDirectory) #list of files like 20170922_NE_GMU.gdb
##	for gmuFile in sorted(gmuList,reverse=True):
##		gmuTar = gmuFile.split('_')[1]
##		if gmuTar.upper()==stateAbbr:
##			DateStamp_GMUGDB = gmuFile.split('_')[0]
##			gmuGDB=gmuFile
##			arcpy.AddMessage(stateAbbr+ " GMU GDB located,datestamp : "+DateStamp_HandoffGDB)
##			break
##	arcpy.AddMessage ("\tGMU GDB: "+gmuFile)
##	gmuGDBpath = gmuHandoffDirectory+gmuFile

#finding old GDB information
if arcpy.Exists(oldExtractsDirectory):
	oldPubList = os.listdir(oldExtractsDirectory)
	for oldPub in oldPubList:
		if oldPub.endswith(".gdb"):
			DateStamp_OldePublishGDB = oldPub.split('_')[0]
			OldePublishGDB = oldPub
			arcpy.AddMessage(stateAbbr+ " Old Publish GDB located, datestamp : "+DateStamp_OldePublishGDB)
			##print stateAbbr+ " Old Publish GDB located,datestamp : "+DateStamp_OldePublishGDB
			break
	arcpy.AddMessage ("\tOLD GDB: "+OldePublishGDB)
	##print "\tOld GDB: "+OldePublishGDB
	OldePublishGDBpath = oldExtractsDirectory+OldePublishGDB
	arcpy.AddMessage ('\t\t'+OldePublishGDBpath)
	##print '\t\t'+OldePublishGDBpath
if not arcpy.Exists(oldExtractsDirectory):
	arcpy.AddMessage('\tEXTRACT THE SD FILES BEFORE RUNNING THIS SCRIPT')
	sys.exit()


#finding old MXD information
oldPubList2 = os.listdir(oldExtractsDirectory)
for oldPub2 in oldPubList2:
	if oldPub2.endswith(".mxd"):
		#arcpy.AddMessage(oldState2()+"(from Extract) is equal to "+stateAbbr+ " (from the SD file)")
		#arcpy.AddMessage(oldPub2+" this is the target")
		DateStamp_OldePublishMXD = oldPub2.split('_')[0]
		Version_OldePublishMXD = (oldPub2.split('_')[2]).split('.')[0]
		OldePublishMXD = oldPub2
		arcpy.AddMessage(StateFull+ " Old Publish MXD located, datestamp : "+DateStamp_OldePublishMXD+", version # : "+Version_OldePublishMXD)
		##print StateFull+ " Old Publish MXD located,datestamp : "+DateStamp_OldePublishMXD+",version # : "+Version_OldePublishMXD
		break
arcpy.AddMessage ("\tOLD MXD: "+OldePublishMXD)
##print "\tOld MXD: "+OldePublishMXD
OldePublishMXDpath = oldExtractsDirectory+OldePublishMXD
arcpy.AddMessage ('\t\t'+OldePublishMXDpath)
##print '\t\t'+OldePublishMXDpath


#finding master template info
if arcpy.Exists(templateDirectory):
	templateList = os.listdir(templateDirectory)
	for mTemplateMXD in sorted (templateList,reverse=True):
		if mTemplateMXD.endswith('.mxd'):
			Datestamp_MasterPublishTemplate = mTemplateMXD.split('_')[0]#20170516_MasterPublishTemplate
			TemplateMXD = mTemplateMXD
			arcpy.AddMessage("Master Template mxd located, datestamp : "+Datestamp_MasterPublishTemplate)
			##print "Master Template mxd located, datestamp : "+Datestamp_MasterPublishTemplate
			break
#Datestamp_MasterPublishTemplate = #'20160628' - OLD MANUAL ENTRY
arcpy.AddMessage ("\tMASTER TEMPLATE MXD: "+mTemplateMXD)
##print "\tMASTER TEMPLATE MXD: "+TemplateMXD
mTemplateMXDpath=templateDirectory+mTemplateMXD
arcpy.AddMessage('\t\t'+mTemplateMXDpath)
##print '\t\t'+mTemplateMXDpath
if not arcpy.Exists (templateDirectory):
	arcpy.AddMessage("The Master Template Directory is not where it is expected, which is here \n\t+"+templateDirectory)
	sys.exit()

for mTemplateGDB in sorted (templateList,reverse=True):
	if mTemplateGDB.endswith('.gdb'):
		Datestamp_MasterPublishTemplate = mTemplateGDB.split('_')[0]
		TemplateGDB = mTemplateGDB
		arcpy.AddMessage("Master Template gdb located, datestamp : "+Datestamp_MasterPublishTemplate)
		##print "Master Template gdb located, datestamp : "+Datestamp_MasterPublishTemplate
		break
#Datestamp_MasterPublishTemplate = #'20160628' - OLD MANUAL ENTRY
arcpy.AddMessage ("\tMASTER TEMPLATE GDB: "+mTemplateGDB)
##print "\tMASTER TEMPLATE GDB: "+TemplateGDB
mTemplateGDBpath=templateDirectory+mTemplateGDB
arcpy.AddMessage('\t\t'+mTemplateGDBpath)
##print '\t\t'+mTemplateGDBpath


arcpy.AddMessage('--------------------------------')
arcpy.AddMessage('NEW GDB CREATION & FEATURE DATASET CREATION')
# Create a folder in the local working directory for the state of interest, if it doesn't already exist
if not arcpy.Exists(stagingStatePath):
	arcpy.CreateFolder_management(stagingDirectory,stateAbbr)
	arcpy.AddMessage(stagingStatePath+' DIRECTORY CREATED, because it did not exist previously')

#create the new publish GDB
arcpy.CreateFileGDB_management(stagingStatePath, DateStamp_Today+'_'+stateAbbr+'_Publish.gdb')
PublishGDBpath = stagingStatePath+DateStamp_Today+'_'+stateAbbr+'_Publish.gdb'
PublishMXDpath = stagingStatePath+DateStamp_Today+'_'+StateFull+'_'+Version+'.mxd' #will be used down in arcpy mapping section
arcpy.AddMessage("Created new publish GDB : "+DateStamp_Today+'_'+stateAbbr+'_Publish.gdb')

# Define the feature datasets from the OldePublishGDB which you desire to copy into the HandoffGDB:  ## this should be done in to the new Publish GDB leaving the handoff raw
WebMercator = arcpy.SpatialReference(3857)

arcpy.env.workspace = OldePublishGDBpath
##print "Creating FEATURE DATASETS"
arcpy.AddMessage("Creating FEATURE DATASETS")
for oldFeatureDataset in arcpy.ListDatasets(feature_type='Feature'):
	arcpy.CreateFeatureDataset_management(PublishGDBpath, oldFeatureDataset, WebMercator)
	arcpy.AddMessage("/t"+oldFeatureDataset+" being created in \n\t\t"+PublishGDBpath)
	##print "/t"+oldFeatureDataset+" being created in \n\t\t"+PublishGDBpath

arcpy.AddMessage('NEW GDB CREATION & FEATURE DATASET CREATION COMPLETE')
arcpy.AddMessage('--------------------------------')



arcpy.AddMessage('--------------------------------')
arcpy.AddMessage('COPYING HANDOFF DATA TO THE NEW PUBLISH GDB')

if arcpy.Exists(handoffGDBpath):
	arcpy.AddMessage('\tCopying the LAND handoff for '+StateFull)
	arcpy.Copy_management(handoffGDBpath,PublishGDBpath)
if not arcpy.Exists(handoffGDBpath):
	arcpy.AddMessage('\tThere is no LAND handoff for '+StateFull)

arcpy.AddMessage('COPYING HANDOFF DATA TO THE NEW PUBLISH GDB COMPLETE')
arcpy.AddMessage('--------------------------------')



##arcpy.AddMessage('--------------------------------')
##arcpy.AddMessage('COPYING HUNT DATA TO THE NEW PUBLISH GDB')
##
##if arcpy.Exists(gmuGDBpath):
##	arcpy.env.workspace = gmuGDBpath
##	gmuDataset = arcpy.ListDatasets('*GMU*','feature')
##	for gmus in gmuDataset:
##		for gmuFeature in arcpy.ListFeatureClasses(feature_dataset=gmus):
##			path2Gmus = os.path.join(arcpy.env.workspace, gmus, gmuFeature)
##			arcpy.FeatureClassToGeodatabase_conversion(path2Gmus,PublishGDBpath+'\\GMUs')
##			arcpy.AddMessage('\tCopied GMUs from '+ gmuGDBpath+ ' to:\n'+PublishGDBpath+'\\GMUs')
##	Other_OldePublishGDB = OldePublishGDBpath+ '/Other' 
##	if arcpy.Exists(Other_OldePublishGDB):
##		otherDataset = arcpy.ListDatasets('*Other*','feature')
##		for others in otherDataset:
##			for otherFeature in arcpy.ListFeatureClasses(feature_dataset=others):
##				path2Others = os.path.join(arcpy.env.workspace, others, otherFeature)
##				arcpy.FeatureClassToGeodatabase_conversion(path2Others,PublishGDBpath+'\\Other')
##				arcpy.AddMessage('\tCopied Others from '+ gmuGDBpath+ ' to:\n'+PublishGDBpath+'\\Other')
##	if not arcpy.Exists(Other_OldePublishGDB):
##		arcpy.AddMessage('\tNo /Other feature dataset found for '+StateFull)
##	##	print 'No /Other found for '+StateFull
##if not arcpy.Exists(gmuGDBpath):
##	arcpy.AddMessage('There is no GMU handoff for '+StateFull)
##
##arcpy.AddMessage('COPYING HUNT DATA TO THE NEW PUBLISH GDB COMPLETE')
##arcpy.AddMessage('--------------------------------')



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
##arcpy.Copy_management(handoffGDBpath,PublishGDBpath)#will this work with an existing GDB there????
arcpy.AddMessage('HandoffGDB duplicated into PublishGDB')


# Arcpy.mapping, bitches!
mxd = arcpy.mapping.MapDocument(mTemplateMXDpath)
mxd.replaceWorkspaces(mTemplateGDBpath, "FILEGDB_WORKSPACE", PublishGDBpath, "FILEGDB_WORKSPACE")

##if arcpy.Exists(handoffGDBpath+'/Wilderness/'):
##	for lyr in arcpy.mapping.ListLayers(mxd):
##		if lyr.name== "Wilderness Boundaries":
##			lyr.replaceDataSource(PublishGDBpath, "FILEGDB_WORKSPACE", stateAbbr+'_Wilderness_Boundaries')
##		if lyr.name== "Wilderness Areas":
##			lyr.replaceDataSource(PublishGDBpath, "FILEGDB_WORKSPACE", stateAbbr+'_Wilderness_Areas')
##
##if arcpy.Exists(handoffGDBpath+'/Sections/'):
##	for layer in arcpy.mapping.ListLayers(mxd):
##		if layer.name=="Section Boundaries":
##			layer.replaceDataSource(PublishGDBpath, "FILEGDB_WORKSPACE",'Section_Boundaries')
##		if layer.name=="Section Areas":
##			layer.replaceDataSource(PublishGDBpath, "FILEGDB_WORKSPACE",'Section_Areas')

mxd.saveACopy(PublishMXDpath)
arcpy.AddMessage('TemplateMXD used to create the new PublishMXD for '+StateFull)
##print 'TemplateMXD used to create the new PublishMXD for '+StateFull

# Open that recently created PublishMXD to begin manual inspection of the data
# And the OldePublishMXD to compare the PublishMXD to
os.startfile(OldePublishMXDpath)
os.startfile(PublishMXDpath)
arcpy.AddMessage("Wasn't that sweet! Those ArcMaps opened magically all on their own, dude!")

arcpy.AddMessage('GEODATABASE REPLICATION; arcpy.mapping MAGICS COMPLETE')
arcpy.AddMessage('--------------------------------')
