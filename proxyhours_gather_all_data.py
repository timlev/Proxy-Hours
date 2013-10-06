def proxy_hours(filename):
	from datetime import datetime
	startTime = datetime.now()

	from sys import argv
	from subprocess import call, check_output, PIPE
	import glob
	from string import letters
	import os
	from HTMLParser import HTMLParser

	class MLStripper(HTMLParser):
		def __init__(self):
			self.reset()
			self.fed = []
		def handle_data(self, d):
			self.fed.append(d)
		def get_data(self):
			return ''.join(self.fed)

	def strip_tags(html):
		s = MLStripper()
		s.feed(html)
		return s.get_data()
	try:
		from csv import writer
	except:
		pass
	startdir = os.getcwd()
	print startdir
	goback = os.path.abspath(startdir)
	startdir = startdir.replace('\\','/')
	startdir = '"' + startdir + "/"
	print startdir
	#filename = filename.encode('string-escape')
	#pdffilename = os.path.basename(filename)
	pdfdir = os.path.dirname(filename)
	#print pdffilename
	#print pdfdir
	#pdffilename = os.path.abspath(filename)
	pdffilename = filename
	# os.path.abspath(filename)
	#print filename
	#print type(pdffilename)
	os.chdir(pdfdir)
	pdfhtml = pdffilename[0:pdffilename.rindex(".pdf")] +"s.html"
	pdftxt = pdffilename[0:pdffilename.rindex(".pdf")] +".txt"
	csvf = pdffilename[0:pdffilename.rindex(".pdf")] +".csv"
	pdffile = csvf
	#Convert to HTML
	call(startdir + 'pdftohtml.exe"' + ' -q "' + pdffilename +'"',shell=True)

	print("Finished PDF to HTML Conversion")

	#Convert to txt
	with open(pdfhtml,'rb') as ht:
		ht_lines = ht.readlines()
	list_of_lines = [strip_tags(line).strip() for line in ht_lines if strip_tags(line).strip() != ""]

	print("Finished HTML to TXT Conversion")

	#removes html and txt files, leaving pdf file
	pdfhtml1 = pdffilename[0:pdffilename.rindex(".pdf")] +".html"
	pdfhtml2 = pdffilename[0:pdffilename.rindex(".pdf")] +"_ind.html"
	htmlfiles = [pdfhtml, pdfhtml1, pdfhtml2]
	#print htmlfiles
	for doc in htmlfiles:
		os.remove(os.path.abspath(doc))

	newdocument = "\n".join(list_of_lines)
	
	#Split document by Page 1 (each student has only one Page 1)
	newdocument = newdocument.split('Page 1\n')

	allpages = []

	#Split by newlines and create list of lists of lines
	for page in newdocument:
		allpages.append(page.split('\n'))

	#Strips empty first chunk and students with no hours
	allpages = allpages[1:-1]
	#for page in allpages[0:5]:
		#print page
	#TESTING: print(allpages[0])

	def findusername(page):
		username = page[page.index("User Name:")+1]
		return username

	def findstudentname(page):
		studentname = page[page.index("Student:")+1]
		return studentname

	def hasletters(line):
		return any(c.isalpha() for c in line)

	#IMPORTANT Global Variables
	totalproxyhours = 0.0
	dataresultslist = [["Date","Time","Username","Student Name", "Subject","Section","Lesson", "Score","Percent","Time Spent"]]
	proxyhourreport = [["Username","Student Name","Proxy Hours"]]
	logfilelist = []
	#updated 8/20/2013 from myskillstutor.com
	possibletitles = ["Beginning Language Arts","Beginning Math","Language Arts A","Language Arts B","Language Arts C","Reading Comprehension LL","Reading Comprehension A","Reading Comprehension B","Reading Comprehension C","Reading Vocabulary A","Reading Vocabulary B","Reading Vocabulary C","Reading","Writing","Language","Math A","Math B","Math C","Basic Mathematics","Intermediate Mathematics","Algebra","Algebra II (updated)","Algebra II","Science I","Science II","Information Skills","Workforce Readiness Skills"]
	global totalproxyhours, dataresultslist, proxyhourreport, logfilelist, possibletitles
	def gatherdata(page): #Main Function
		global totalproxyhours
		validactivities = []
		
		#remove footer and header chunks
		while page.count("(min)") > 1: #if there is more than one page, remove footer and header in between pages
			footerstart = page.index("Average score(%) is for completed activities, excluding pretests and placement tests.")
			headerend = page.index("(min)", footerstart)+1
			page = page[:footerstart]+ page[headerend:]
		
		#remove (Average=
		page = [line for line in page if "(Average=" not in line]
		
		#TESTING:print page
		enu = enumerate(page) #enumerates page as reference point
		enu = [num for num in enu if ":" in num[1] and num[1].count("-") == 2 and ("AM" in num[1] or "PM" in num[1])] #finds all timestamps, looking for "-" "-" and ":" surrounded by numbers
		activities = []
		
		#Finds the title and section the lesson is in so as not to eliminate duplicate lesson names found in different sections/titles
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
			#Fixing Errors
			if page[pos-1].isdigit() or page[pos-1] == "Incomplete": #if item before timestamp is a number, PDF is broken
				logfilelist.append(str("item before timestamp is a number or Incomplete. Fixing ..."+ str(page[pos-1:pos+5])))
				lesson = page[pos+3]
				timespent = page[pos+4]
			if page[pos+1] != "Incomplete" and not page[pos+3].isdigit():
				logfilelist.append(str("There is a lesson in the percent column. Fixing ..."+str(page[pos+3])))
				lesson = page[pos+3]
				timespent = page[pos+4]
			
			#Finding Title
			title = ""
			gobackindex = 0
			test_title = False
			while not test_title:
				try_line = [pos - gobackindex, page[pos - gobackindex]]
				try_line_pos = try_line[0]
				try_line_string = try_line[1]
				if try_line_string in possibletitles:# and hasletters(try_line_string) and hasletters(page[try_line_pos+1]) and hasletters(page[try_line_pos+2]) and ("AM" in page[try_line_pos+3] or "PM" in page[try_line_pos+3]) and ("/" in page[try_line_pos+4] or "Incomplete" in page[try_line_pos+4]) and "AM" not in try_line_string and "PM" not in try_line_string and "Incomplete" not in try_line_string:
					title = try_line_string
					test_title = True
				gobackindex += 1
			
			#Finding Section
			section = ""
			gobackindex = 0 #go back until you find text that != "Incomplete' and doesn't have AM or PM in the next line
			while "AM" in section or "PM" in section or "AM" in page[pos-gobackindex+1] or "PM" in page[pos-gobackindex+1] or "AM" in page[pos-gobackindex-1] or "PM" in page[pos-gobackindex-1] or "/" in page[pos-gobackindex-1] or "/" in section or "Incomplete" in section or len(set(section) & set(letters))==0 or "%" in section or "(min" in section or ("Time" == section and "(min" == page[pos-gobackindex+1]) or ("Score" == section and "Time" == page[pos-gobackindex+1]): #keep going until none of these are in the section
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
			dataresultslist.append([date,time,findusername(page),findstudentname(page),title, section, lesson,str('"'+score+'"'), percent,timespent])
		
		proxyhours = len(set(validactivities)) * 0.5
		#print "Proxy hours: " + str(proxyhours)
		if proxyhours > 0.0:
			proxyhourreport.append([findusername(page),findstudentname(page), float(proxyhours)])
		totalproxyhours += proxyhours

	#Main Function Executing
	for page in allpages:
		gatherdata(page)

	print "\n\n"
	#FLAG 0
	write_out_0 = [[u,s,'{0: >16}'.format(str(p))] for [u,s,p] in proxyhourreport[1:]]
	
	#print proxy hours report
	with open(str(pdffile[:-4] + "_log" + ".csv"), 'wb') as csvfile: #writes the output from above to a csv file with the same stem name as pdf file
		resultswriter = writer(csvfile, dialect='excel')
		for row in proxyhourreport:
			#print "\t".join(row)
			resultswriter.writerow(row)
	#FLAG 1
	write_out_1 = str(pdffile[:-4] + "_log" + ".csv") + "\tTotal Proxy Hours: " + str(totalproxyhours)
	print "Written to:",str(pdffile[:-4] + "_log" + ".csv")
	print "Total Proxy Hours for",pdffile[:-4],":", totalproxyhours

	print "\n\n"

	#print all data log
	try:
		with open(str(pdffile[:-4] + "_alldata_log" + ".csv"), 'wb') as csvfile: #writes the output from above to a csv file with the same stem name as pdf file
			resultswriter = writer(csvfile, dialect='excel')
			for row in dataresultslist:
				resultswriter.writerow(row)
		#FLAG 2
		write_out_2 = str(pdffile[:-4] + "_alldata_log" + ".csv")
		print "Written to:",str(pdffile[:-4] + "_alldata_log" + ".csv")
	except:
		with open(str(pdffile[:-4] + "_alldata_log" + ".txt"), 'w') as txtfile:
			txtfile.write(str(dataresultslist))

	print "This shows all data including Incomplete and retakes to gather Usage Data\n\n"

	#SQL Database - Determine which activities have not been done before, and then add activities to mega.db and allskillstutordata...csv
	import sys, csv, sqlite3, os

	conn = sqlite3.connect('mega.db')
	curr = conn.cursor()

	#IMPORT NEW CSV ALL LOG to temp table
	try:
		newfile = str(pdffile[:-4] + "_alldata_log" + ".csv")
	except:
		print "USAGE: python st_db.py [csvfilename]"
		quit()
	with open(newfile,'rb') as csvfile:
		f = csv.reader(csvfile,dialect='excel')
		f = [x for x in f]
	data = f[1:]

	headers = "(Date text, Time text, Username text, Student_Name text, Subject text, Section text, Lesson text, Score text, Percent int, Time_Spent int)"
	updates_headers = "(Username text, Student_Name text, Subject text, Section text, Lesson text)"

	try:
		curr.execute("""CREATE TABLE records""" + headers)
		print "No DB Found. Run make_mega_db.py to make the db"
	except:
		pass

	#CREATE temp table and import newfile.csv
	try:
		curr.execute("""DROP TABLE new""")
		curr.execute("""DROP TABLE updates""")
	except:
		pass
	curr.execute("""CREATE TABLE new"""+ headers)
	curr.executemany("""INSERT INTO new VALUES(?,?,?,?,?,?,?,?,?,?)""", data)
	
	#CREATE updates table
	curr.execute("""CREATE TABLE updates"""+updates_headers)
	rel_cols = "Username, Student_Name, Subject, Section, Lesson"
	#CREATE [valids] view
	curr.execute("""CREATE TEMP VIEW [valids] AS SELECT * FROM records WHERE Score <> '"Incomplete"' AND (Percent >= 70 OR Lesson LIKE '%retest%' )""")
	
	#INSERT valid activities from newfile (temp) if not in valids view
	curr.execute("""INSERT INTO updates SELECT """ + rel_cols + """ FROM new WHERE Score <> '"Incomplete"' AND (Percent >= 70 OR Lesson LIKE '%retest%' ) EXCEPT SELECT """ + rel_cols + """ FROM [valids]""")


	#TESTING
	curr.execute("""SELECT * FROM updates""")
	print len(curr.fetchall())
	curr.execute("""SELECT * FROM new WHERE Score <> '"Incomplete"' AND (Percent >= 70 OR Lesson LIKE '%retest%' )""")
	print len(curr.fetchall())
	
	#SELECT Valid Activities Counts
	curr.execute("""SELECT Student_Name, Username, count(DISTINCT Username || Subject || Section || Lesson) FROM updates GROUP BY Username""")
	results = curr.fetchall()
	results = [[row[0],row[1],int(row[2])/2.0] for row in results]
	write_out_0 = [[u,s,'{0: >16}'.format(str(p))] for [u,s,p] in results]
	
	write_out_1 = str(pdffile[:-4] + "_log" + ".csv") + "\tTotal Proxy Hours: " + str(sum([row[2] for row in results]))
	
	write_out_2 = str(pdffile[:-4] + "_alldata_log" + ".csv")
	#PRINT and SAVE data
	for row in results:
		print row
	with open(str(pdffile[:-4] + "_log" + ".csv"),'wb') as ou:
		f = csv.writer(ou)
		f.writerows(results)
	

	#Add contents of newfile to mega.db table records
	curr.executemany("""INSERT INTO records VALUES(?,?,?,?,?,?,?,?,?,?)""", data)

	#Append contents of newfile to alldata.csv
	with open('all_skillstutor_data.csv','a') as a:
		f = csv.writer(a, dialect ='excel')
		f.writerows(data)

	#Append _added to csv file to signify data has been added to mega.db table records
	os.rename(newfile, newfile[:newfile.rindex(".")]+"_added.csv")
	

	#DROP updates
	curr.execute("""DROP TABLE updates""")
	curr.execute("""DROP TABLE new""")
	conn.commit()
	conn.close()
	
	write_out_3 = str(datetime.now() - startTime)
	print "Running time for script:",str(datetime.now() - startTime)
	os.chdir(goback)
	return write_out_0, write_out_1, write_out_2, write_out_3
