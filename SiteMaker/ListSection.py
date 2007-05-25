##################
# ListSection.py #
##################

from globalVars import *
from Section import *

# Note that for now, we only use the Title, Date, and Content keywords.
# Now we also use TemplateName

class ListSection(Section):

	####################################################################
	# This is what we over-ride from our parent that does all the work #
	####################################################################

	def processDirectory(self, path, nav, depth, config, globalConfig):
		"""Given the given information, process the directory."""

		global fileUpdateCount, fileProcessCount

		# First let's get some information about the directory we'll be working with

		directoryContents = self.getDirectoryContents(path)

		# Now get the two dictionaries from that

		(fileDateDict, fileTypeDict) = self.getDirectoryContentsHelper(directoryContents)

		fileList = fileDateDict.keys()

		# Now we need the date of most recent update of the templates that we use

		listTemplateName = self.getConfig(config, "ListTemplate", "Default")
		pageTemplateName = self.getConfig(config, "PageTemplate", "Default")

		listTemplateDate = self.getTemplateDate(listTemplateName, "List")
		pageTemplateDate = self.getTemplateDate(pageTemplateName, "Page")

		try:
			entrySetupDate = fileDateDict["entrySetup.txt"]
		except:
			entrySetupDate = 0

		try:
			sectionDate = fileDateDict["sections.txt"]
		except:
			sectionDate = 0

		templateDate = max(listTemplateDate, pageTemplateDate, sectionDate, entrySetupDate)

		# Now we need to load the info from entrySetupDate

		entrySetupContents = self.readFileAsLines(self.joinPaths(path, "entrySetup.txt"))

		entryFormula = entrySetupContents[0]
		entrySort = entrySetupContents[1]
		headerEnglish = entrySetupContents[2]

		entryFormulaList = entryFormula.split(",")
		entryFormula = []

		for item in entryFormulaList:
			entryFormula.append(item.strip())

		entrySortList = entrySort.split(",")
		entrySort = []

		for item in entrySortList:
			entrySort.append(item.strip())

		headerEnglishList = headerEnglish.split(",")
		headerEnglish = []

		for item in headerEnglishList:
			headerEnglish.append(item.strip())

		entryRequirements = self.decodeEntryRequirements(entrySetupContents[3:])	# All but first

		# We'll have to know what the sections are

		sections = self.getSections(path)

		# Now we get the list of files that will contain our entries

		entryList = []

		for fileName in fileList:
			if self.isSpecialFile(fileName):
				fileList.remove(fileName)		# Special files need to be removed from the list
			else:
				if fileName[-4:] == ".txt":	# If it's a text file
					entryList.append(fileName)
				else:
					pass					# We won't check non .txt files

		# Now get the dates on some files

		dateOnNewestFile = 0
		dateOnOutput = 0

		for fileName in entryList:
			if fileDateDict[fileName] > dateOnNewestFile:
				dateOnNewestFile = fileDateDict[fileName]

		try:
			dateOnOutput = fileDateDict["index.html"]
		except:
			dateOnOutput = 0

		# With that info, we should be able to do what we want.

		forceUpdate = self.getConfig(globalConfig, "ForceUpdate")
