##################
# FileSection.py #
##################

from globalVars import *
from Section import *

class FileSection(Section):
	"""A section where all content is stored as flat text files, one per page."""

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

		pageTemplateName = self.getConfig(config, "PageTemplate", "Default")
		bodyTemplateName = self.getConfig(config, "BodyTemplate", "Default")

		pageTemplateDate = self.getTemplateDate(pageTemplateName, "Page")
		bodyTemplateDate = self.getTemplateDate(bodyTemplateName, "Body")

		try:
			sectionDate = fileDateDict["sections.txt"]
		except:
			sectionDate = 0

		templateDate = max(pageTemplateDate, bodyTemplateDate, sectionDate)

		# We'll have to know what the sections are

		sections = self.getSections(path)

		# With that info, we should be able to do what we want.

		forceUpdate = self.getConfig(globalConfig, "ForceUpdate")

		for fileName in fileList:

			fileNameNoExtention = fileName[:-4]
			fileNameExtention = fileName[-4:]
			fileNameFinal = fileNameNoExtention + ".html"
			fileDate = fileDateDict[fileName]
			filePath = self.joinPaths(path, fileName)

			outputName = fileNameNoExtention + ".html"

			outputPath = self.joinPaths(path, outputName)

			try:
				fileFinalDate = fileDateDict[fileNameFinal]
			except:
				fileFinalDate = 0
			
			if fileNameExtention == ".txt":
				# OK, it's a test file, so let's start out magic
				# First let's see if it is a file we want to work with

				if fileTypeDict[fileName] != "Special":
					# OK it's a file for us.
					# Does it need an update?
#
#					print "newest: %i, template: %i, output: %i" % (fileDate, templateDate, fileFinalDate)
#
					if (forceUpdate or (fileDate > fileFinalDate) or (templateDate > fileFinalDate)):
						fileDict = self.readFileAsPairs(filePath, True)

						dateText = self.formatDateString(fileDict["Date"])
						contentText = fileDict["Content"]
						titleText = fileDict["Title"]

						contentTemplate = self.getTemplate(bodyTemplateName, "Body")
						contentTemplate = contentTemplate.replace("###DATE###", dateText)
						contentTemplate = contentTemplate.replace("###TEXT###", contentText)

						pageText = self.getTemplate(pageTemplateName, "Page")
						pageText = pageText.replace("###BODY###", contentTemplate)
						pageText = pageText.replace("###NAV###", nav)
						pageText = pageText.replace("###TITLE###", titleText)

						self.printAtDepth(depth + 1, "Writing '%s'..." % outputName, 1)

						self.writeFile(outputPath, pageText)
						fileProcessCount = fileProcessCount + 1	# OK, we processed it...
						fileUpdateCount = fileUpdateCount + 1	# ...and it was updated
					else:
						self.printAtDepth(depth + 1, "Skipping '%s', no update needed..." % outputName, 4)
						fileProcessCount = fileProcessCount + 1	# Skipping counts as processing

		# Once we get here, we should have updated everything that needed it
		# Now we have to process each subsection that we'll be working on

		self.processSubdirectories(sections, nav, path, depth, config, globalConfig)

		# OK, we're done (we hope)

	##########################################################################
	# Any helper functions we want go under here, they are internal use only #
	##########################################################################

