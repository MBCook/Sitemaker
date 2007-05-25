################
# sitemaker.py #
################

from globalVars import *
import routines
import FileSection
import BlogSection
import ListSection
import GallerySection
import Section
import os
import ftplib
import sys
import time

#####################
# The main function #
#####################

def main():
	"""The main function of the program that gets everything going."""

	global fileProcessCount, fileUpdateCount, updateChecked, updatePerformed

	startTime = time.time()

	print ""

	# First we figure out what to do

	doUpdate = True						# Default options
	doUpload = False

	if len(sys.argv) < 2:
		pass							# Default options
	elif len(sys.argv) == 2:
		if sys.argv[1] == "update":
			pass						# Default options
		elif sys.argv[1] == "upload":
			doUpdate = False			# Upload, no update
			doUpload = True
		elif sys.argv[1] == "help":
			print "Useage: sitemaker [update] [upload]"
			doUpdate = False
			doUpload = False
		else:
			raise NameError, "Unknown argument: %s" % sys.argv[1]
	elif len(sys.argv) == 3:
		if ((sys.argv[1] == "update") and (sys.argv[2] == "upload")):
			doUpdate = True				# Do both!
			doUpload = True
		else:
			if ((sys.argv[1] == "upload") and (sys.argv[2] == "update")):
				raise NameError, "Update argument MUST COME BEFORE upload argument."
			else:
				raise NameError, "Only known arguments are 'update' and 'upload'.\nYou gave '%s' and '%s'." % (sys.argv[1], sys.argv[2])
	else:
		raise NameError, "Two arguments maximim, you gave %i." % len(sys.argv)

	# Load config info

	config = routines.readConfigFile("siteConfig.txt")

	config = prepareConfig(config)	# Make sure the default stuff is good for us

	# Load everything else

	os.chdir(routines.getConfig(config, "LocalRoot"))	# No default needed because of above

	# Call startProcessing

	if doUpdate:
		print ""
		updateProcessing(config)

	if doUpload:
		print ""
		uploadProcessing(config)

	# Now we'll print some status because stats are fun

	print ""

	if doUpdate:
		print "%i files were processed, %i were updated." % (fileProcessCount, fileUpdateCount)

	if doUpload:
		print "%i files were checked for updates, %i were uploaded." % (updateChecked, updatePerformed)

	timeRun = time.time() - startTime

	if timeRun == 1.00:
		print "This program ran for 1.00 seconds."
	else:
		print "This program ran for %.2f seconds." % round(timeRun, 2)

	print ""

	# That's it

#####################
# Kickoff functions #
#####################

def uploadProcessing(config):
	"""The function that starts the uploading to the server."""

	# Get ready (we should already be in the local root directory)

	routines.printAtDepth(0, "Beginning uploading...", 7)

	# Establish the FTP connection
	
	ftp = ftplib.FTP()

	# Make sure everything is in order before we connect

	ftpUser = routines.getConfig(config, "FtpUser")
	ftpPass = routines.getConfig(config, "FtpPass")
	ftpServer = routines.getConfig(config, "FtpServer")
	ftpBase = routines.getConfig(config, "FtpBase")

	if ((ftpUser == "") or (ftpUser == None)):
		raise NameError, "No user name given for FTP upload."

	if ftpPass == None:
		ftpPass = getPassword()

	if ((ftpServer == "") or (ftpServer == None)):
		raise NameError, "No FTP server given, unable to connect."

	# Now we try to connect

	routines.printAtDepth(1, "Connecting to the FTP server...", 14)

	try:
		ftp.connect(ftpServer)
	except:
		routines.printAtDepth(1, "Unable to connect to the FTP server.", 11)
		return

	routines.printAtDepth(1, "Logging into the FTP server...", 14)

	try:
		ftp.login(ftpUser, ftpPass)
	except:
		routines.printAtDepth(1, "Unable to log into the FTP server successfully.", 11)
		routines.printAtDepth(1, "Closing the FTP session...", 15)
		try:
			ftp.quit()
		except:
			ftp.close()
		return

	routines.printAtDepth(1, "Changing to the remote base directory...", 11)

	try:
		ftp.cwd(ftpBase)
	except:
		routines.printAtDepth(1, "Unable to change to the base directory.", 11)
		routines.printAtDepth(1, "Closing the FTP session...", 15)
		try:
			ftp.quit()
		except:
			ftp.close()

	routines.printAtDepth(1, "Successfully logged in and ready to upload things.", 11)

	# OK, we're all setup.

	try:
		routines.uploadDirectory("", config, ftp, 1)
	except ftplib.all_errors:
		routines.printAtDepth(1, "An error occured in the FTP session.", 12)
		# If we fail, we fall through to the disconnect

	# Time to disconnect.

	routines.printAtDepth(1, "Closing the FTP session...", 15)
	
	try:
		ftp.quit()
	except:
		ftp.close()

	# Done

	routines.printAtDepth(0, "Done uploading!", 10)

