#####################
# GallerySection.py #
#####################

from globalVars import *
from Section import *

import EXIF

# Note that for now, we only use the Title keyword.
# Now we also use the template names.

class GallerySection(Section):

	####################################################################
	# This is what we over-ride from our parent that does all the work #
	####################################################################

	def processDirectory(self, path, nav, depth, config, globalConfig):
		"""Given the given information, process the directory."""

		# Need gallery title and description

		global fileUpdateCount, fileProcessCount

		# First let's get some information about the directory we'll be working with

		directoryContents = self.getDirectoryContents(path)

		# Now get the two dictionaries from that

		(fileDateDict, fileTypeDict) = self.getDirectoryContentsHelper(directoryContents)

		fileList = fileDateDict.keys()

		galleryTitle = config["Title"]
		galleryDescFile = self.joinPaths(path, "index.txt")
		galleryDesc = self.readFileAsString(galleryDescFile)

		# Now we need the date of most recent update of the templates that we use

		galleryTemplateName = self.getConfig(config, "GalleryTemplate", "Default")
		entryTemplateName = self.getConfig(config, "GalleryEntry", "Default")
		largeTemplateName = self.getConfig(config, "GalleryLarge", "Default")
		pageTemplateName = self.getConfig(config, "PageTemplate", "Default")

		galleryTemplateDate = self.getTemplateDate(galleryTemplateName, "Gallery")
		entryTemplateDate = self.getTemplateDate(entryTemplateName, "GalleryEntry")
		largeTemplateDate = self.getTemplateDate(largeTemplateName, "GalleryLarge")
		pageTemplateDate = self.getTemplateDate(pageTemplateName, "Page")

		try:
			sectionDate = fileDateDict["sections.txt"]
		except:
			sectionDate = 0

		templateDate = max(entryTemplateDate, pageTemplateDate, sectionDate,
							largeTemplateDate, galleryTemplateDate)

		# We'll have to know what the sections are

		sections = self.getSections(path)

		# Now we get the list of files that will contain our entries

		entryList = fileDateDict.keys()

		newList = []

		for entry in entryList:
			if entry[-4:] == ".jpg":
				# It's an image...
				if entry[-10:] == "_thumb.jpg":
					# This is a thumbnail file, we'll ignore it
					pass
				else:
					newList.append(entry)	# It's a normal image, append it to the list
			else:
				# Not an image, so we'll ignore it
				pass

		entryList = newList	# Put the list of files where we want it.

		# Now get the dates on some files

		dateOnNewestFile = fileDateDict["index.txt"]
		dateOnOutput = 0

		for fileName in entryList:
			if fileDateDict[fileName] > dateOnNewestFile:
				dateOnNewestFile = fileDateDict[fileName]

			newFileName = "%s.txt" % fileName[:-4]				# Check if the description is updated
			if fileDateDict[newFileName] > dateOnNewestFile:
				dateOnNewestFile = fileDateDict[newFileName]

		try:
			dateOnOutput = fileDateDict["index.html"]
		except:
			dateOnOutput = 0

		# With that info, we should be able to do what we want.

		forceUpdate = self.getConfig(globalConfig, "ForceUpdate")

		galleryText = ""

		if (forceUpdate or (dateOnNewestFile > dateOnOutput) or (templateDate > dateOnOutput)):

			# OK, we step through each file creating it's page and adding it's content to 
			#	galleryText, which holds all the entries in the galleryIndex

			entryList.sort()

			for photo in entryList:
				# Note that if anything needs updating, we update EVERYTHING.
				#	This is simply easier than checking each file, then going back
				#	and re-reading stuff to make the index page.
				# First, load the text from the file that describes the picture

				photoFile = self.joinPaths(path, photo)
				textFile = "%s.txt" % photoFile[:-4]
				descDict = self.readFileAsPairs(textFile, True)

				# Now get the EXIF info

#				print "About to extract EXIF data on " + photo

#				exifDict = self.extractExif(photoFile)

#				print "Got EXIF data on " + photo

				# Now the EXIF text string made from the data above

