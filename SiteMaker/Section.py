##############
# Section.py #
##############

from globalVars import *
import os
import routines
import re			# Regular Expressions
import datetime

class Section:
	"""A section of the website."""

	#################################
	# This is what childen override #
	#################################

	def processDirectory(self, path, nav, depth, config, globalConfig):
		raise NotImplementedError, "Section is an abstract class and should never be called."

		# Path is the path of the directory from the root
		# Nav is the content of the navigation frame
		# Depth is how deep we are (used for printAtDepth)
		# Config is the dictonary of config info about the directory
		# ForceUpdate is if we want to update everything no matter what

	###############################################################
	# Below here are the helper functions they are allowed to use #
	###############################################################

	def getConfig(self, dict, key, default = None):
		"""Read a configuration key for us from a dictionary."""

		return routines.getConfig(dict, key, default)

	def processSubdirectories(self, sections, nav, dir, depth, config, globalConfig):
		"""Step through the subsections and process them."""

		sectionList = sections.keys()
		sectionList.sort()

		for section in sectionList:
			if section != "home":	# Home is a virtual section and not processed

				self.printAtDepth(depth + 1, "Entering directory \"%s\"..." % section, 2)
	
				subDir = self.joinPaths(dir, section)
	
				subNav = self.makeNavigationHTML(subDir, globalConfig, section)

				subNav = nav.replace("<!-- " + section + " -->", subNav)
	
				self.processDirectorySelector(subDir, subNav, depth + 1, globalConfig)
	
				self.printAtDepth(depth + 1, "Leaving directory \"%s\"..." % section, 3)

	def joinPaths(self, path1, path2):
		"""Wrapper for routines.joinPaths"""

		return routines.joinPaths(path1, path2)

	def processDirectorySelector(self, path, nav, depth, forceUpdate):
		"""Calls processDirectorySelector for us."""

		routines.processDirectorySelector(path, nav, depth, forceUpdate)

	def findFileNames(self, fileNameList, fileNameRE):
		"""Find file names in the list that match the given regular expression."""

		expression = re.compile(fileNameRE)

		resultList = []

		for fileName in fileNameList:
			if expression.match(fileName) != None:
				resultList.append(fileName)

		resultList.sort()

		return resultList

	def printAtDepth(self, depth, string, code):
		"""Just a wrapper to printAtDepth in the routines file so sublcasses don't include it."""

		routines.printAtDepth(depth, string, code)

	def getTemplate(self, type, name):
		"""Get the template with the given name and type."""

		global templateDict

		try:
			stringName = "%s_%s" % (type.strip(), name.strip())
			return templateDict[stringName]
		except:
			raise KeyError, "No template with name '%s' and type '%s'." % (name, type)

	def getTemplateDate(self, name, type):
		"""Get the template with the given name and type."""

		global templateDateDict

		try:
			stringName = "%s_%s" % (name.strip(), type.strip())
			return templateDateDict[stringName]
		except:
			raise KeyError, "No template with name '%s' and type '%s'." % (name, type)

	def getSections(self, path):
		"""Wrapper to routines.getSections."""

		return routines.getSections(path)

	def makeNavigationHTML(self, path, config, subsection = None):
		"""A reference to the function to make the navigation HTML."""

		html = "<ul>\n"

		sections = self.getSections(path)

		dirBase = self.getConfig(config, "RemoteBase")

		if sections == {}:
			return ""

		tempList = []

		sectionList = sections.keys()
		sectionList.sort()

		for section in sectionList:							# Make a list with the name
			tempList.append((sections[section], section))	#	as the first element of a tuple

		tempList.sort()										# Sort it

		# Now we iterate over that, it should be in alphabetical order

		for secDir, section in tempList:
			html += '<li><a href="'

			if ((section == "home") or (section == None)):
				html += self.joinPaths(dirBase, path)
			else:
				html += self.joinPaths(dirBase, self.joinPaths(path, section))

			html += '">' + secDir + '</a><br/>\n'

			html += "<!-- " + section + " -->\n"

			html += "</li>\n"

		html += "</ul>\n"

		return html

	def readFileAsString(self, path):
		"""A wrapper to the function in the routines file."""

		return routines.readFileAsString(path)

	def readFileAsLines(self, path):
		"""Wrapper to routines.readFileAsLines."""

		return routines.readFileAsLines(path)

	def readFileAsPairs(self, path, concat = True):
		""" A wrapper to routines.readFileAsPairs."""

		return routines.readFileAsPairs(path, concat)

	def writeFile(self, path, content):
		"""Write the content to the file at path"""

		try:
			fileHandle = open(path, "w")
			fileHandle.write(content)
			fileHandle.close()
		except:
			raise IOError, "Unable to write to file '%s'." % path

	def formatDateString(self, fromString):
		"""Turn a date in 'YYYYMMDD' into 'MM/DD/YYYY'"""

		dateInt = int(fromString)

		year = dateInt / 10000
		dateInt -= year * 10000
		month = dateInt / 100
		dateInt -= month * 100

		dateString = "%i/%i/%i" % (month, dateInt, year)

		return dateString
		
	def formatDateStringAsRFC822(self, fromString, fromTimestamp = False):
		"""Turn a date in 'YYYYMMDD' into 'Day, DD Mon YYYY 00:00:00'"""

		if fromTimestamp:
			fromString = datetime.datetime.fromtimestamp(fromString).strftime("%Y%m%d")

		dateInt = int(fromString)

		year = dateInt / 10000
		dateInt -= year * 10000
		month = dateInt / 100
		dateInt -= month * 100

		theDate = datetime.date(year, month, dateInt)

		return theDate.strftime("%a, %d %b %Y %H:%M:%S GMT")

	def getDirectoryContentsHelper(self, contents):
		"""A wrapper to routines.getDirectoryContentsHelper()."""

		return routines.getDirectoryContentsHelper(contents)

	def getDirectoryContents(self, path):
		"""Wrapper to routines.getDirectoryContents()."""

		return routines.getDirectoryContents(path)

	def getTemplate(self, type, name):
		"""Return the template with the given name of the given type.

			Returned in a tuple of (text, templateDate)."""

		global templateDict
		
		dictionaryKey = "%s_%s" % (type, name)

		if templateDict.has_key(dictionaryKey):
			return templateDict[dictionaryKey]
		else:
			raise KeyError, "Unknown template with name '%s' of type '%s'." % (name, type)

	def readConfigFile(self, path):
		"""A wrapper to routines.readConfigFile."""

		return routines.readConfigFile(path)

	def isSpecialFile(self, filename):
		"""Wrapper to routines.isSpecialFile()."""

		return routines.isSpecialFile(filename)

	def isSpecialDir(self, filename):
		"""Wrapper to routines.isSpecialDir()."""

		return routines.isSpecialDir(filename)

	##################################
	# DON'T USE THESE FOR SUBCLASSES #
	#								 #
	#		Internal use only!		 #
	##################################

	def isAsciiFile(self, fileExtention):
		"""Wrapper to routines.isAsciiFile()."""

		return routines.isAsciiFile(fileExtention)