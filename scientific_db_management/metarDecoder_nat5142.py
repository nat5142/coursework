################################################################################
# metarDecoder_nat5142.py - Created Spring 2017								   #
# 	Meteo 498a - Scientific Database Management | Prof. Chad Bahrmann		   #	
#																			   #
# Author: Nicholas Tulli (nat5142 [at] psu [dot] edu)						   #
#																			   #
# This program loops through files found in directory specified in variable	   #
# `filepath`, processed data contained in each, and inserts data into MySQL    #
# database. Files are asos-fivemin data files, which were provided to students #
# as part of course material.												   #
#																			   #
# Script written for Python 2.7.7 on Department of Atmospheric Sciences and	   #
# Meteorology servers.														   #
################################################################################

# -------- MODULE LIBRARY -------- #
import os
import re
import mysql.connector
# -------------------------------- #

# establish connection to MySQL server (credentials removed)
cnx = mysql.connector.connect(user='nat5142', password='#########',
							host='#########', database='#########')

# mysql connection cursor
cursor = cnx.cursor(dictionary=True)

# relative path to directory housing numerous METAR record files
filepath = '../../meteo498aData/DATA/asos-fivemin/'

sitenames = "SELECT id, stationID FROM stations WHERE country='US'"
cursor.execute(sitenames)

'''
	Variable 'sites' is a list of dictionaries, each containing keys 'id' and
	'stationID' for US metar sites.

	- Key `id` is an auto-increment field from the `stations` table
	- Key `stationID` is a 4-character ICAO ID corresponding to an
		automated ASOS station in the United States.

'''
sites = cursor.fetchall()


