#qpy:api
PROXY = {}
#qpy:api
PROXY = {}
#qpy:api
PROXY = {}
from datetime import datetime
startTime = datetime.now()

import sys
import subprocess
import glob
import string

try:
	import csv
except:
	pass

#Change this to your PDF Reports folder
pdf_search_dir = "/cygdrive/c/Users/levtim/Dropbox/CollegeReadiness/Reports"

#Tries to open a file from command line arguments
pdffile = "".join(sys.argv[1:])
pdffile = '/home/levtim/Desktop/all_skillstutor_data.pdf'
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

#opens the txt file converted from pdf file
with open(pdffile,'r') as txtfile:
	document = txtfile.readlines()

htmlfiles = glob.glob(pdffile[:-4]+"*.html")
txtfiles = glob.glob(pdffile[:-4]+"*.txt")
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

def is_valid_score(timestamp_pos):
	if ("Pretest" in lesson or "pretest" in lesson or int(score) >= 70):
		return True
	else:
		return False

totalproxyhours = 0.0
dataresultslist = [["Date","Username","Student Name", "Subject","Section","Lesson", "Score","Percent","Time Spent"]]
proxyhourreport = [["Username","Student Name","Proxy Hours"]]
possibletitles = ["Beginning Language Arts","Beginning Math","Language Arts A","Language Arts B","Language Arts C","Reading Comprehension LL","Reading Comprehension A","Reading Comprehension B","Reading Comprehension C","Reading Vocabulary A","Reading Vocabulary B","Reading Vocabulary C","Reading","Writing","Language","Math A","Math B","Math C","Basic Mathematics","Intermediate Mathematics","Algebra","Algebra II (updated)","Algebra II","Science I","Science II","Information Skills","Workforce Readiness Skills"]
def gatherdata(page):
	global totalproxyhours
	validactivities = []
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
	enu = [num for num in enu if ":" in num[1] and num[1].count("-") == 2 and ("AM" in num[1] or "PM" in num[1])] #finds all timestamps, looking for "-" "-" and ":" surrounded by numbers
	#validenu = [num for num in enu if ("Pretest" in page[num[0]-2] or "pretest" in page[num[0]-2] or int(page[num[0]+1]) >= 70)] #includes only scores that are pretests or have a score greater than 70
	activities = []
	#this finds the section the lesson is in so as not to eliminate duplicate lesson names found in different sections/classses
	for pos, timestamp in enu: #for every timestamp index and every timestamp
		date = page[pos][:page[pos].index(" ")]
		time = page[pos][page[pos].index(" "):]
		score = page[pos +1]
		lesson = page[pos -1]
		if score != "Incomplete":
			percent = page[pos + 2]
			timespent = page[pos + 3]
		else:
			 percent = "Incomplete"
			 timespent = ""
		if page[pos-1].isdigit() or page[pos-1] == "Incomplete": #if item before timestamp is a number, PDF is broken
			print "item before timestamp is a number or Incomplete. Fixing ..."
			print page[pos-1:pos+5]
			lesson = page[pos+3]
			timespent = page[pos+4]
		if page[pos+1] != "Incomplete" and not page[pos+3].isdigit():
			print "There is a lesson in the percent column. Fixing ..."
			print page[pos+3]
			lesson = page[pos+3]
			timespent = page[pos+4]
		title = ""
		gobackindex = 0
		test_title = False
		while not test_title:
			try_line = [pos - gobackindex, page[pos - gobackindex]]
			try_line_pos = try_line[0]
			try_line_string = try_line[1]
			if hasletters(try_line_string) and hasletters(page[try_line_pos+1]) and hasletters(page[try_line_pos+2]) and ("AM" in page[try_line_pos+3] or "PM" in page[try_line_pos+3]) and ("/" in page[try_line_pos+4] or "Incomplete" in page[try_line_pos+4]) and "AM" not in try_line_string and "PM" not in try_line_string and "Incomplete" not in try_line_string and try_line_string in possibletitles:
				title = try_line_string
				test_title = True
			gobackindex += 1
		section = ""
		gobackindex = 0 #go back until you find text that != "Incomplete' and doesn't have AM or PM in the next line
		while "AM" in section or "PM" in section or "AM" in page[pos-gobackindex+1] or "PM" in page[pos-gobackindex+1] or "AM" in page[pos-gobackindex-1] or "PM" in page[pos-gobackindex-1] or "/" in page[pos-gobackindex-1] or "/" in section or "Incomplete" in section or len(set(section) & set(string.letters))==0 or "%" in section or "(min" in section or ("Time" == section and "(min" == page[pos-gobackindex+1]) or ("Score" == section and "Time" == page[pos-gobackindex+1]): #keep going until none of these are in the section
			gobackindex += 1
			section = page[pos-gobackindex]
		activity_and_section = str(title) + " : " + str(section) + " : " + str(lesson)
		def is_valid_score(timestamp_pos):
			if percent != "Incomplete" and ("Pretest" in lesson or "pretest" in lesson or int(percent) >= 70):
				return True
			else:
				return False
		if is_valid_score(pos):
			validactivities.append(activity_and_section)
		dataresultslist.append([date.replace("-","/")+time,findusername(page),findstudentname(page),title, section, lesson,str('"'+score+'"'), percent,timespent])
	proxyhours = len(set(validactivities)) * 0.5
	#print "Proxy hours: " + str(proxyhours)
	if proxyhours > 0.0:
		proxyhourreport.append([findusername(page),findstudentname(page), str(proxyhours)])
	totalproxyhours += proxyhours

for page in allpages:
	gatherdata(page)

print "\n\n"
#print proxy hours report
with open(str(pdffile[:-4] + "_log" + ".csv"), 'wb') as csvfile: #writes the output from above to a csv file with the same stem name as pdf file
	resultswriter = csv.writer(csvfile, dialect='excel')
	for row in proxyhourreport:
		print "\t".join(row)
		resultswriter.writerow(row)

print "Written to:",str(pdffile[:-4] + "_log" + ".csv")
print "Total Proxy Hours for",pdffile[:-4],":", totalproxyhours

print "\n\n"
#print all data
try:
	with open(str(pdffile[:-4] + "_alldata_log" + ".csv"), 'wb') as csvfile: #writes the output from above to a csv file with the same stem name as pdf file
		resultswriter = csv.writer(csvfile, dialect='excel')
		for row in dataresultslist:
			resultswriter.writerow(row)
	print "Written to:",str(pdffile[:-4] + "_alldata_log" + ".csv")
except:
	with open(str(pdffile[:-4] + "_alldata_log" + ".txt"), 'w') as txtfile:
		txtfile.write(str(dataresultslist))

print "This shows all data including Incomplete and retakes to gather Usage Data\n\n"



print "Running time for script:",str(datetime.now() - startTime)