#
#		print "newest: %i, template: %i, output: %i" % (dateOnNewestFile, templateDate, dateOnOutput)
#
		if (forceUpdate or (dateOnNewestFile > dateOnOutput) or (templateDate > dateOnOutput)):
			# For the process check our the description in list.txt

			titleText = self.getConfig(config, "Title")
			bodyHtml = ""

			fileDictionary = {}

			listTemplateDict = self.getTemplate(listTemplateName, "List")

			# First we load up the contents of all the files into a dictionary

			for fileName in entryList:

				filePath = self.joinPaths(path, fileName)
				tempDict = self.readFileAsPairs(filePath, True)
				tempDict["linkName"] = fileName[:-4]
				fileDictionary[fileName] = tempDict

			# Let's make the header

			headerList = []

			for fileName in fileDictionary:				# See below for how all this works
				tempList = []
				dict = fileDictionary[fileName]
				for item in entrySort:
					value = dict[item]
					value = value.strip()
					if item == "Rating":
						value = 100 - int(dict[item])
					tempList.append(value)
				tempList.append(dict["linkName"])
				headerList.append(tempList)

			headerList.sort()

			# Now we make the header

			bodyHtml = bodyHtml + "<p align=center>\n"
			bodyHtml = bodyHtml + "<table border=1>\n"
			bodyHtml = bodyHtml + "<tr>\n"

			for item in headerEnglish:
				bodyHtml = bodyHtml + "<th>%s</th>" % item

			bodyHtml = bodyHtml + "</tr>\n"

			for list in headerList:				# For each file we are listing in the header
				listSize = len(list)
				bodyHtml = bodyHtml + "<tr>"
				for i in range(listSize - 1):	# For each item listed in the header (except the last,
												#	which is the filename
					if headerEnglish[i] == "Item Name":
						bodyHtml = bodyHtml + "<td><a href=\"#%s\">%s</a></td>" % (list[-1], list[i])
					elif headerEnglish[i] == "Rating":
						bodyHtml = bodyHtml + "<td align=center>%s%%</td>" % (100 - list[i])
					else:							# Not last element, no link
						bodyHtml = bodyHtml + "<td>%s</td>" % list[i]
				bodyHtml = bodyHtml + "</tr>\n"

			bodyHtml = bodyHtml + "</table>\n"
			bodyHtml = bodyHtml + "</p>\n"

			# Now we sort entry list by our sort order

			listToSort = []

			for fileName in fileDictionary:
				tempList = []
				dict = fileDictionary[fileName]			# Get the dictionary for the file
				for item in entrySort:					# For each parameter to sort by
					value = dict[item]
					tempList.append(value.strip())		# Add it to the temp list
				tempList.append(fileName)				# Filename as the last element
				listToSort.append(tempList)				# Add the temp list to the listToSort

			listToSort.sort()							# Sort the list

			fileOrder = []

			for list in listToSort:						# For each element of the sorted list
				fileOrder.append(list[-1])				# Add the last element (the file name)

			# Now we use all that to filli n the bodyHtml variable

			for entryName in fileOrder:
				entryHtml = self.applyListTemplate(listTemplateDict, fileDictionary[entryName],
														entryFormula, entryRequirements)
				bodyHtml = bodyHtml + entryHtml

			# Now we finish the page

			filePath = self.joinPaths(path, "index.html")

			bodyTemplate = self.getTemplate(pageTemplateName, "Page")
			bodyTemplate = bodyTemplate.replace("###BODY###", bodyHtml)
			bodyTemplate = bodyTemplate.replace("###NAV###", nav)
			bodyTemplate = bodyTemplate.replace("###TITLE###", titleText)

			self.printAtDepth(depth + 1, "Writing 'index.html'...", 1)

			outputFile = self.joinPaths(path, "index.html")

			self.writeFile(outputFile, bodyTemplate)
			fileProcessCount = fileProcessCount + 1	# OK, we processed it...
			fileUpdateCount = fileUpdateCount + 1	# ...and it was updated

		else:
			self.printAtDepth(depth + 1, "Skipping 'index.html', no update needed...", 4)
			fileProcessCount = fileProcessCount + 1	# Skipping counts as processing
		

		# Once we get here, we should have updated everything that needed it
		# Now we have to process each subsection that we'll be working on

		self.processSubdirectories(sections, nav, path, depth, config, globalConfig)

	##########################################################################
	# Any helper functions we want go under here, they are internal use only #
	##########################################################################

	def decodeEntryRequirements(self, requirementList):
		"""Take the list of requirements for a line and turn it into something we understand."""

		requirementDict = {}

		for line in requirementList:
			lineList = []
			line = line.strip()
			lineList = line.split(",")

			if len(lineList) < 2:	# Is there enough there?
				raise NameError, "Unable to process requirement list, line was too short: %s" % line
			if lineList[1].strip() == "NONE":	# Is it our sepcial token?
				requirementDict[lineList[0].strip()] = None
			else:
				# OK, we'll actually have to process this. Luckily it's easy.
				reqList = []
				for item in lineList[1:]:	# Each element but the first
					reqList.append(item.strip())
				requirementDict[lineList[0].strip()] = reqList

		return requirementDict		# That's it

	def applyListTemplate(self, templateDict, entryDict, entryFormula, entryRequirements):
		"""Given the rules and whatnot, fill in an entry."""

		entryHtml = ""

		for item in entryFormula:
			itemHtml = ""
			
			# First we see if the item is an "OR".
			
			if item.count("|") >= 1:
				# It's an OR, so we'll handle it
				# We step through each option seeing if it works, first get the list

				optionList = item.split("|")

				for option in optionList:
					option = option.strip()

					if self.requirementsSatisfied(entryDict, entryRequirements[option]):
						# Requirements are satisfied
						itemHtml = templateDict[option]
						if entryRequirements[option]:
							for requirement in entryRequirements[option]:	# Replace what's needed
								itemHtml = itemHtml.replace("###%s###" % requirement.upper(), 
																entryDict[requirement])
						itemHtml = itemHtml + "\n"
						break;	# Found one that works, so let's leave the looop

				# If we are here, either we found a working option (and itemHtml has what we need)
				#	or we DIDN'T find a working option, so we skip it (itemHtml is "")

			else:
				# It's just normal, simple, easy to do
				if self.requirementsSatisfied(entryDict, entryRequirements[item]):
					# Requirements are satisfied
					itemHtml = templateDict[item]
					if entryRequirements[item]:
						for requirement in entryRequirements[item]:	# Replace what's needed
							itemHtml = itemHtml.replace("###%s###" % requirement.upper(), 
															entryDict[requirement])
					itemHtml = itemHtml + "\n"
				else:
					# Something missing, we'll skip the line
					pass

			# Now we add the item html to the entry html

			entryHtml = entryHtml + itemHtml

		# Noww we're done

		return entryHtml

	def requirementsSatisfied(self, sourceDict, thingsNeeded):
		"""Check to see if the dictionary contains everything we need."""

		if thingsNeeded == None:	# Check for our special case
			return True

		for requirement in thingsNeeded:
			if sourceDict.has_key(requirement):
				pass
			else:
				return False

		return True