for site in sites:
	files = [f for f in os.listdir(filepath) if re.match("64010"+site['id'], f)]

	'''
		Regular expression library.

		These regular expressions will be used to pull requested data
		from asos-fivemin data files.
	'''
	station_RE = '(?P<siteid>^K\w{3})'
	zdatetime_RE = '\s+(?P<utc_day>[0-2]?[0-9]|3[0-1])(?P<utc_hour>[0-1]?[0-9]|2[0-3])(?P<utc_min>[0-5][0-9])Z'
	# re.compile is used here to convert regular expression patterns into regular expression objects
	wind_RE = re.compile('(?P<wdir>\d{3}|VRB)(?P<wspd>\d{2})(?:KT\s|G)(?:(?P<wgust>\d{2})?KT\s)?')
	temp_RE = re.compile('(?P<temp>M?\d{2})\/(?P<dew>M?\d{2})?$')
	ldatetime_RE = '\w{3}(?P<lyear>\d{4})(?P<lmonth>\d{2})(?P<lday>\d{2})(?P<lhour>\d{2})(?P<lmin>\d{2})'
	# ---------------------------------------------------------------------------------------------------- #
	
	# database insert statement string, to be used at end of upcoming for loop
	insert_stmt = '''
		INSERT INTO metar_screen_trial \
		(stationID, ldatetime, zdatetime, wspd, wdir, wgust, vrb, temp, dew)
		VALUES (%(stationID)s, %(ldatetime)s, %(zdatetime)s, %(wspd)s, \
				%(wdir)s, %(wgust)s, %(vrb)s, %(temp)s, %(dew)s)
	'''

	# for each file in list files:
	for filename in files:
		linerecords = {
				'stationID':site['stationID'],
				'ldatetime':None,
				'zdatetime':None,
				'wspd':None,
				'wdir':None,
				'wgust':None,
				'vrb':None,
				'temp':None,
				'dew':None
			}
		
		# open the file in question
		with open(filepath+filename) as f:
			# create variable 'lines' containing content of file in question
			lines=f.readlines()
		f.close()

		for line in lines:
			zdatetime = re.search(zdatetime_RE, line)
			ldatetime = re.search(ldatetime_RE, line)

			if zdatetime and ldatetime:
				zdt = zdatetime.groupdict()
				ldt = ldatetime.groupdict()

				linerecords['ldatetime'] = str(ldatetime.group(1) + '-' \
					+ ldatetime.group(2) + '-' + ldatetime.group(3) \
					+ ' ' + ldatetime.group(4) + ':' + ldatetime.group(5))

				'''
					Because of the discrepancy between UTC and US local 
					times, and the fashion in which each are printed in 
					metars, we need to ensure that dates and times are 
					accurate within the last 4-7 hours of each month and
					year.
				'''
				if zdt['utc_day'] >= ldt['lday']:
					linerecords['zdatetime'] = str(ldatetime.group(1) + '-' \
						+ ldatetime.group(2) + '-' + zdatetime.group(1) \
						+ ' ' + zdatetime.group(2) + ':' + zdatetime.group(3))

				'''
					If the UTC date is LESS THAN the local date 
					(i.e. 01APR/31MAR), conversions are required
				'''
				else:
					'''
						If the record corresponds to December 31st, 
						the UTC year must be increased by 1, and 
						month must be reset to 01
					'''
					if ldt['lday'] == 31 and ldt['lmonth'] == 12:
						linerecords['zdatetime'] = str((int(ldatetime.group(1))+1) \
							+ '-' + str(01) + '-' + str(01) \
							+ ' ' + zdatetime.group(2) + ':' + zdatetime.group(3))
					'''
						If the record corresponds to the last day of a month 
						that is NOT December 31st, only UTC month must be 
						increased by 1
					'''
					else:
						linerecords['zdatetime'] = str(ldatetime.group(1) + '-' \
							+ str(int(ldatetime.group(2))+1) + '-' + zdt['utc_day'] \
							+ ' ' + zdatetime.group(2) + ':' + zdatetime.group(3))
		
			# split the line in question by white space
			for token in re.split('\s',line):
				temp = temp_RE.match(token)
				if temp:
					temps = temp.groupdict()

					# loop over each key, value pair in dictionary temps
					for k,v in temps.items():
						# if a value exists for the key in question:
						if v:
							'''
								If the two digits representing either 
								temperature or dew point do not contain 
								a leading 'M', no change required
							'''
							if re.match('^\d+', v):
								temps[k] = int(v)

							'''
								In automated METAR observations, a negative
								value for temperature and dewpoint is 
								signified by a leading `M` prior to digits.
								If an M is matched, a conversion to negative
								must be made.
							'''
							if re.match('^M\d+', v):
								temps[k] = -int(v[1:])	
						linerecords.update(temps)
				
				# use the wind regex to match appropriate string in token
				wind = wind_RE.match(token)	
				
				if wind:
					'''
						if VRB appears in wind string, set linerecords['VRB']
						equal to string 'VRB' and linerecords['wdir'] = NULL
					'''
					if wind.group(1) == 'VRB':
						linerecords['vrb'] = wind.group(1)
						linerecords['wdir'] = None

					'''
						If match group does not equal 'VRB', set 
						linerecords['wdir'] equal to integer value 
						in captured group, and make linerecords['VRB'] NULL
					'''
					else:
						linerecords['wdir'] = int(wind.group(1))
						linerecords['vrb'] = None

					linerecords['wspd'] = int(wind.group(2))

					if wind.group(3):
						linerecords['wgust'] = int(wind.group(3))

					'''
						If the third capturing group DOES NOT exist, the wind 
						gust value has been omitted in the metar, which is
						standard practice under steady winds so, make 
						linerecords['wgust'] = NULL
					'''
					else:
						linerecords['wgust'] = None
				
				# use station regular expression to match to token in question
				siteid = re.match(station_RE, token)

				if siteid:
					linerecords['siteid'] = siteid.group(1)
			
			print linerecords
			
			'''
				Try to insert the now-populated 'linerecords' dictionary 
				to the database if a duplicate key is inserted, the 
				dictionary will be omitted from database insertion
			'''
			try:
				cursor.execute(insert_stmt, linerecords)
			except mysql.connector.errors.IntegrityError:		
				pass

			
# close MySQL connection
cnx.close()