def updateProcessing(config):
	"""The function that calls processDirectory on the root directory."""

	routines.printAtDepth(0, "Beginning processing...", 5)

	# Load the objects that we'll need

	loadSectionObjects()
	loadTemplates()

	# Figure out the local root

	localRoot = routines.getConfig(config, "LocalRoot")

	routines.printAtDepth(1, "Entering directory \"%s\"..." % localRoot, 2)

	# Get the begining navigation HTML

	nav = Section.Section().makeNavigationHTML("", config, "main")	# HACK!

	# Process

	routines.processDirectorySelector("", nav, 1, config)

	routines.printAtDepth(1, "Leaving directory \"%s\"..." % localRoot, 3)
	routines.printAtDepth(0, "Done Processing!\n", 6)

####################
# Helper functions #
####################

def prepareConfig(config):
	"""Prepare some things in the config data that we must have set."""

	# Make sure that local root is set

	if not config.has_key("LocalRoot"):
		config["LocalRoot"] = os.getcwd()	# We need this, so if not specified we'll assume.
		routines.printAtDepth(0, "No local root specified, assuming current directory!", 13)

	# Now make sure that the remote root is valid

	rb = routines.getConfig(config, "RemoteBase")

	if rb == None:											# Assume remote base of / if none
		config["RemoteBase"] = "/"
	elif rb[-1] != "/":										# Remote base must end in /
		config["RemoteBase"] = config["RemoteBase"] + "/"

	# Make sure we have ana FTP base directory

	ftpb = routines.getConfig(config, "FtpBase")

	if ftpb == None:										# Assume remote base of / if none
		config["FtpBase"] = "."

	# Setup forceUpdate and forceUpload

	forceUpdate = routines.getConfig(config, "ForceUpdate")
	forceUpload = routines.getConfig(config, "ForceUpload")

	if forceUpdate == None:	# Force an update if not disabled
		config["ForceUpdate"] = True
	elif forceUpdate.strip() == "True":
		config["ForceUpdate"] = True
	else:
		config["ForceUpdate"] = False
		
	if forceUpdate == None:	# Don't force an upload if not enabled
		config["ForceUpload"] = False
	elif forceUpload.strip() == "True":
		config["ForceUpload"] = True
	else:
		config["ForceUpload"] = False

	return config

def loadSectionObjects():
	"""Load the section objects that we'll need."""

	# FIX ME: Remove the hardcoding here so that we can load things dynamically
	#				based on what the config file tells us

	global sectionObjects

	sectionObjects["Blog"] = BlogSection.BlogSection()
	sectionObjects["File"] = FileSection.FileSection()	# See? This should be easy to automate
	sectionObjects["List"] = ListSection.ListSection()
	sectionObjects["Gallery"] = GallerySection.GallerySection()

def loadTemplates():
	"""Load the templates that we'll use."""

	# FIX ME: Remove hardcoding, load the ones we want based on config file.

	global templateDict, templateDateDict

	dateDict = routines.dirToDateDict("")

	templateDict["Default_Page"] = routines.readFileAsString("templatePage.txt")
	templateDateDict["Default_Page"] = dateDict["templatePage.txt"]
	templateDict["Default_Body"] = routines.readFileAsString("templateBody.txt")
	templateDateDict["Default_Body"] = dateDict["templateBody.txt"]
	templateDict["Default_Entry"] = routines.readFileAsString("templateEntry.txt")
	templateDateDict["Default_Entry"] = dateDict["templateEntry.txt"]
	templateDict["Wanted_List"] = routines.readFileAsPairs("templateList_want.txt", False)
	templateDateDict["Wanted_List"] = dateDict["templateList_want.txt"]
	templateDict["Default_Gallery"] = routines.readFileAsString("templateGalleryIndex.txt")
	templateDateDict["Default_Gallery"] = dateDict["templateGalleryIndex.txt"]
	templateDict["Default_GalleryEntry"] = routines.readFileAsString("templateGalleryIndexEntry.txt")
	templateDateDict["Default_GalleryEntry"] = dateDict["templateGalleryIndexEntry.txt"]
	templateDict["Default_GalleryLarge"] = routines.readFileAsString("templateGalleryLarge.txt")
	templateDateDict["Default_GalleryLarge"] = dateDict["templateGalleryLarge.txt"]
	templateDict["Default_Feed"] = routines.readFileAsString("templateFeed.txt")
	templateDateDict["Default_Feed"] = dateDict["templateFeed.txt"]
	templateDict["Default_FeedEntry"] = routines.readFileAsString("templateFeedEntry.txt")
	templateDateDict["Default_FeedEntry"] = dateDict["templateFeedEntry.txt"]	

def getPassword():
	"""Ask the user for a password."""

	thePass = raw_input("  Please enter your FTP password: ")

	return thePass

##############
# Magic Code #
##############

# This magic code makes the main function run when this file is executed by Python

if __name__ == "__main__":
	main()

# That's all!
