###############
# routines.py #
###############

from globalVars import *
import os
import time
import datetime
import glob

###############

def getDirectoryContentsHelper(contents):
	"""Return the two seperate dictionaries from the directory contents."""

	dateDict = {}
	typeDict = {}

	for key in contents:
		tuple = contents[key]
		dateDict[key] = tuple[0]
		typeDict[key] = tuple[1]

	return (dateDict, typeDict)

###############

def getDirectoryContents(path):
	"""Get the contents of the directory as a dictionary.

		Results are key/value pairs where key is file name
		and value is (modification date as int, type)

		Where type is "Dir", "Special", "Ascii", "Binary"."""

	if (path == "") or (path == None):
		path = "."

	fileDict = {}

	# Get the contents of the directory

	objectList = os.listdir(path)

	# Now walk over them for what we want to know

	for object in objectList:
		theFile = joinPaths(path, object)

		fileType = ""
		fileDate = 0

		# First we figure out what it is.

		if os.path.isfile(theFile):
			if isSpecialFile(object):
				fileType = "Special"
			elif object[0] == ".":		# Dot files are always special
				fileType = "Special"
			else:
				# Figure out if it's ASCII or not

				(name, extention) = os.path.splitext(theFile)

				if isAsciiFile(extention):
					fileType = "Ascii"
				else:
					fileType = "Binary"

		elif os.path.isdir(theFile):
			fileType = "Dir"

		# Now get the date

		(st_mode, st_ino, st_dev, st_nlink, st_uid, st_gid,
			st_size, st_atime, st_mtime, st_ctime) = os.stat(theFile)

		fileDate = st_mtime

		fileDict[object] = (fileDate, fileType)

	# OK, we should have what we need now, return it

	return fileDict

###############

def isAsciiFile(fileExtention):
	"""Check to see if the file is a special file."""

	global asciiExtentions

	for extention in asciiExtentions:
		if extention == fileExtention:
			return True

	return False

###############

def isSpecialDir(filename):
	"""Check to see if the file is a special file."""

	global specialDirectoires

	for special in specialDirectories:
		if special == filename:
			return True

	return False

###############

def isSpecialFile(filename):
	"""Check to see if the file is a special file."""

	global specialFiles

	for special in specialFiles:
		if special == filename:
			return True

	return False

###############

def joinPaths(path1, path2):
	"""Wrapper for os.path.join."""

	if (path1 == "") or (path1 == None):
		return path2

	if (path2 == "") or (path2 == None):
		return path1

	if path2[-1] == "/":			# Make sure path2 doesn't overwrite path1
		path2 = "." + path2

	return os.path.join(path1, path2)

###############

def getSections(path):
	"""Get a list of the sections under this level."""

	filePath = joinPaths(path, "sections.txt")

	try:
		sectionFile = open(filePath, "r")
		sectionsList = sectionFile.readlines()
		sectionFile.close()
	except:
		return {}	# If we didn't find the file, there were no subsections

	sections = {}

	for line in sectionsList:
		line = line.strip()

		if line == "":
			pass

		dir, name = line.split("-", 1)
		dir = dir.strip()
		name = name.strip()
		sections[dir] = name

	return sections

###############

def processDirectorySelector(path, nav, depth, globalConfig):
	"""Figure out what kind of directory it is, and process it."""

	# Note that config isn't passed in because we are responsible for that

	global sectionObjects

	# First up, we have to read the config file in the directory

	configData = readConfigFile(os.path.join(path, "style.txt"))

	# Now we get the object we'll be using

	try:
		sectionObject = sectionObjects[getConfig(configData, "Style")]
	except:
		raise KeyError, "Unknown section type '%s'." % configData["Style"]

	sectionObject.processDirectory(path, nav, depth, configData, globalConfig)

###############

def getConfig(dict, key, default = None):
	"""Read a configuration key for us from a dictionary."""

	try:
		return dict[key]
	except:
		return default			# Key wasn't in dictionary, return default or None

###############

def readConfigFile(path):
	"""Read in the configuration file and return it's pairs."""

	configDict = {}

	try:
		configFile = open(path, "r")
		configList = configFile.readlines()
		configFile.close()
	except:
		return configDict

	for line in configList:

		line = line.strip()

		if not line == "":
			param, value = line.split("-", 1)

			param = param.strip()
			value = value.strip()

			configDict[param] = value

	return configDict

###############

