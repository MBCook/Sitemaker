##################
# BlogSection.py #
##################

from globalVars import *
from Section import *

import re

# Note that for now, we only use the Title, Date, and Content keywords.
# Now we also use TemplateName

class BlogSection(Section):

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

		entryTemplateName = self.getConfig(config, "EntryTemplate", "Default")
		pageTemplateName = self.getConfig(config, "PageTemplate", "Default")
		feedTemplateName = self.getConfig(config, "FeedTemplate", "Default")
		feedEntryTemplateName = self.getConfig(config, "FeedEntryTemplate", "Default")

		entryTemplateDate = self.getTemplateDate(entryTemplateName, "Entry")
		pageTemplateDate = self.getTemplateDate(pageTemplateName, "Page")
		feedTemplateDate = self.getTemplateDate(feedTemplateName, "Feed")
		feedEntryTemplateDate = self.getTemplateDate(feedEntryTemplateName, "FeedEntry")		

		try:
			sectionDate = fileDateDict["sections.txt"]
		except:
			sectionDate = 0

		templateDate = max(entryTemplateDate, pageTemplateDate, sectionDate)

		# We'll have to know what the sections are

		sections = self.getSections(path)

		# Now we get the list of files that will contain our entries

		entryList = self.findFileNames(fileList, self.dateFileNameRE)
		entryList.reverse()

		# Now get the dates on some files

		dateOnNewestFile = 0
		dateOnOutput = 0

		for fileName in entryList:
			if fileDateDict[fileName] > dateOnNewestFile:
				dateOnNewestFile = fileDateDict[fileName]

		try:
			dateOnOutput = fileDateDict["index.html"]
		except:
			try:
				dateOnOutput = fileDateDict["feed.xml"]
			except:
				dateOnOutput = 0

		# With that info, we should be able to do what we want.

		forceUpdate = self.getConfig(globalConfig, "ForceUpdate")

