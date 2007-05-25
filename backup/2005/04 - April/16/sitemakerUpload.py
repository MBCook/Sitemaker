####################################################################
#
#	SiteMaker version 0.1
#
#	Copyright 2005.02.22 Michael Cook, foobarsoft@foobarsoft.com
#
#	http://www.foobarsoft.com
#
#	Do not distribute, do not remove this notice
#
####################################################################

import os
import time
import datetime
from ftplib import FTP

def main():
	"""The main thing that does... things!"""

	global specialNames, asciiList, specialDirs

	specialNames = ["sections.txt", "template.txt",
					"style.txt", "templateEntry.txt",
					"templateBody.txt", "sitemaker.py",
					"sitemakerRoutines.py", "sitemakerUpload.py",
					"sitemakerRoutines.pyc", "sitemakerUpload.pyc"]

	specialDirs = ["manual"]

	asciiList = [".py", ".htm", ".html", ".c", ".cpp", ".h",
					".m", ".java"]

	remoteBase = "/home/username/my_website"
	localBase = "/Users/michael/Sites"

	# Start by connecting and changing to the www directory.

	ftp = FTP()

	print "Connecting to server..."

	ftp.connect("my_user.myftpserver.com")

	print "Loggin in..."

	ftp.login("my_user", "secret_password")

	print "Chaning to www directory..."

	ftp.cwd(remoteBase)

	processDirectory("", localBase, remoteBase, 1, ftp, True)

	print "Done processing, closing connection..."

	try:
		ftp.quit()	# Ask to quit
	except:
		ftp.close() # If they don't want to quit, we'll force it

	print "Connection closed. Goodbye!"

def processDirectory(dirName, localBase, remoteBase, depth, ftp, doUpload):
	"""Process a directory by sending relevent files."""

	printAtDepth(depth, "Staring on directory '" + dirName + "'.")

	localPath = os.path.join(localBase, dirName)
	remotePath = os.path.join(remoteBase, dirName)

	printAtDepth(depth, "Switching to remote directory %s..." % remotePath)

	try:
		ftp.cwd(remotePath)
	except:
		# If that didn't work, the directory must not exist. Create it!
		ftp.mkd(remotePath)
		ftp.cwd(remotePath)

	# TEST CODE

#	global remoteLines

#	remoteLines = [];
	
#	ftp.retrlines('LIST', addToRemoteLines)	# This is basically "ls", I hope.

#	localDict = dirToDateDict(localPath)
#	remoteDict = linesToDateDict(remoteLines)

#	updateList = needsUpdate(localDict, remoteDict, 0, ".txt")

	# END TEST

	filesInLocal = os.listdir(localPath)

	normal = []
	dir = []

	for file in filesInLocal:
		tempPath = os.path.join(localPath, file)
		if os.path.isdir(tempPath):
			if isSpecialDir(file):
				pass
			else:
				dir.append(file)
		else:
			normal.append(file)

	for file in normal:
		if isSpecialFile(file):
			# Skip it
			printAtDepth(depth + 1, "Skipping %s, it was special..." % file)
		else:
			(name, extention) = os.path.splitext(file)
			if extention == ".txt":
				# Skip it
				printAtDepth(depth + 1, "Skipping %s, it was a .txt file..." % file)
			else:
				if doUpload:
					fullPath = os.path.join(localBase, dirName, file)
					fileObj = open(fullPath)
					(theDir, fileName) = os.path.split(file)

					if isAsciiFile(extention):
						printAtDepth(depth + 1, "Sending %s as ASCII..." % file)
						ftp.storlines("STOR %s" % fileName, fileObj)
					else:
						printAtDepth(depth + 1, "Sending %s as binary..." % file)
						ftp.storbinary("STOR %s" % fileName, fileObj)

					fileObj.close()
				else:
					printAtDepth(depth + 1, "Upload would have occured on %s..." % file)

	printAtDepth(depth, "Done processing directory, processing subdirs...")

	for theDir in dir:
		newDir = os.path.join(dirName, theDir)
		processDirectory(newDir, localBase, remoteBase, depth + 1, ftp, doUpload)

	printAtDepth(depth, "Done processing subdirectories.")

def addToRemoteLines(newLine):
	"""The callback used to get the lines from a 'list' command on the server"""

	global remoteLines

	remoteLines.append(newLine)

def printAtDepth(depth, string):
	"""Put spaces to depth."""

	retVal = ""

	for i in range(depth):
		retVal += "	 "

	print retVal + string	

def isSpecialFile(theName):
	"""Check to see if the file is a special file."""

	global specialNames

	for special in specialNames:
		if special == theName:
			return True

	if theName[0] == ".":
		return True

	return False

def isSpecialDir(theName):
	"""Check to see if the directory is a special one."""

	global specialDirs

	for special in specialDirs:
		if special == theName:
			return True

	if theName[0] == ".":
		return True

	return False

def isAsciiFile(theType):
	"""Check to see if the file is a special file."""

	global asciiList

	for special in asciiList:
		if special == theType:
			return True

	return False

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
				timeStruct = (currentYear, timeStruct[1], timeStruct[2], timeStruct[3], 
								timeStruct[4], timeStruct[5], timeStruct[6], timeStruct[7],
								timeStruct[8])

			timeInSec = time.mktime(timeStruct)

			dateDict[name] = timeInSec

	return dateDict

def dirToDateDict(theDir):
	"""Get a list of files in current directory and put into a dict of dates."""

	dateDict = {}

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

def needsUpdate(sourceDict, destDict, offsetTime, filterExt):
	"""Given the two dictionaries of times, figure out which files to update."""

	updateList = []

	for filename in sourceDict.keys():

		(name, extention) = os.path.splitext(filename)

		if isSpecialFile(filename):
			# This file is special, we wouldn't upload it anyway
			pass
		elif extention == filterExt:
			# Skip it, we don't do these files
			pass
		else:
			if destDict.has_key(filename):
				if ((sourceDict[filename] + offsetTime) > destDict[filename]):
					# The file has been updated, add it to the list
					updateList.append(filename)
			else:
				# The file isn't in the dest, so it would need to be uploaded
				updateList.append(filename)

	# Now that we have that list, return it

	return updateList

# This code runs the program

if __name__ == "__main__":
	main()
