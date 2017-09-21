# Import system modules
import datetime, arcpy, os, logging
from arcpy import env					# From Arcpy, import environmental variable
arcpy.env.overwriteOutput = True		# Overwrite is turned ON for this script
arcpy.env.outputZFlag = "Disabled"		# Disables Z-values
arcpy.env.outputMFlag = "Disabled"		# Disables M-values


#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
#the end target of this script is to create a new GDB and MXD named after
# for the GDB the state abbreviation and the current date build the name
# for the mxd the full state name and  the current date build the name
#
#the GDB will transfer things from the handoff GDB
#
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-

print "SCRIPT START"

#state abbreviation dictionary - includes special names for WY & MT
stateTar = {'AK': 'Alaska','AL': 'Alabama','AR': 'Arkansas','AS': 'AmericanSamoa','AZ': 'Arizona','CA': 'California','CO': 'Colorado','CT': 'Connecticut','DC': 'DistrictOfColumbia','DE': 'Delaware','FL': 'Florida','GA': 'Georgia','GU': 'Guam','HI': 'Hawaii','IA': 'Iowa','ID': 'Idaho','IL': 'Illinois','IN': 'Indiana','KS': 'Kansas','KY': 'Kentucky','LA': 'Louisiana','MA': 'Massachusetts','MD': 'Maryland','ME': 'Maine','MI': 'Michigan','MN': 'Minnesota','MO': 'Missouri','MP': 'NorthernMarianaIslands','MS': 'Mississippi','MT': 'Montana_Yellowstone','NA': 'National','NC': 'NorthCarolina','ND': 'NorthDakota','NE': 'Nebraska','NH': 'NewHampshire','NJ': 'NewJersey','NM': 'NewMexico','NV': 'Nevada','NY': 'NewYork','OH': 'Ohio','OK': 'Oklahoma','OR': 'Oregon','PA': 'Pennsylvania','PR': 'PuertoRico','RI': 'RhodeIsland','SC': 'SouthCarolina','SD': 'SouthDakota','TN': 'Tennessee','TX': 'Texas','UT': 'Utah','VA': 'Virginia','VI': 'VirginIslands','VT': 'Vermont','WA': 'Washington','WI': 'Wisconsin','WV': 'WestVirginia','WY': 'Wyoming_Yellowstone'}

# PRIMARY variables, which must be changed/verified ahead of running this script
State= 'KS'
newVersion = '166'
StateFull = stateTar[State] #OLD MANUAL ENTRY

# SECONDARY variables, which may need to changed\\verified (but hopefully not) ahead of running this script
networkDirectory = 'G:/Products/ArcServer/'
networkPath = networkDirectory + 'PRODUCTION_DATA/'+State + '/'
handoffDirectory = networkDirectory+"PRODUCTION_DATA/!Handoff/" # what will this be?
networkNewData = networkDirectory+"/Data_State/"+State

LocalDirectory = 'D:/sd-files/staging/' #NEEDS to be set to whatever the SD file extract is
##localPath = LocalDirectory + State + '/' #no longer needed
handoffDirectory = LocalDirectory+"PRODUCTION_DATA/!Handoff/" # what will this be?
scriptingPath = LocalDirectory+'!Scripting/' #is this needed?
mtemplatePath = LocalDirectory+'!MasterPublishTemplate/' #is this needed?
maskclipGDB = scriptingPath+'ClipMask/ClipMask_Tiger2013.gdb' #is this needed?
adminBounds = maskclipGDB+'/Clip/'+StateFull #is this needed?

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#
#Gather timestamps and old versions#
today = datetime.date.today()
dateStamp = today.strftime('%Y%m%d')
#DateStamp_Today = '20151110' - OLD MANUAL ENTRY