#		print "newest: %i, template: %i, output: %i" % (dateOnNewestFile, templateDate, dateOnOutput)
#
#		if forceUpdate:
#			print "Update forced."
#			print forceUpdate
#		if dateOnNewestFile > dateOnOutput:
#			print "Newer file than output by %i seconds." % (dateOnNewestFile - dateOnOutput)
#			print "  newest: %i, output: %i" % (dateOnNewestFile, dateOnOutput)
#		if templateDate > dateOnOutput:
#			print "Template file than output by %i seconds." % (templateDate - dateOnOutput)
#			print "  template: %i, output: %i" % (templateDate, dateOnOutput)
#
		if (forceUpdate or (dateOnNewestFile > dateOnOutput) or (templateDate > dateOnOutput)):

			# OK, we step through each blog entry backwards adding as we go to the body HTML

			titleText = self.getConfig(config, "Title")
			bodyHtml = ""
			bodyFeed = ""

			for fileName in entryList:

				filePath = self.joinPaths(path, fileName)
				(tempText, tempFeed) = self.readEntry(filePath, fileName, entryTemplateName, feedEntryTemplateName, globalConfig)
				bodyHtml = bodyHtml + tempText
				bodyFeed = bodyFeed + tempFeed

			# Now we finish the blog page

			filePath = self.joinPaths(path, "index.html")

			bodyTemplate = self.getTemplate(pageTemplateName, "Page")
			bodyTemplate = bodyTemplate.replace("###BODY###", bodyHtml)
			bodyTemplate = bodyTemplate.replace("###NAV###", nav)
			bodyTemplate = bodyTemplate.replace("###TITLE###", titleText)

			rssURL = self.joinPaths(self.getConfig(globalConfig, "HttpPath"), path) + "/feed.xml"

			rssStuff = "--> <link rel=\"alternate\" title=\"RSS\" href=\"" + rssURL + "\" type=\"application/rss+xml\"> <!-- "

			bodyTemplate = bodyTemplate.replace("###RSS###", rssStuff)

			self.printAtDepth(depth + 1, "Writing 'index.html'...", 1)

			outputFile = self.joinPaths(path, "index.html")

			self.writeFile(outputFile, bodyTemplate)
			fileProcessCount = fileProcessCount + 1	# OK, we processed it...
			fileUpdateCount = fileUpdateCount + 1	# ...and it was updated

			# Now do the same thing for the feed

			filePath = self.joinPaths(path, "feed.xml")

			bodyTemplate = self.getTemplate(feedTemplateName, "Feed")
			bodyTemplate = bodyTemplate.replace("###FEED_ITEMS###", bodyFeed)
			bodyTemplate = bodyTemplate.replace("###FEED_TITLE###", self.getConfig(config, "FeedTitle", titleText))
			bodyTemplate = bodyTemplate.replace("###FEED_LINK###", self.joinPaths(self.getConfig(globalConfig, "HttpPath"), self.joinPaths(path, "feed.xml")))
			bodyTemplate = bodyTemplate.replace("###FEED_DESCRIPTION###", self.getConfig(config, "FeedDescription", titleText))
			bodyTemplate = bodyTemplate.replace("###FEED_EMAIL###", self.getConfig(config, "FeedEmail", "noone@nowhere.com"))
			bodyTemplate = bodyTemplate.replace("###FEED_DATE###", self.formatDateStringAsRFC822(dateOnNewestFile, True))

			self.printAtDepth(depth + 1, "Writing 'feed.xml'...", 1)

			outputFile = self.joinPaths(path, "feed.xml")

			self.writeFile(outputFile, bodyTemplate)
			fileProcessCount = fileProcessCount + 1	# OK, we processed it...
			fileUpdateCount = fileUpdateCount + 1	# ...and it was updated

		else:
			self.printAtDepth(depth + 1, "Skipping 'index.html'/'feed.xml', no update needed...", 4)
			fileProcessCount = fileProcessCount + 2	# Skipping counts as processing
		

		# Once we get here, we should have updated everything that needed it
		# Now we have to process each subsection that we'll be working on

		self.processSubdirectories(sections, nav, path, depth, config, globalConfig)

	##########################################################################
	# Any helper functions we want go under here, they are internal use only #
	##########################################################################

	dateFileNameRE = "^[0-9]{8}[a-z]?.txt$"	# Filenames of 8 digits with the extention ".txt"
											# There is an optional entry letter just before ".txt"

	def readEntry(self, filePath, fileName, entryTemplateName, blogEntryTemplateName, globalConfig):
		"""Read and create a single blog entry from the given file."""

		fileDict = self.readFileAsPairs(filePath, True)
	
		dateText = self.formatDateString(fileDict["Date"])
		contentText = fileDict["Content"]
		entryTitleText = fileDict["Title"]

		tempText = self.getTemplate(entryTemplateName, "Entry")

		tempText = tempText.replace("###TITLE###", entryTitleText)
		tempText = tempText.replace("###DATE###", dateText)
		tempText = tempText.replace("###TEXT###", contentText)
		tempText = tempText.replace("###ANCHOR###", fileName[0:-4])

		# Now fix the links
		
		httpPath = self.getConfig(globalConfig, "HttpPath")
		improvedLink = httpPath + "/" + filePath[0:-len(fileName)]

		tempFeed = self.getTemplate(blogEntryTemplateName, "FeedEntry")
		
		tempFeed = tempFeed.replace("###ENTRY_TITLE###", entryTitleText)
		tempFeed = tempFeed.replace("###ENTRY_URL###", improvedLink + "index.html#" + fileName[0:-4])
		tempFeed = tempFeed.replace("###DESCRIPTION###", contentText)
		tempFeed = tempFeed.replace("###ENTRY_DATE###", self.formatDateStringAsRFC822(fileDict["Date"]))
		
		# I HATE REGULAR EXPRESSIONS

		pat = "href=\"(?!https?://)/([^\"]*)\""		# Absolute links
		rep = "href=\"" + httpPath + "/" + "\\1\""

		p = re.compile(pat, re.IGNORECASE)
		
		tempFeed = re.sub(p, rep, tempFeed)
		
		pat = "href=\"(?!https?://)([^\"]*)\""		# Relative links
		rep = "href=\"" + improvedLink + "\\1\""

		p = re.compile(pat, re.IGNORECASE)
		
		tempFeed = re.sub(p, rep, tempFeed)

		pat = "src=\"(?!https?://)/([^\"]*)\""
		rep = "src=\"" + httpPath + "/" + "\\1\""

		p = re.compile(pat, re.IGNORECASE)
		
		tempFeed = re.sub(p, rep, tempFeed)

		pat = "src=\"(?!https?://)([^\"]*)\""
		rep = "src=\"" + improvedLink + "\\1\""

		p = re.compile(pat, re.IGNORECASE)
		
		tempFeed = re.sub(p, rep, tempFeed)

		return (tempText, tempFeed)
