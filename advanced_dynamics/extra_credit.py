################################################################################
# extra_credit.py - Created 2017/11/28										   #
# 	Meteo 422 - Advanced Dynamics | Dr. David Stensrud						   #
#																			   #
# Author: Nicholas Tulli (nat5142 [at] psu [dot] edu)						   #
#																			   #
# This program loads in file `air.mon.mean.nc`, provided as part of course 	   #
# material for Meteo 422. The dataset is read from the file, and mean 		   #
# temperatures for a given latitude and longitude are selected for plotting.   #
#																			   #
# Outputs of this script are files `fulltempData.png`, `limitTempData.png`,    #
# and `trendlineIncluded.png`.												   #
################################################################################

from netCDF4 import Dataset, num2date, date2num
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt

file = Dataset('air.mon.mean.nc')

longitude = file.variables['lon'][:]
latitude = file.variables['lat'][:]
time = file.variables['time'][:]
air = file.variables['air'][:]

dt_time = [dt.date(1800, 1, 1) + dt.timedelta(hours=t) for t in time]

# selected latitude --> 44.25 (latitude[91])
lat = {'value': latitude[91], 'index': 91}
# selected longitude --> 282.25 (longitude[564])
lon = {'value': longitude[564], 'index': 564}

'''
	Define a function to grab only the datetime.date objects from the variable
	'dt_time' for a certain given month.

	Arguments:
		- monthNumber: A numerical representation of the month in a year (i.e. 
					   1 for January, 2 for February, 12 for December)

	Returns:
		- monthlyMeans: A list of dictionaries containing all monthly mean
						temperatures for the specified month, separted by year. 
						Example format below:

				decemberMeans = [
					{'year': 1948, 'temp': 271.23999},
					{'year': 1949, 'temp': 271.28},
					{...},
					{'year': 2016, 'temp': 271.25}
				]
'''
def getMonths(monthNumber):
	monthlyMeans = []
	months = [i for i in dt_time if i.month == monthNumber]
	temps = [air[count][lat['index']][lon['index']] for count, dates in \
		enumerate(dt_time) if dates.month == monthNumber]
	for i in range(len(months)):
		monthlyMeans.append({'year': int(months[i].year), 'temp': temps[i]})
	return monthlyMeans

'''
	Call function getMonths for each month specified in instructions.
'''
decemberMeans = getMonths(12)
januaryMeans = getMonths(1)
februaryMeans = getMonths(2)
marchMeans = getMonths(3)


'''
	Each of the following three lists should assume the following format at
	completion of the program. This includes variables 'allData', 'limitData' 
	and 'pastDecade'. An example format of the first element of 'allData' is 
	shown below:

		allData[0] = {
				'month': 'December',
				'data': [
							{
								'year': 1948,
								'temp': 271.23999,
								'trend': 268.8679,
								'anomaly': 2.37
							},
							{
								'year': 1949,
								'temp': ...,
								'trend': ...,
								'anomaly': ...
							},
							{
								...
							}
					],
				'color': 'k-',
				'trendline': 'k--'
			}
'''
allData = [
	{'month': 'December', 'data': decemberMeans, 'color': 'k-', 'trendline': 'k--'},
	{'month': 'January', 'data': januaryMeans, 'color': 'r-', 'trendline': 'r--'},
	{'month': 'February', 'data': februaryMeans, 'color': 'b-', 'trendline': 'b--'},
	{'month': 'March', 'data': marchMeans, 'color': 'g-', 'trendline': 'g--'}
]

limitData = [
	{'month': 'December', 'data': decemberMeans[0:61], 'color': 'k-', 'trendline': 'k--'},
	{'month': 'January', 'data': januaryMeans[0:61], 'color': 'r-', 'trendline': 'r--'},
	{'month': 'February', 'data': februaryMeans[0:61], 'color': 'b-', 'trendline': 'b--'},
	{'month': 'March', 'data': marchMeans[0:61], 'color': 'g-', 'trendline': 'g--'}
]

pastDecade = [
	{'month': 'December', 'data': decemberMeans[61:], 'color': 'k-', 'trendline': 'k--'},
	{'month': 'January', 'data': januaryMeans[61:], 'color': 'r-', 'trendline': 'r--'},
	{'month': 'February', 'data': februaryMeans[61:], 'color': 'b-', 'trendline': 'b--'},
	{'month': 'March', 'data': marchMeans[61:], 'color': 'g-', 'trendline': 'g--'}
]


