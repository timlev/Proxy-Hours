#qpy:api
PROXY = {}
#qpy:api
PROXY = {}
#qpy:api
PROXY = {}
import sys
import subprocess
import glob
import string
from datetime import datetime
import csv
startTime = datetime.now()
"""
for file in glob(BLAH):
	pdffile = file
	#run rest of script, but rename csv file with new and then run a comparison
"""
#Change this to your PDF Reports folder
#pdf_search_dir = "/cygdrive/c/Users/levtim/Dropbox/CollegeReadiness/Reports"

#Tries to open a file from command line arguments
pdffile = "".join(sys.argv[1:])
if pdffile == "":
	print(subprocess.call(["find", pdf_search_dir,"-iname", "*.pdf"]))
	pdffile = input("Oops, you forgot to add a PDF file.\nEnter the exact location of a PDF file after the command:\n This should start with /cygdrive/c/ and use / instead of \ between folders.\n")
pdfdir = pdffile[0:pdffile.rfind("/")]+"/"
pdffilename = pdffile[pdffile.rfind("/")+1::]
pdfhtml = pdffilename[0:-4] +"s.html"
pdftxt = pdffilename[0:-4] +".txt"
subprocess.call(["pdftohtml", "-q",pdffilename],cwd = pdfdir)
print("Finished PDF to HTML Conversion")
output = subprocess.check_output(["lynx", "--dump",pdfhtml],cwd=pdfdir)
with open(pdfdir+pdftxt,'wb') as txt:
	txt.write(output)
pdffile = str(pdfdir+pdftxt)
print("Finished HTML to TXT Conversion")


#test txt file
#pdffile = './rwservlet (4).txt'


show_valid_lessons = raw_input("Do you want to show the valid activity names?(Y/N and Enter: ")

#opens the txt file converted from pdf file
with open(pdffile,'r') as txtfile:
	document = txtfile.readlines()
htmlfiles = glob.glob(pdfdir+"*.html")
txtfiles = glob.glob(pdfdir+"*.txt")
#removes html and txt files, leaving pdf file
for doc in htmlfiles:
	subprocess.call(["rm",doc])
for doc in txtfiles:
	subprocess.call(["rm",doc])

newdocument = ""
for line in document:
	newdocument += line.replace("   ","")
#print(newdocument)

#Split document by Page 1
newdocument = newdocument.split('Page 1\n')

allpages = []
#Split by newlines and create list of lists of lines
for page in newdocument:
	allpages.append(page.split('\n'))
allpages = allpages[1:-1] #Strips empty first chunk and students with no hours

#print(allpages[0])

def findusername(page):
	username = page[page.index("User Name:")+1]
	return username
def findstudentname(page):
	studentname = page[page.index("Student:")+1]
	return studentname

def hasletters(line):
	if len(set(string.letters) & set(line)) > 0:
		return True
	else:
		return False


totalproxyhours = float(0.0)
writeout = ""

#listoftitles = []
#listofsections = []
#listoflessons = []
#masterlist = [["date","username","studentname","lesson","percent"]]
resultslist = [["Username","Student Name","Proxy Hours"]]
def createscoreindex(page):
	global totalproxyhours
	global writeout
	global listoftitles
	global listofsections
	global listoflessons
	#remove footer and header chunks
	while page.count("(min)") > 1: #if there is more than one page, remove footer and header in between pages
		footerstart = page.index("Average score(%) is for completed activities, excluding pretests and")
		headerend = page.index("(min)", footerstart)+1
		page = page[:footerstart]+ page[headerend:]
	#remove (Average=
	for line in page:
		if "(Average=" in line:
			page.remove(line)
	#print page
	enu = enumerate(page) #enumerates page as reference point
	enu = [num for num in enu if "/" in num[1] and len(set(num[1]) & set(string.letters)) == 0] #finds all scores, looking for "/" surrounded by numbers
	validenu = [num for num in enu if ("Pretest" in page[num[0]-2] or "pretest" in page[num[0]-2] or int(page[num[0]+1]) >= 70)] #includes only scores that are pretests or have a score greater than 70
	activities = []
	#this finds the section the lesson is in so as not to eliminate duplicate lesson names found in different sections/classses
	for pos, score in validenu: #for every valid score index and every valid score /
		date = page[pos -1]
		percent = page[pos +1]
		title = ""
		gobackindex = 0
		test_title = False
		while not test_title:
			try_line = [pos - gobackindex, page[pos - gobackindex]]
			try_line_pos = try_line[0]
			try_line_string = try_line[1]
			if hasletters(try_line_string) and hasletters(page[try_line_pos+1]) and hasletters(page[try_line_pos+2]) and ("AM" in page[try_line_pos+3] or "PM" in page[try_line_pos+3]) and ("/" in page[try_line_pos+4] or "Incomplete" in page[try_line_pos+4]) and "AM" not in try_line_string and "PM" not in try_line_string and "Incomplete" not in try_line_string:
				title = try_line_string
				test_title = True
			gobackindex += 1
		section = ""
		gobackindex = 0 #go back until you find text that != "Incomplete' and doesn't have AM or PM in the next line
		while "AM" in section or "PM" in section or "AM" in page[pos-gobackindex+1] or "PM" in page[pos-gobackindex+1] or "AM" in page[pos-gobackindex-1] or "PM" in page[pos-gobackindex-1] or "/" in page[pos-gobackindex-1] or "/" in section or "Incomplete" in section or len(set(section) & set(string.letters))==0 or "%" in section or "(min" in section or ("Time" == section and "(min" == page[pos-gobackindex+1]) or ("Score" == section and "Time" == page[pos-gobackindex+1]): #keep going until none of these are in the section
			gobackindex += 1
			section = page[pos-gobackindex]
		activity_and_section = str(title) + " : " + str(section) + " : " + str(page[pos-2])
		activities.append(activity_and_section)
		#listoftitles.append(title)
		#listofsections.append(section)
		#listoflessons.append(page[pos-2])
	activities = set(activities) #eliminates retakes of same lesson in same section
	if float(len(activities)) > 0.0:
		print findusername(page), findstudentname(page),"Proxy hours:",float(len(activities)/2.0)
		if show_valid_lessons in ["Yes", "YES", "y","Y"]:
			print activities
		resultslist.append([findusername(page),findstudentname(page),str(float(len(activities)/2.0))])
	totalproxyhours += .5 * float(len(activities))#float(len(activities)/2.0) #adds current user proxy hours to total

for page in allpages:
	createscoreindex(page)
with open(str(pdffile[:-4] + "_log" + ".csv"), 'wb') as csvfile: #writes the output from above to a csv file with the same stem name as pdf file
	resultswriter = csv.writer(csvfile, dialect='excel')
	for row in resultslist:
		resultswriter.writerow(row)

print "Written to:",str(pdffile[:-4] + "_log" + ".csv")
print "Total Proxy Hours for",pdffile[:-4],":", totalproxyhours

print "This version no longer removes pretests and lessons in different sections that share the same name."
"""
print "List of Titles:", listoftitles
print "List of Sections:", listofsections
print "List of Lessons:", listoflessons
"""

print "Time for script:",str(datetime.now() - startTime)
