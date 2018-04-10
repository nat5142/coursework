################################################################################
# processStations.py - Created Spring 2017									   #
# 	Meteo 498a - Scientific Database Management | Prof. Chad Bahrmann		   #	
#																			   #
# Author: Nicholas Tulli (nat5142 [at] psu [dot] edu)									   #
#																			   #
# This file will read `stations.txt`, which is a text file containing 		   #
# information for gloabl meteorological observation sites (ASOS), and process  #
# the information within accordingly.										   #
# 																			   #
# File `stations.txt` was authored and is continually maintained by Greg	   #
# Thompson of NCAR. File can be found at:									   #
# 		'http://www.rap.ucar.edu/weather/surface/stations.txt'				   #
#																			   #
# Script written for Python 2.7.7 on Department of Atmospheric Sciences and	   #
# Meteorology servers.														   #
################################################################################

# -------- MODULE LIBRARY -------- #
import re
import mysql.connector
# -------------------------------- #

# establish connection to MySQL server (credentials removed)
cnx = mysql.connector.connect(user='nat5142', password='#########',
							host='#########', database='#########')
# mysql connection cursor
cursor = cnx.cursor(dictionary=True) 

# relative path to file stations.txt
# NOTE: for simplicity, file is provided in PWD in portfolio
filename = '../../meteo498aData/DATA/stations.txt'

# open file and read lines
with open(filename, 'r') as f:
	lines = f.readlines()
f.close()

data = []

elements={}
elements['state']= {'start': 0,  'end': 2}
elements['name']= {'start': 3,  'end': 19}
elements['id']= {'start': 20, 'end': 24}
elements['lat']= {'start': 39, 'end': 45}
elements['lon']= {'start': 47, 'end': 54}
elements['elev']= {'start': 55, 'end': 59}
elements['country']= {'start': 81, 'end': 83}

'''
	Lines matching the 'noDataRE' regular expression will be omitted from
	processing for this assignment, as we were instructed to process U.S.
	stations ONLY.
'''
noDataRE = '^(?:!|\s{4,}|\w{3,}|CD|\w{1}(?:\s|\.)|\n|EL)'

for line in lines:

	parse = {}

	# ignore lines in file matching noDataRE regular expression
	if re.match(noDataRE, line):
		continue

	for key in elements:

		parse[key] = line[elements[key]['start']:elements[key]['end']].strip()

		if re.match('lat|lon', key):
			# 'match' is a regex object including three capturing groups
			# 	capturing group \d{1,3} will obtain the lat/lon degrees
			#	capturing group \d{2} will obtain the lat/lon minutes
			# 	capturing group N|S|E|W will obtain the lat/lon direction
			match = re.search(
					'(\d{3})\s(\d{2})(N|S|E|W)',
					line[elements[key]['start']:elements[key]['end']]
				)

			'''
				Assignment included instructions to convert the 
				latitude/longitude from degrees and minutes to
				decimal degrees. This conversion takes place below.
			'''
			try:
				parse[key] = float(match.group(1)) + (float(match.group(2)) / 60)
				parse[key] = round((parse[key]),2)

				'''
					If the directional capturing group is either South or West, 
					we must multiply decimal degree value by -1
				'''
				if match.group(3) == 'S' or match.group(3) == 'W':
					parse[key]*= -1
			except AttributeError:
				continue
		else:
			if re.match('^\s+$', line[elements[key]['start']:elements[key]['end']]):
				parse[key]=None

	'''
		Some stations in the file do not contain ICAO ID values,
		only white space in columns 20:24 should the computer encounter 
		one of these records, they should be omitted from final database 
		insertion
	'''
	if parse['id'] == None:
		continue
	else:
		data.append(parse)

# a string containing our SQL insert statement
insert_stmt = "INSERT INTO stations(id, name,state, country, lat, lon, elev) VALUES"
insert_stmt += "(%(id)s, %(name)s, %(state)s, %(country)s, %(lat)s, %(lon)s, %(elev)s)"


# for each dictionary in the list 'data':
for dictionary in data:
	cursor.execute(insert_stmt, dictionary)
	print(dictionary)

# close MySQL connection
cnx.close()



