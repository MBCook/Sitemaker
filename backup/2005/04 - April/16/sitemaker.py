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

from sitemakerRoutines import *
import os
import glob

global specialNames, templateHTML, templateEntry, templateBody

def main():
	"""The main program!"""

	printAtDepth(0, "Initializing globals.")
	
	initializeGlobals()

	printAtDepth(0, "Beginning processing.")
	
	processDirectory("/", None, "Michael Cook's Place", 1)

	printAtDepth(0, "Done processing.")

def processDirectory(dir, nav, title, depth):
	"""Process the given directory and all subdirectories."""

	global specialNames, templateHTML, templateEntry, templateBody

	printAtDepth(depth, "Starting on directory '" + dir + "'.")

	tempDir = os.path.basename(dir)

	if tempDir == "":
		tempDir = "home"

	if nav == None:
		newNav = makeNavigationHTML()
		nav = "<!-- " + tempDir + " -->"
	else:
		newNav = nav.replace("<!-- " + tempDir + " -->", makeNavigationHTML())

	# Do the work for this directory

	dirType = getDirType().strip()

	if dirType == "blog":
		printAtDepth(depth + 1, "This is a blog directory. Writing blog file.")
		content = getBlogContent(templateEntry, specialNames)
		writeFile(newNav, content, title, "index.html", templateHTML)
	elif dirType == "normal":
		printAtDepth(depth + 1, "This is a normal directory. Processing files...")
		contentFiles = glob.glob("*.txt")
		for filename in contentFiles:
			if isSpecialFile(filename, specialNames):
				continue
			else:
				printAtDepth(depth + 1, "  " + filename + "...")
				newFilename = filename.replace(".txt", ".html")
				content, title = getNormalContent(filename, templateBody)
				writeFile(newNav, content, title, newFilename, templateHTML)
		printAtDepth(depth + 1, "  ...Done!")
	else:
		raise NameError, "Unknown type encountered, " + dirType + "."

	# Now process subdirectories

	sectionsList = getSectionsList()

	if sectionsList == []:
		printAtDepth(depth + 1, "No subsections. Returning.")
		return

	printAtDepth(depth + 1, "Beginning to process subsections...")

	for title, section in sectionsList:
		if section == "home":
			continue
		else:
			subdirName = os.path.join(dir, section)
			subsecNav = makeNavigationHTML(section, dir)
			tempNav = nav.replace("<!-- " + tempDir + " -->", subsecNav)
			os.chdir(section)
			processDirectory(subdirName, tempNav, title, depth + 2)
			os.chdir("..")

	printAtDepth(depth + 1, "Done processing subsections. Returning.")

def initializeGlobals():
	"""Initialize the global variables."""

	global specialNames, templateHTML, templateEntry, templateBody

	specialNames = ["sections.txt", "template.txt",
					"style.txt", "templateEntry.txt",
					"templateBody.txt"]

	templateFile = open("template.txt", "r")
	templateHTML = templateFile.read()
	templateFile.close()

	templateFile = open("templateEntry.txt", "r")
	templateEntry = templateFile.read()
	templateFile.close()

	templateFile = open("templateBody.txt", "r")
	templateBody = templateFile.read()
	templateFile.close()

# This code runs the program

if __name__ == "__main__":
	main()

