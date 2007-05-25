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
import glob

def printAtDepth(depth, string):
    """Put spaces to depth."""

    retVal = ""

    for i in range(depth):
        retVal += "  "

    print retVal + string

def getDirType():
    """Get which type of directory this one is."""

    fileHandle = open("style.txt")
    fileLine = fileHandle.readline()
    fileHandle.close()

    name, value = fileLine.split("-", 1)

    return value.strip()

def writeFile(nav, text, title, file, templateHTML):
    """Write out the file given the information."""

    fileText = templateHTML.replace("###TITLE###", title)
    fileText = fileText.replace("###NAV###", nav)
    fileText = fileText.replace("###BODY###", text)

    fileHandle = open(file, "w")
    fileHandle.write(fileText)
    fileHandle.close()

def getNormalContent(filename, templateBody):
    """Get the content for the filename given."""

    fileHandle = open(filename, "r")
    fileContents = fileHandle.readlines()
    fileHandle.close()

    title = fileContents.pop(0).strip()
    dateString = fileContents.pop(0).strip()

    dateInt = int(dateString)

    year = dateInt / 10000
    dateInt -= year * 10000
    month = dateInt / 100
    dateInt -= month * 100

    dateString = "%i/%i/%i" % (month, dateInt, year)

    text = "\n"
    text = text.join(fileContents)

    entryHTML = templateBody.replace("###DATE###", dateString)
    entryHTML = entryHTML.replace("###TEXT###", text)

    return (entryHTML, title)

def isSpecialFile(filename, specialNames):
    """Check to see if the file is a special file."""

    for special in specialNames:
        if special == filename:
            return True

    return False

def getBlogContent(templateEntry, specialFiles):
    """Get all the blog content in the current directory."""
    
    contentFiles = glob.glob("*.txt")

    contentFiles.sort()
    contentFiles.reverse()

    blogHTML = ""

    for date in contentFiles:
        if isSpecialFile(date, specialFiles):
            continue

        dateText = date.replace(".txt", "")
        dateInt = int(dateText)

        year = dateInt / 10000
        dateInt -= year * 10000
        month = dateInt / 100
        dateInt -= month * 100

        dateString = "%i/%i/%i" % (month, dateInt, year)

        dateFile = open(date, "r")
        dateContents = dateFile.read()
        dateFile.close()

        lines = dateContents.splitlines(True)

        title = lines.pop(0).strip()

        text = "\n"

        text = text.join(lines)

        entryHTML = templateEntry.replace("###TITLE###", title)
        entryHTML = entryHTML.replace("###DATE###", dateString)
        entryHTML = entryHTML.replace("###TEXT###", text)
        blogHTML += entryHTML

    return blogHTML

def prepareOutput():
    """Prepare the output directory."""

    os.removedirs("output")
    os.mkdir("output")

def makeNavigationHTML(subsection = None, dir = ""):
    """Make the navigation HTML."""

    html = "<ul>"

    sections = getSectionsList()

    if sections == []:
        return ""

    for (name, subDir) in sections:
        html += '<li/><a href="'

        if subDir == "home":
            html += dir
        else:
            html += os.path.join(dir, subDir)

        html += '">' + name + '</a><br/>\n'

        if subDir == subsection:
            html += '<!-- ' + subDir + ' -->'

    html += "</ul>"

    return html

def writeNavigationHTML():
    """Write out the HTML for the navigation bar."""

    # Note, we never use this

    html = makeNavigationHTML(subsection)

    filename = "navigation.html"

    navFile = open(filename, "w")
    navFile.write(html)
    navFile.close()

def getSectionsList():
    """Get the list of sections in the site (no subsections)."""

    try:
        sectionFile = open("sections.txt", "r")
        sectionsList = sectionFile.readlines()
        sectionFile.close()
    except:
        return []

    sections = []

    for line in sectionsList:
        line = line.strip()
        dir, name = line.split("-", 1)
        dir = dir.strip()
        name = name.strip()
        sections.append((name, dir))

    sections.sort()

    return sections