#				exifText = self.makeExifText(exifDict)
				exifText = "<p>EXIF data currently not available.</p>\n"

				# Now we assemble some stuff, first the gallery entry.

				picPage = "%s.html" % photo[:-4]
				picPage = picPage.lower()				# Make sure we're lower case

				thumb = "%s_thumb.jpg" % photo[:-4]

				galleryEntry = self.getTemplate(entryTemplateName, "GalleryEntry")
				galleryEntry = galleryEntry.replace("###PICPAGE###", picPage)
				galleryEntry = galleryEntry.replace("###PICSOURCE###", thumb)
				galleryEntry = galleryEntry.replace("###DESCRIPTION###", descDict["Short"])

				# And add it to the gallery

				galleryText = galleryText + galleryEntry

				# Now we'll make the close-up-look page

				largeText = self.getTemplate(largeTemplateName, "GalleryLarge")
				largeText = largeText.replace("###PICTURELARGE###", photo)
				largeText = largeText.replace("###EXIF###", exifText)
				largeText = largeText.replace("###SHORTCOMMENT###", descDict["Short"])
				largeText = largeText.replace("###LONGCOMMENT###", descDict["Long"])

				# Now we embed that into a page

				pageText = self.getTemplate(pageTemplateName, "Page")
				pageText = pageText.replace("###BODY###", largeText)
				pageText = pageText.replace("###NAV###", nav)
				pageText = pageText.replace("###TITLE###", "Photo: %s" % descDict["Short"])

				pagePath = self.joinPaths(path, picPage)

				self.printAtDepth(depth + 1, "Writing '%s'..." % picPage, 1)

				self.writeFile(pagePath, pageText)
				fileProcessCount = fileProcessCount + 1	# We processed it.
				fileUpdateCount = fileUpdateCount + 1	# And we updated it.

			# OK, the FOR loop is done, so we're ready for the main page.

			galleryShell = self.getTemplate(galleryTemplateName, "Gallery")
			galleryShell = galleryShell.replace("###GALLERYTITLE###", galleryTitle)
			galleryShell = galleryShell.replace("###GALLERYTEXT###", galleryDesc)
			galleryShell = galleryShell.replace("###GALLERYENTRIES###", galleryText)

			bodyTemplate = self.getTemplate(pageTemplateName, "Page")
			bodyTemplate = bodyTemplate.replace("###BODY###", galleryShell)
			bodyTemplate = bodyTemplate.replace("###NAV###", nav)
			bodyTemplate = bodyTemplate.replace("###TITLE###", galleryTitle)

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

	def makeExifText(self, exifDict):
		"""Given the EXIF data in a dictionary, print out the information."""

		if exifDict is None:
			text = "<p>EXIF data currently not available.</p>\n"
		else:
			text = "<p><pre>"
			if exifDict["Width"] is not None:
				text = text + "Width:        %d pixels\n" % exifDict["Width"]
			if exifDict["Height"] is not None:
				text = text + "Height:       %d pixels\n" % exifDict["Height"]
			text = text + "<br />\n"
			if exifDict["Date"] is not None:
				text = text + "Date/Time:    %s\n" % exifDict["Date"]
			text = text + "<br />\n"
			if exifDict["ISO"] is not None:
				text = text + "ISO:          %i speed\n" % exifDict["ISO"]
			if exifDict["F-Stop"] is not None:
				text = text + "Aperature:    %s F-stops\n" % exifDict["F-Stop"]
			if exifDict["Shutter"] is not None:
				text = text + "Shutter:      1/%i seconds\n" % exifDict["Shutter"]
			if exifDict["Mode"] is not None:
				text = text + "Mode:         %s\n" % exifDict["Mode"]
			if exifDict["Lens"] is not None:
				text = text + "Focal length: %s mm\n" % exifDict["Lens"]
			if exifDict["Distance"] is not None:
				text = text + "Focal dist:   %s m\n" % exifDict["Distance"]
			text = text + "<br />\n"
			if exifDict["Make"] is not None and exifDict["Model"] is not None:
				text = text + "Camera:    %s %s\n" % (exifDict["Make"], exifDict["Model"])
			text = text + "</pre></p>\n"

		return text

	def extractExif(self, filename):
		"""Take the given filename and extract the EXIF information."""

		if filename[-4:] == ".jpg":
			try:
				theImage = open(filename, "rb")
			except:
				raise IOError("Unable to open '%s' to get EXIF data." % filename)

			# We're all set. Time to read us some data

			try:
				tags = EXIF.process_file(theImage)
			except:
				return None

			theImage.close()

			print tags.keys()

			# Now we got the tags, lets take what we need

			retDict = {}

			try:
				retDict["Width"] = tags["ExifImageLength"]
			except:
				try:
					retDict["Width"] = tags["ImageWidth"]
				except:
					retDict["Width"] = tags["EXIF ExifImageWidth"]
				
			try:
				retDict["Height"] = tags["ExifImageHeight"]
			except:
				try:
					retDict["Height"] = tags["ImageHeight"]
				except:
					retDict["Height"] = tags["EXIF ExifImageLength"]

			try:
				retDict["Date"] = tags["DateTime"]
			except:
				try:
					retDict["Date"] = tags["DateTimeOrigional"]
				except:
					retDict["Date"] = tags["Image DateTime"]

			try:
				retDict["ISO"] = tags["ISOSpeedRatings"]
			except:
				try:
					retDict["ISO"] = tags["ISOSetting"]
				except:
					try:
						retDict["ISO"] = tags["ISOSelection"]
					except:
						try:
							retDict["ISO"] = tags["ISOSpeedRequested"]
						except:
							retDict["ISO"] = None

			try:
				retDict["F-Stop"] = tags["ApertureValue"]
			except:
				retDict["F-Stop"] = tags["EXIF FNumber"]

			try:
				retDict["Shutter"] = tags["ShutterSpeedValue"]
			except:
				try:
					retDict["Shutter"] = tags["ExposureTime"]
				except:
					retDict["Shutter"] = tags["EXIF ExposureTime"]

			try:
				retDict["Make"] = tags["Make"]
			except:
				retDict["Make"] = tags["Image Make"]
			
			try:
				retDict["Model"] = tags["Model"]
			except:
				retDict["Model"] = tags["Image Model"]

			try:
				retDict["Mode"] = tags["ExposureProgram"]
			except:
				try:
					retDict["Mode"] = tags["Image ExposureProgram"]
				except:
					retDict["Mode"] = None

			try:
				retDict["Lens"] = tags["FocalLength"]
			except:
				retDict["Lens"] = tags["EXIF FocalLength"]

			try:
				retDict["Distance"] = tags["SubjectDistance"]
			except:
				retDict["Distance"] = None

			# Return the dictionary

			return retDict
		else:
			return None