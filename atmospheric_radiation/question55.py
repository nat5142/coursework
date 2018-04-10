################################################################################
# question55.py - Created 2017/12/04										   #
# 	Meteo 436 - Atmospheric Radiation | Dr. Eugene Clothiaux				   #
#																			   #
# Author: Nicholas Tulli													   #
#																			   #
# This program calculates the radiances for a range of viewing angles as 	   #
# instructed in a homework assignment for Meteo 436. An image of the question  #
# can be found in file 'problem55.JPG' for reference.						   #
#																			   #
################################################################################




# ------------------------ MODULE LIBRARY ------------------------ #
import numpy as np
import matplotlib.pyplot as plt
import json
# ---------------------------------------------------------------- #

# ----------------------- GLOBAL VARIABLES ----------------------- #
alpha = 26.39
gamma1 = 0.89936816 # 51.53 degrees expressed as radians
h = 6.626 * float(10**(-34)) # Planck constant
kb = 1.38 * float(10**(-23)) # Boltzmann constant [m^2 kg / s^2 K]
c = 3.0 * float(10**8) # speed of light
Ts = 5975.0 # Temperature of the Sun [K]
N = 2.46 * float(10**25) # number concentration [1 / m^3]
omegaSun = 6.08 * float(10**-5)
scaleHeight = 8000.0 # [m]
# ---------------------------------------------------------------- #

wavelengths = [
	{'wavelength': 0.45, 'color': 'b-', 'radiances': []},
	{'wavelength': 0.55, 'color': 'g-', 'radiances': []},
	{'wavelength': 0.65, 'color': 'r-', 'radiances': []}
]


'''
	Create function to calculate the value of the scattering phase function.

	Accepts:
		- viewZenith: a value from 0 - 90 representing the view zenith angle. 
					  This value should be passed in as an argument from the
					  overall radiance calculating function.

	Global variables used:
		- alpha: a float value representing the difference between due South
			     (180 deg) and the solar azimuth angle (206.39 deg).
		- gamma1: a float value representing the difference between the solar
				   zenith angle and the zenith angle directly overhead (90 deg)
'''
def scatteringPhaseFunction(viewZenith):
	#cosine = (np.sin(gamma1) * np.sin(viewZenith * (np.pi / 180.0))) + \
	#	(np.cos(gamma1) * np.cos(viewZenith * (np.pi / 180.0)) * \
	#		np.cos(alpha * (np.pi / 180.0)))
	t = np.arccos((-np.sin(gamma1) * np.sin(alpha) * \
		np.sin(viewZenith * (np.pi / 180.0))) + (np.cos(gamma1) * \
			np.cos(alpha * (np.pi / 180.0))))
	scatteringPhase = (3.0 / 4.0) * (1.0 + (np.cos(t))**2)
	#scatteringPhase = (3.0 / 4.0) * (1.0 + (cosine ** 2))
	return scatteringPhase

'''
	Define Planck Function.

	Accepts:
		wavelength: a wavelength for incoming radiation in MICROMETERS. Make
					sure to first convert this value to meters.

	Returns:
		radiance: a value for the radiance corresponding to a globally-declared
			temperature.
'''
def PlanckFunction(wavelength):
	wavelengthMeters = wavelength * float(10 ** -6)
	radiance = ((2.0 * h * (c**2)) / (wavelengthMeters ** 5)) * \
		(1.0 / (np.exp((h * c) / (wavelengthMeters * kb * Ts)) - 1.0))
	return radiance

'''
	Define function to calculate scattering coefficient (Beta)

	Accepts:
		- wavelength: a wavelength, in MICROMETERS, from wavelengths dict.

	Returns:
		- beta: a value of the scattering coefficient for a given wavelength.
'''
def scatteringCoeff(wavelength):
	sigma = (4.0 * float(10**-32)) / ((wavelength) ** 4)
	b = sigma * N
	return b


def makePlot(wavelengthDict):
	plt.figure(figsize=(12,6))
	for wave in wavelengthDict:
		plt.plot([x['theta'] for x in wave['radiances']],
			[y['radianceSum'] for y in wave['radiances']],
			wave['color'],
			label=str(wave['wavelength']) + ' micrometers')
	plt.grid(True)
	plt.title('Observed Radiances at 3 Wavelengths')
	plt.xlabel('View Zenith Angle (Degrees)')
	plt.ylabel('Radiance to Observer (W m^-2 sr^-1 um^-1)')
	plt.legend(loc='best')
	#plt.savefig('plotQ55.png')
	plt.show()
	plt.close()


for w in wavelengths:
	w['beta'] = scatteringCoeff(w['wavelength'])
	w['sunRadiance'] = PlanckFunction(w['wavelength'])
	betaTerm = (w['beta']) / (4.0 * np.pi)
	for theta in range(91):
		radianceVals = []
		scattering = scatteringPhaseFunction(theta)
		for i in np.arange(1,1000000,1):
			z = np.cos(float(theta) * (np.pi / 180.0)) * float(i)
			if z >= scaleHeight:
				break
			sunToPathTrans = np.exp(-((scaleHeight - z) * w['beta']) / np.cos(gamma1))
			pathTrans = np.exp(-(float(i - 1) * w['beta']))
			radianceVals.append(betaTerm * w['sunRadiance'] * sunToPathTrans * \
				scattering * omegaSun * pathTrans)
		w['radiances'].append(
			{
				'theta': theta,
				'radianceSum': sum([(r / (10 ** 6)) for r in radianceVals])
			}
		)


makePlot(wavelengths)










