'''
	Define function to handle repetitive, repeatable data plotting. This
	function will evaluate the number of different data lists to plot on the 
	same graph, and arrange them accordingly.

	Arguments:
		dictionary_list: A list of data sets to plot concurrently, each 
						 pertaining to a specific month. The dictionary must 
						 take the format of an element shown in variables
						 'allData', 'limitData' and 'pastDecade'. Keys in 
						 each dict must include:

				- 'month': a hard-coded (or datetime converted) string of the 
						   name of the month for which the data applies
				- 'data': a list of dictionaries equivalent to 'decemberMeans', 
						  or another applicable month
				- 'color': a string defining the color and style of the line 
						   to be plotted for the corresponding data
				- 'trendline': a string defining the color and style of the 
							   trendline to be plotted for the corresponding data

	Optional Keyword Arguments (**kwargs):
		'title': A graph title
		'xAxis': An x-axis label
		'yAxis': A y-axis label
		'grid': A boolean to turn grid on or off
		'save': An string to serve as the name of the figure upon save. If not 
				provided, figure should not be saved.

	Returns:
		None
'''
def createPlot(dictionary_list, **kwargs):
	plt.figure(figsize=(10,6))
	plt.hold(True)
	alpha_kwarg = kwargs.get('alpha', None)
	for dataDict in dictionary_list:
		plt.plot([item['year'] for item in dataDict['data']],
			[item['temp'] for item in dataDict['data']], 
			dataDict['color'],
			label=dataDict['month'],
			alpha=alpha_kwarg)

	if alpha_kwarg != None:
		for dataDict in dictionary_list:
			plt.plot([item['year'] for item in dataDict['data']],
				[item['trend'] for item in dataDict['data']],
				dataDict['trendline'])

	grid = kwargs.get('grid', None)
	save = kwargs.get('save', None)
	plt.title(kwargs.get('title', None))
	plt.xlabel(kwargs.get('xAxis', None))
	plt.ylabel(kwargs.get('yAxis', None))
	plt.legend(loc='best')
	if grid != None:
		try:
			plt.grid(grid)
		except:
			plt.grid(False)
			print "Invalid parameter for grid argument."
	if save != None:
		try: 
			plt.savefig(save)
		except:
			print "Invalid string for save parameter."
	plt.show()
	plt.close()

	return


'''
	Create function to determine best-fit line of a dataseries. The function
	will accept raw data and compute an equation for the best-fit line.

	The function should take the following arguments:
		- A list of dictionaries in the following format:
			'data': [
				{'year': 1948, 'temp': 271.23999},
				{'year': 1949, 'temp': 2271.28},
				...,
				{'year': 2016, 'temp': ...}
			]
		- The only argument passed in should be given in a for loop as so:
			for item in allData:
				bestFit(item['data'])

	The function should do the following:
		- Generate a list of all raw 'temp' values stored in list
		- Use this generated list to produce trendline data for list
		- zip trendline values and years
		- create new field in each dictionary in the 'data' list for trendline 
			values
		- store trendline values for each year in original list of dictionaries

	Arguments:
		- rawDataDictList: a list of dictionaries in the format of 
						   'decemberMeans'

	Returns:
		None
'''
def bestFit(rawDataDictList):
	years = [pairing['year'] for pairing in rawDataDictList]
	temps = [pairing['temp'] for pairing in rawDataDictList]
	z = np.polyfit(years, temps, 1)
	p = np.poly1d(z)
	trends = p(years)
	trendZip = zip(years, trends)
	for item in rawDataDictList:
		for pair in trendZip:
			if item['year'] == pair[0]:
				item['trend'] = pair[1]
		item['anomaly'] = item['temp'] - item['trend']
	return


'''
	Define function to calculate mean yearly temperature anomalies and variance
	from our dataset. The function should accept a full list of dictionaries,
	such as the variable 'allData'.

	Accepts:
		- fullDataDictList: see variable 'allData'

	Returns:
		- anomaly_series: The full series of anonmaly values for all data in 
						  dataset.
		- variance: A float variable, representing the variance of the
					'anomaly_series' which is also returned.
'''
def meanAnomaly(fullDataDictList):
	anomaly_series = []
	for count, data in enumerate(fullDataDictList[0]['data']):
		anomalies = []
		for dictionary in fullDataDictList:
			anomalies.append(dictionary['data'][count]['anomaly'])
		anomaly_series.append(
			{'year': data['year'],'meanAnomaly': np.mean(anomalies)}
		)

	variance = np.var([data['meanAnomaly'] for data in anomaly_series])
	return anomaly_series, variance

for item in allData:
	bestFit(item['data'])

for item in limitData:
	bestFit(item['data'])

for item in pastDecade:
	bestFit(item['data'])

fullMeanAnomaly, fullVariance = meanAnomaly(allData)
limitMeanAnomaly, limitVariance = meanAnomaly(limitData)
decadalAnomaly, decadalVariance = meanAnomaly(pastDecade)


createPlot(allData, xAxis='Year', yAxis='Temperature (K)', 
	title='Mean Monthly Temperature from 1948 - Present (' + \
				str(lat['value']) + ' N, ' +  str(lon['value']) + ' W)',
	grid=True, save='fullTempData.png')

createPlot(limitData, xAxis='Year', yAxis='Temperature (K)',
	title='Mean Monthly Temperature from 1948 - 2008 (' +  \
				str(lat['value']) + ' N, ' +  str(lon['value']) + ' W)',
	grid=True, save='limitTempData.png')

createPlot(limitData, xAxis='Year', yAxis='Temperature (K)',
	title='Mean Monthly Temperature from 1948 - 2008 (' +  \
				str(lat['value']) + ' N, ' +  str(lon['value']) + ' W)',
	grid=True, save='trendlineIncluded.png', alpha=0.25)

print "Mean temperature anomaly for each year (Dec, Jan, Feb, Mar; 1948 - 2008): \
			\n" + str(limitMeanAnomaly)

print "Temperature anomaly variance (1948 - 2008): " + str(limitVariance) 

print "Mean temperature anomaly for each year (Dec, Jan, Feb, Mar; 2009 - 2017): \
			\n" + str(decadalAnomaly)

print "Temperature anomaly variance (2009 - 2017): " + str(decadalVariance) 



