def readFileAsLines(path):
	"""Read the file with the given path and return its
		contents as a series of lines"""

	try:
		fileHandle = open(path, "r")
		fileContents = fileHandle.readlines()
		fileHandle.close()
	except:
		raise IOError, "Unable to read from file '%s'." % path

	return fileContents

###############

def readFileAsPairs(path, concat = True):
	"""Read the file with the given path and return its
		contents as key/vallue pairs"""

	# This is for reading content files, NOT CONFIG FILES

	# The first line is a list of the names, comma seperated
	# The rest of the file is the values, one line per value
	# The very last value gets EVERYTHING after that (multi-line)
	# If concat is 1, all extra lines are put together as one long string.

	fileLines = readFileAsLines(path)

	# Make sure there isn't a blank line as the last line

	if fileLines[-1].strip() == "":
		fileLines.pop()

	# Now that we have that, we get the number of lines

	numLines = len(fileLines)

	if numLines < 2:
		# Gotta have at least two lines (the names line, and a content line)
		raise EOFError, "Not enough lines in file '%s', count is %i." % (path, numLines)

	# Now we get a list of the names we'll need

	lineNames = fileLines[0].split(',')

	numNames = len(lineNames)

	if numLines <= numNames:
		# There aren't enough lines to fill the names for name/value pairs
		raise EOFError, "Not enough lines in file '%s' (have %i, need %i)." % (path, numLines, numNames + 1)

	# Now we do the processing

	pairDict = {}

	i = 1

	for name in lineNames:
		if i != numNames:
			# Not the last thing, so just save it
			pairDict[name.strip()] = fileLines[i].strip()
			i = i + 1
		else:
			if concat == True:
				# Last thing, so we must concatenate all the rest
				tempString = ""

				for j in range(i, numLines):
					tempString = tempString + fileLines[j].strip() + "\n"

				pairDict[name.strip()] = tempString
			else:
				# OK, we want to take the lines as they are, and hand off the list
				linesLeft = fileLines[i:]	# fileLines[i] through the last element

				pairDict[name.strip()] = fileLines[i]

	# Now we should have everything in the pairDict dictionary, so return it

	return pairDict

###############

def printAtDepth(depth, string, code):
	"""Put spaces to depth."""

	global printStyle

	if printStyle == "text":					# Print out just the text
		retVal = "  " * depth

		print retVal + string
	elif printStyle == "both":					# Print the code and the text
		retVal = "  " * depth

		retVal = "%i: %s%s" % (code, retVal, string)

		print retVal
	elif printStyle == "code":					# Print just the code
		print code
	else:										# Shhhh! Silent mode.
		pass

###############

def writeFile(nav, body, title, file, templateHTML):
	"""Write out the file given the information."""

	global fileCount, rootDir

	fileText = templateHTML.replace("###TITLE###", title)
	fileText = fileText.replace("###NAV###", nav)
	fileText = fileText.replace("###BODY###", body)

	fileHandle = open(file, "w")
	fileHandle.write(fileText)
	fileHandle.close()

	fileCount = fileCount + 1

###############

def linesToDateDict(theLines):
	"""Turn a list of files into a list of modification dates."""

	dateDict = {}

	for line in theLines:
		if line[0] == '-':
			(perm, link, owner, group, size, month, day, timeYear, name) = line.split(None, 8)

			dateString = month + ' ' + day + ' ' + timeYear

			timeStruct = ""

			if dateString.count(":") == 1:
				# Date ended in hours
				timeStruct = time.strptime(dateString, "%b %d %H:%M")
			else:
				# Date ended in year
				timeStruct = time.strptime(dateString, "%b %d %Y")

			# Make sure the year is correct

			currentYear = datetime.date.today().year

			if timeStruct[0] < 2000:
				timeStruct = (currentYear, timeStruct[1], timeStruct[2],
								timeStruct[3], timeStruct[4], timeStruct[5],
								timeStruct[6], timeStruct[7], timeStruct[8])

			timeInSec = time.mktime(timeStruct)

			dateDict[name] = timeInSec

	return dateDict

###############

def readFileAsString(path):
	"""Read the file with the given path and return its
		contents as a string"""

	try:
		fileHandle = open(path, "r")
		fileContents = fileHandle.read()
		fileHandle.close()
	except:
		raise IOError, "Unable to read from file '%s'." % path

	return fileContents

###############

