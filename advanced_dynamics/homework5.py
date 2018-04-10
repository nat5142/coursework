################################################################################
# homework5.py - Created 2017/12/07											   #
# 	Meteo 422 - Advanced Dynamics | Dr. David Stensrud						   #
#																			   #
# Author: Nicholas Tulli													   #
#																			   #
# This program generates plots of wind profiles over various regimes.		   #
################################################################################

# ------ Module Library ------- #
import numpy as np
import matplotlib.pyplot as plt
# ----------------------------- #

vanKarman = 0.4

'''
	Define function to calculate friction velocity from mean wind speed equation
		- Should return a single float value specific to certain regime
		- Function should accept unique values for:
			- Roughness length (z0)
			- Displacement height (d) --> OPTIONAL
			- Height of given mean wind speed (so that function applies to both 
				protected and unprotected regimes)
		- Function must incorporate global variable for von Karman's constant (k)
'''
def frictionVelocity(roughness, **kwargs):
	displacement = kwargs.get('displacement', 0)
	height = kwargs.get('height', 50)
	windSpeed = kwargs.get('windSpeed', 10)
	u_star = (windSpeed * vanKarman) / np.log((height - displacement) / roughness)
	print u_star
	return u_star

unprotectedGrassFriction = frictionVelocity(0.05, height=50)
unprotectedHedgeFriction = frictionVelocity(0.875, height=50, displacement=5.25)
longGrassHeights = np.arange(0, 50, 0.01)
unprotectedHedgeHeights = np.arange(7.0, 50, 0.01)

def windProfile(roughness, frictionVelocity, height, **kwargs):
	displacement = kwargs.get('displacement', 0)
	speed = (frictionVelocity / vanKarman) * np.log((height - displacement) / roughness)
	return speed

longGrassWindProfile = [windProfile(0.05, unprotectedGrassFriction, z) for z in longGrassHeights]
longGrass = zip(longGrassHeights, longGrassWindProfile)
longGrass = [i for i in longGrass if i[1] > 0]

unprotectedHedgeProfile = [windProfile(0.875, unprotectedHedgeFriction, 
							z, displacement=5.25) for z in unprotectedHedgeHeights]

protectedHedgeFriction = frictionVelocity(0.1, height=7, windSpeed=unprotectedHedgeProfile[0])
protectedHedgeHeights = np.arange(0, 7.0, 0.01)

protectedHedgeProfile = [windProfile(0.1, protectedHedgeFriction, z) for z in protectedHedgeHeights]
protectedHedge = zip(protectedHedgeHeights, protectedHedgeProfile)
protectedHedge = [i for i in protectedHedge if i[1] > 0]


plt.figure(figsize=(10,6))
plt.hold(True)
plt.plot(unprotectedHedgeProfile, unprotectedHedgeHeights, 
		'k-', label='Unprotected Hedge Profile')
plt.plot([i[1] for i in longGrass], [i[0] for i in longGrass], 
		'r-', label='Unprotected Profile (40 cm grass)')
plt.plot([i[1] for i in protectedHedge], [i[0] for i in protectedHedge], 
		'k--', label='Protected Hedge Profile')
plt.axhline(y=2, color='b', linestyle='--', label='2 meters')
plt.axhline(y=7, color='g', linestyle='--', label='7 meters')
plt.title('Log-Wind Profile Over Two Regimes')
plt.xlabel('Mean Wind Speed (m/s)')
plt.ylabel('Altitude (m)')
plt.legend(loc='best')
plt.grid(True)
plt.savefig('windprofiles.png')
plt.show()
plt.close()

print "Unprotected Long Grass Friction Velocity: " + str(unprotectedGrassFriction)
print "Unprotected Hedge Friction Velocity: " + str(unprotectedHedgeFriction)
print "Protected Hedge Friction Velocity: " + str(protectedHedgeFriction)





























