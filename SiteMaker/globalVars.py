#################
# globalVars.py #
#################

global specialFiles, specialDirectories, asciiExtentions
global printStyle, templateDict, fileProcessCount, fileUpdateCount
global templateDateDict, sectionObjects, updateChecked, updatePerformed

# printStyle tells us how we print things out (text, code, both, nothing)

printStyle = "text"

# specialFiles is a list of files we never mess with when processing
# Note: hidden files (those starting with a ".") are ignored

specialFiles = ["config.txt",						# Program configuration file
				"sections.txt",						# List of subsections in DIR
				"style.txt",						# Style of this DIR
				"sections.txt",						# The list of subsections to this section
				"entrySetup.txt",					# How to construct an entry
				"tempateEntry.txt",					# Basic entry template
				"templateBody.txt",					# Basic page template
				"templateList_want.txt",			# Birthday list template
				"templateGalleryIndex.txt",			# The index of a gallery
				"templateGalleryIndexEntry.txt",	# An entry in the index
				"templateGalleryLarge.txt",			# The large picture page
				"tempalte.txt",						# Overall template
				"tempalteFeed.txt",					# Template RSS Feed
				"tempalteFeedEntry.txt",			# Template RSS Feed entry
				"sitemaker.py",						# SiteMaker
				"sitemaker.pyc"]					# SiteMaker - Complied

# specialDirectories is a list of directories that we ignore
# Note: hidden directories (those starting with a ".") are ignored

specialDirectories = ["manual"]		# Part of OS X's "Sites" folder

# asciiExtentions is a list of those that signify an ASCII file

asciiExtentions = [	".py",		# Python script
					".htm",		# HTML file
					".html",
					".c",		# C source
					".cpp",		# C++ Source
					".h",		# Header
					".m",		# Objective-C
					".java",	# Java
					".xml",		# XML File
					".txt"]		# Text document

# The template dictionary that holds templates as strings.
# The template date dictionary holds template modificationd dates
# Note: they are put in as keys as "type_name"

templateDict = {}
templateDateDict = {}

# File count and dir count are used to guess at how close we are to done

fileProcessCount = 0
fileUpdateCount = 0

# These next to tell us how many files we have that were checked for update,
#	and how many were actually sent.

updateChecked = 0
updatePerformed = 0

# A dictionary holding the kinds of sections we understand and their objects

sectionObjects = {}