def dirToDateDict(theDir):
	"""Get a list of files in current directory and put into a dict of dates."""

	global rootDir

	dateDict = {}

	if theDir == "":
		theDir = os.getcwd()
		
	# Get the contents of the directory
	
	objectList = os.listdir(theDir)

	# Now walk over them for what we want to know

	for object in objectList:
		theFile = os.path.join(theDir, object)
		# First make sure it is a normal file
		if os.path.isfile(theFile):
			# OK, it's a normal file, work our magic
			(st_mode, st_ino, st_dev, st_nlink, st_uid, st_gid,
				st_size, st_atime, st_mtime, st_ctime) = os.stat(theFile)

			# Now that we have all that, let us figure out what we want

			dateDict[object] = st_mtime

	# OK, we should have what we need now, return it

	return dateDict

###############

def needsUpdate(sourceDict, destDict, offsetTime):
	"""Given the two dictionaries of times, figure out which files to update."""

	# NOTE: It is up to the caller to filter out things they wouldn't mess with.

	updateList = []

	for filename in sourceDict.keys():
		if destDict.has_key(filename):
			if ((sourceDict[filename] + offsetTime) > destDict[filename]):
				# The file has been updated, add it to the list
				updateList.append(filename)
		else:
			# The file isn't in the dest, so it would need to be uploaded
			updateList.append(filename)

	# Now that we have that list, return it

	return updateList

###############

def addToRemoteLines(line):
	"""Add the line to the global variable remoteLines."""

	global remoteLines

	remoteLines.append(line)

###############

def uploadDirectory(dirName, config, ftp, depth):
	"""Upload the subdirectory with the given name of the current working directory."""

	global remoteLines, updateChecked, updatePerformed

	# Step 1: Go into the new directory

	printAtDepth(depth, "Entering directory '%s'..." % dirName, 2)

	oldCWD = ftp.pwd()

	if dirName is not "":
		try:
			ftp.cwd(dirName)
		except:
			try:
				ftp.mkd(dirName)		# Make the directory since it wasn't there.
				ftp.cwd(dirName)
				
				printAtDepth(depth, "Created directory '%s' and entered it..." % dirName, 2)
				
			except:
				raise IOError, "Unable to change into directory '%s', even after trying to make it." % dirName

		os.chdir(dirName)

	# Step 2: Figure out what needs updating

	dirContents = getDirectoryContents("")

	(dateDict, typeDict) = getDirectoryContentsHelper(dirContents)

	dateDictList = dateDict.keys()
	dateDictList.sort()

	remoteLines = []

	ftp.retrlines("LIST", addToRemoteLines)

	remoteDict = linesToDateDict(remoteLines)

	filesNeedingUpdate = needsUpdate(dateDict, remoteDict, 0)

	# Step 3: Upload all the files that need uploading

	for file in dateDictList:
		if filesNeedingUpdate.count(file) or getConfig(config, "ForceUpload"):	# If the file is listed as one needing updating
			if (typeDict[file] == "Special") or (file[-4:] == ".txt"):
				printAtDepth(depth + 1, "Skipping '%s', it was special..." % file, 4)
				updateChecked = updateChecked + 1			
			elif (typeDict[file] == "Binary") or (typeDict[file] == "Ascii"):
				uploadFile(file, ftp, depth + 1)	# Upload it
				updateChecked = updateChecked + 1
				updatePerformed = updatePerformed + 1
			elif typeDict[file] == "Dir":
				if not isSpecialDir(file):	# Make sure it's not special
					# This is a subdirectory that needs uploading
					uploadDirectory(file, config, ftp, depth + 1)
					# Directories don't count against the check count
			else:
				raise NameError, "File category, '%s', was unknown!" % typeDict[file]
		else:
			printAtDepth(depth + 1, "Skipping '%s', doesn't need update..." % file, 4)
			updateChecked = updateChecked + 1

	# Step 4: Return

	printAtDepth(depth, "Leaving directory '%s'..." % dirName, 3)

	ftp.cwd("..")

	os.chdir("..")
	
###############

def uploadFile(fileName, ftp, depth):
	"""Upload the file whose name is passed to us."""

	# First we need to know if the file is ASCII or BINARY

	(name, ext) = os.path.splitext(fileName)

	# Now we open the file

	fileObj = open(fileName)

	# Now we do our stuff

	if isAsciiFile(ext):
		printAtDepth(depth, "Uploading '%s' as ASCII..." % fileName, 8)
		ftp.storlines("STOR %s" % fileName, fileObj)
	else:
		printAtDepth(depth, "Uploading '%s' as binary..." % fileName, 8)
		ftp.storbinary("STOR %s" % fileName, fileObj)

	# Now we close the file

	fileObj.close()

	# That's it.

	printAtDepth(depth + 2, "Done.", 9)