#set up loggging file
logging.basicConfig(level=logging.INFO,
                    filename=dateStamp+'_mapUpdate.csv',
                    format=' %(asctime)s,%(levelname)s,%(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

logging.info(StateFull.upper()+" map update")
logging.info("Locating data\n")

print "Check versions of inputs"
#finding Handoff information for newest target state
handoffFiles = os.listdir(handoffDirectory)
for targetFile in sorted(handoffFiles,reverse=True):
	stateTar = targetFile.split('_')[1]
	if stateTar==State: #if the handoff state is equal to the defined state
		handoffGDBdate = targetFile.split('_')[0]
		targetHandoff = targetFile
		logging.info(State+ " Handoff GDB located,datestamp : "+handoffGDBdate)
		break
#DateStamp_HandoffGDB = '20151104' - OLD MANUAL ENTRY
print "\tHANDOFF: "+targetHandoff


#finding old GDB information
oldPubList = os.listdir(networkPath)
for oldGDB in sorted(oldPubList,reverse=True):
	if oldGDB.endswith("Publish.gdb"):
		oldGDBdate = oldGDB.split('_')[0]
		targetOLDgdb=oldGDB
		logging.info(State+ " Old Publish GDB located,datestamp : "+oldGDBdate)
		break
#DateStamp_OldePublishGDB = '20140403' - OLD MANUAL ENTRY
print "\tOLD GDB: "+targetOLDgdb


#finding old MXD information
for oldMXD in sorted(oldPubList,reverse=True):
	if oldMXD.endswith(".mxd"):
		oldMXDdate = oldMXD.split('_')[0]
		oldMXDversion = (oldMXD.split('_')[2]).split('.')[0]
		targetOLDmxd=oldMXD
		logging.info(State+ " Old Publish MXD located,datestamp : "+oldMXDdate+",version # : "+oldMXDversion)
		break
#DateStamp_OldePublishMXD = '20140403' - OLD MANUAL ENTRY
#Version_OldePublishMXD = '140' - OLD MANUAL ENTRY
print "\tOLD MXD: "+targetOLDmxd


mTemplateList = os.listdir(mtemplatePath)
for mTemplateGDB in sorted(mTemplateList,reverse=True):
	if mTemplateGDB.endswith("MasterPublishTemplate.gdb"):
		mTemplateDate = mTemplateGDB.split('_')[0]
		targetMgdb = mTemplateGDB
		logging.info("Master Template GDB located,datestamp : "+mTemplateDate+"\n")
		break
#Datestamp_MasterPublishTemplate = '20151020' - OLD MANUAL ENTRY
print "\tMASTER TEMPLATE GDB: "+targetMgdb


#finding master template mxd information
mTemplateList = os.listdir(mtemplatePath)
for mTemplateMXD in sorted(mTemplateList,reverse=True):
	if mTemplateMXD.endswith("MasterPublishTemplate.mxd"):
		mTemplateDate = mTemplateMXD.split('_')[0]
		targetMmxd = mTemplateMXD
		logging.info("Master Template MXD located,datestamp : "+mTemplateDate)
		break
#Datestamp_MasterPublishTemplate = '20151020' - OLD MANUAL ENTRY
print "\tMASTER TEMPLATE MXD: "+targetMmxd

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#
# TERTIARY variables, which do not need to be changed/verified ahead of running this script
OldePublishMXD_Network = networkPath+targetOLDmxd										#G:\\Products\\ArcServer\\PRODUCTION_DATA\\20140403_Michigan140.mxd
OldePublishMXD = localPath+targetOLDmxd													#D:\\APP\\MI\\20140403_Michigan140.mxd
OldePublishGDB_Network = networkPath+targetOLDgdb										#G:\\Products\\ArcServer\\PRODUCTION_DATA\\MI\\20140403_MI_Publish.gdb
OldePublishGDB = localPath+targetOLDgdb													#D:\\APP\\MI\\20140403_MI_Publish.gdb
HandoffGDB_Network = handoffDirectory+targetHandoff											#G:/Products/ArcServer/PRODUCTION_DATA/!Handoff
HandoffGDB = localPath+targetHandoff													#D:\\APP\\MI\\20151104_MI_Handoff.gdb

PublishGDB = localPath+dateStamp+"_"+State+"_Publish.gdb"								#D:\\APP\\MI\\20151110_MI_Publish.gdb
PublishMXD = localPath+dateStamp+"_"+StateFull+"_"+newVersion+".mxd"					#D:\\APP\\MI\\20151110_Michigan_150.mxd


logging.info(StateFull.upper() +' processing start\n')
logging.info('FOLDERS AND GEODATABASE CREATION; DATA COPYING')
print '\nFOLDERS AND GEODATABASE CREATION; DATA COPYING'

# Create a folder in the local working directory for the state of interest, if it doesn't already exist
if not arcpy.Exists(localPath):
	arcpy.CreateFolder_management(LocalDirectory,State)
	logging.info(State+" directory created on "+ LocalDirectory)

# Copy OldePublishMXD from G:/ to local, if it doesn't exist already
if arcpy.Exists(OldePublishMXD):
	logging.info('OldePublishMXD already exists')
if not arcpy.Exists(OldePublishMXD): 
	arcpy.Copy_management(OldePublishMXD_Network,OldePublishMXD)
	logging.info(OldePublishMXD+' copied to '+localPath)

# Copy OldePublishGDB from G:/ to local, if it doesn't exist already
if arcpy.Exists(OldePublishGDB):
	logging.info('OldePublishGDB already exists')
if not arcpy.Exists(OldePublishGDB): 
	arcpy.Copy_management(OldePublishGDB_Network,OldePublishGDB)
	logging.info(OldePublishGDB+' copied to '+localPath)

# Copy the HandoffGDB_Network local to become the HandoffGDB, if it doesn't exist already
if arcpy.Exists(HandoffGDB):
	logging.info('HandoffGDB already exists')
if not arcpy.Exists(HandoffGDB): 
	arcpy.Copy_management(HandoffGDB_Network,HandoffGDB)
	logging.info(HandoffGDB_Network+' copied to '+localPath)
	# Delete HandoffGDB_Network in the future after it is copied local? Just an idea; throwing it out there.

logging.info('FOLDER AND GEODATABASE CREATION; DATA COPYING COMPLETE\n')


logging.info('FEATURE DATASET/FEATURE CLASS COPYING [OldePublishGDB -> HandoffGDB]')
print 'FEATURE DATASET/FEATURE CLASS COPYING [OldePublishGDB -> HandoffGDB]'

# Define the feature datasets from the OldePublishGDB which you desire to copy into the HandoffGDB:
WebMercator = arcpy.SpatialReference(3857)
# /GMUs/
GMUs_OldePublishGDB = OldePublishGDB+ '/GMUs' 
if arcpy.Exists(GMUs_OldePublishGDB):
	arcpy.CreateFeatureDataset_management(HandoffGDB, "GMUs", WebMercator)
	logging.info('GMUs feature dataset created because it exists in the OldePublishGDB')
# /GMU/ -> /GMUs/
GMU_OldePublishGDB = OldePublishGDB+ '/GMU' 
if arcpy.Exists(GMU_OldePublishGDB):
	arcpy.CreateFeatureDataset_management(HandoffGDB, "GMUs", WebMercator)
	logging.info('GMU dataset created because it exists in the OldePublishGDB')
print"\tGMU dataset created"


# /Other/
Other_OldePublishGDB = OldePublishGDB+ '/Other' 
if arcpy.Exists(Other_OldePublishGDB):
	arcpy.CreateFeatureDataset_management(HandoffGDB, "Other", WebMercator)
	logging.info('Other dataset created because it exists in the OldePublishGDB')
print "\tOther dataset created"


### /Sections/ -> /Sections/
### If they exist, clip the section areas to the state clipping boundary, reading from OldePublishGDB and writing to HandoffGDB
##OldePublish_SectionLines2 = OldePublishGDB+'/Sections/Section_Lines'
##OldePublish_BoundaryLines2 = OldePublishGDB+'/Sections/Section_Boundaries' #variable added 092016 to handle Boundary used in old data
##Handoff_SectionLines2  = HandoffGDB+'/Sections/Section_Boundaries'
##OldePublish_SectionAreas2 = OldePublishGDB+'/Sections/Section_Areas'
##Handoff_SectionAreas2 = HandoffGDB+'/Sections/Section_Areas'
##
##if arcpy.Exists(OldePublishGDB+'/Sections'):
##	# Create a feature dataset in the HandoffGDB named 'Sections' into which section areas and boundaries from the OldePublishGDB are going to be clipped
##	logging.info('Old GDB has a Sections dataset creating a new /Sections dataset')
##	print "\tSections dataset created"
##	arcpy.CreateFeatureDataset_management(HandoffGDB, "Sections", WebMercator)
##	if arcpy.Exists(OldePublish_SectionLines2):
##		arcpy.Clip_analysis(OldePublish_SectionLines2, adminBounds, Handoff_SectionLines2)
##	if arcpy.Exists(OldePublish_BoundaryLines2):
##		arcpy.Clip_analysis(OldePublish_BoundaryLines2, adminBounds, Handoff_SectionLines2)
##	logging.info('Old Section Lines clipped/copied from Old GDB to Handoff GDB')
##	arcpy.Clip_analysis(OldePublish_SectionAreas2, adminBounds, Handoff_SectionAreas2)
##	logging.info('Old Section Areas clipped/copied from Old GDB to Handoff GDB')
##
##if not arcpy.Exists(OldePublishGDB+'/Sections'):
##	logging.warning('Old GDB does not have a Sections feature dataset')
##	print"\t\tOld GDB does not have a Sections dataset"
##
##
### /PLSS/ -> /Sections/
### If they exist, clip the section boundaries to the state clipping boundary, reading from OldePublishGDB and writing to HandoffGDB
##OldePublish_SectionLines = OldePublishGDB+'/PLSS/Section_Lines'
##OldePublish_BoundaryLines = OldePublishGDB+'/PLSS/Section_Boundaries' #variable added 092016 to handle Boundary used in old data
##Handoff_SectionLines  = HandoffGDB+'/Sections/Section_Boundaries'
##OldePublish_SectionAreas = OldePublishGDB+'/PLSS/Section_Areas'
##Handoff_SectionAreas = HandoffGDB+'/Sections/Section_Areas'
##
##if arcpy.Exists(OldePublishGDB+'/PLSS'):
##	logging.info('Old GDB has a PLSS dataset creating a new /Sections dataset')
##	print "\tSections dataset created"
##	arcpy.CreateFeatureDataset_management(HandoffGDB, "Sections", WebMercator)
##	if arcpy.Exists(OldePublish_SectionLines):
##		arcpy.Clip_analysis(OldePublish_SectionLines, adminBounds, Handoff_SectionLines)
##	if arcpy.Exists(OldePublish_BoundaryLines):
##		arcpy.Clip_analysis(OldePublish_BoundaryLines, adminBounds, Handoff_SectionLines)
##	logging.info('Old Section Lines clipped/copied from Old GDB to Handoff GDB')
##	arcpy.Clip_analysis(OldePublish_SectionAreas, adminBounds, Handoff_SectionAreas)
##	logging.info('Old Section Areas clipped/copied from Old GDB to Handoff GDB')
##
##if not arcpy.Exists(OldePublishGDB+'/PLSS'):
##	logging.warning('Old GDB does not have a PLSS dataset')
##	print "\t\tOld GDB does not have a PLSS dataset"
##
##logging.info('FEATURE DATASET/FEATURE CLASS COPYING [OldePublishGDB -> HandoffGDB] COMPLETE\n')
##
##
##logging.info('WILDERNESS AREAS/BOUNDARIES PROCESSING')
##print 'WILDERNESS AREAS/BOUNDARIES PROCESSING'
##
### /Wilderness/
### If they exist, import the wilderness lines and areas into the HandoffGDB from the GIS drive
##OldWilderness_Lines = OldePublishGDB+'/Wilderness/'+State+'/_Wilderness_Boundaries'
##OldWilderness_Areas = OldePublishGDB+'/Wilderness/'+State+'/_Wilderness_Areas'
##
####Wilderness_Lines = 'G:/Data_State/'+State+'/Wilderness/Complete/'+State+'_Wilderness_Boundaries.shp'
####Wilderness_Lines_HandoffGDB = HandoffGDB+'/Wilderness/'+State+'_Wilderness_Boundaries'
##	
##if arcpy.Exists(OldWilderness_Lines):
##	# Create a feature dataset to house the wilderness lines and areas
##	arcpy.CreateFeatureDataset_management(HandoffGDB,"Wilderness",WebMercator)
##	logging.info('Wilderness feature dataset created')
##	arcpy.FeatureClassToFeatureClass_conversion(OldWilderness_Lines, OldWilderness_Lines, State+'_Wilderness_Boundaries') #if the old wilderness lines exists then pull it across
##	logging.info('Wilderness lines imported into the HandoffGDB from the GIS drive')
##if not arcpy.Exists(OldWilderness_Lines):
##	logging.warning('No Wilderness Lines exist in '+OldWildernessLines)
##
### If they exist, import the wilderness lines and areas into the HandoffGDB from the GIS drive
####Wilderness_Areas = 'G:/Data_State/'+State+'/Wilderness/Complete/'+State+'_Wilderness_Areas.shp'
####Wilderness_Areas_HandoffGDB = HandoffGDB+'/Wilderness/'+State+'_Wilderness_Areas'
##
### If they exist, import the wilderness lines and areas into the HandoffGDB from the GIS drive
##if arcpy.Exists(OldWilderness_Areas):
##	arcpy.FeatureClassToFeatureClass_conversion(OldWilderness_Areas, OldWilderness_Areas, State+'_Wilderness_Areas') #if the old wilderness area exists then pull it across
##	logging.info('Wilderness areas imported into the HandoffGDB from the GIS drive')
##if not arcpy.Exists(OldWilderness_Areas):
##	logging.warning('No Wilderness Areas exist in'+OldWildernessAreas)
##
##logging.info('WILDERNESS AREAS/BOUNDARIES PROCESSING COMPLETE\n')


logging.info('GEODATABASE REPLICATION; arcpy.mapping MAGICS')
print 'GEODATABASE REPLICATION; arcpy.mapping'

# Duplicate the HandoffGDB to become the PublishGDB
arcpy.Copy_management(HandoffGDB,PublishGDB)
logging.info('HandoffGDB duplicated into PublishGDB')

# Arcpy.mapping, bitches!
TemplateGDB = mtemplatePath+targetMgdb													#D:\\APP\\!MasterPublishTemplate\\20151020_MasterPublishTemplate.gdb
TemplateMXD = mtemplatePath+targetMmxd													#D:\\APP\\!MasterPublishTemplate\\20151020_MasterPublishTemplate.mxd
PublishGDB = localPath+dateStamp+"_"+State+"_Publish.gdb"								#D:\\APP\\MI\\20151110_MI_Publish.gdb
PublishMXD = localPath+dateStamp+"_"+StateFull+"_"+newVersion+".mxd"					#D:\\APP\\MI\\20151110_Michigan_150.mxd

mxd = arcpy.mapping.MapDocument(TemplateMXD)
mxd.replaceWorkspaces(TemplateGDB, "FILEGDB_WORKSPACE", PublishGDB, "FILEGDB_WORKSPACE",False)

if arcpy.Exists(Wilderness_Areas):
	for lyr in arcpy.mapping.ListLayers(mxd):
		if lyr.name== "Wilderness Boundaries":
			lyr.replaceDataSource(PublishGDB, "FILEGDB_WORKSPACE", State+'_Wilderness_Boundaries')
		if lyr.name== "Wilderness Areas":
			lyr.replaceDataSource(PublishGDB, "FILEGDB_WORKSPACE", State+'_Wilderness_Areas')

mxd.saveACopy(PublishMXD)
logging.info('TemplateMXD used to create the new PublishMXD for '+StateFull)
print "\tBreak and replace complete"

# Open that recently created PublishMXD to begin manual inspection of the data
# And the OldePublishMXD to compare the PublishMXD to
os.startfile(OldePublishMXD)
os.startfile(PublishMXD)
logging.info('GEODATABASE REPLICATION; arcpy.mapping MAGICS COMPLETE\n')

#-------------------------------------------------------------------------------
logging.info("Script finished")
print "\nScript finished"
logging.shutdown()
