from json import *
from math import *
import sys

# Open file to read:

if len(sys.argv) < 2:
    print("Not enough arguments given. Terminating.\n")
    sys.exit(0)

f = None
try:
    f = open(sys.argv[1], 'r')
except:
    print("File could not be opened. Terminating.\n")
    #sys.exit(0)

json = loads(f.read())

# Universal constants:

PI = pi
R_GAS = 8.314
PA_O_PSI = 6895

# Get the set of required statistics about the rocket. All values should be given in SI units:

gamma = json["gamma"] if "gamma" in json else 1.2
t_chamber = json["t_chamber"] if "t_chamber" in json else 2500 # Hot APCP
p_chamber = 101300*json["p_chamber"] if "p_chamber" in json else 101300*20 # 20 atm

p_atmosphere = json["p_atmosphere"] if "p_atmosphere" in json else 101300 # STP

p_surface_area = json["p_surface_area"] if "p_surface_area" in json else 1
p_density = json["p_density"] if "p_density" in json else 1750 # Good approximate value
br_exp = json["br_exp"] if "br_exp" in json else 0.48
br_coeff = json["br_coeff"] if "br_coeff" in json else 0.0005 / pow(6895, br_exp)
mol_weight = json["mol_weight"] if "mol_weight" in json else .02 # TODO -- find actual APCP number.

hangle_nozzle_c = json["hangle_nozzle_c"] if "hangle_nozzle_c" in json else 0.5236 # 30 degrees
hangle_nozzle_d = json["hangle_nozzle_d"] if "hangle_nozzle_d" in json else 0.2618 # 15 degrees

l_nozzle_throat = json["l_nozzle_throat"] if "l_nozzle_throat" in json else -1 # Marking for later calculation

r_chamber = json["d_chamber"] if "d_chamber" in json else .009525 # 0.375 inch

# Calculate characteristics:

p_flow = br_coeff * p_surface_area * pow(p_chamber, br_exp) * p_density

t_throat = t_chamber / (1+(gamma-1)/2)
p_throat = p_chamber * pow(1+(gamma-1)/2, -gamma/(gamma-1))

a_throat = p_flow * sqrt((R_GAS*t_throat) / (mol_weight * gamma)) / p_throat
r_throat = sqrt(a_throat / PI)
d_throat = 2 * r_throat
if l_nozzle_throat == -1: # Recalculate l_nozzle_throat to be the radius the of throat.
    l_nozzle_throat = r_throat
d_bore = 2 * d_throat

n_mach = sqrt((2 / (gamma-1)) * (pow(p_chamber / p_atmosphere, (gamma-1)/gamma) - 1))
a_nozzle_exit = (a_throat / n_mach) * pow(2*(1+pow(n_mach, 2)*((gamma-1)/2))/(gamma+1), (gamma+1)/(2*gamma-2))
d_nozzle_exit = 2 * sqrt(a_nozzle_exit / PI)

cosine_eff = (1+cos(hangle_nozzle_d)) / 2

ve_max = sqrt((2*gamma/(gamma-1))*(R_GAS*t_chamber/mol_weight)*(1-pow(p_atmosphere/p_chamber, (gamma-1)/gamma)))*cosine_eff

nozzle_length = (r_chamber-r_throat) / tan(hangle_nozzle_c) + l_nozzle_throat + (sqrt(a_nozzle_exit / PI)-r_throat) / tan(hangle_nozzle_d)
bulkhead_force = p_chamber * pow(r_chamber, 2) * PI

thrust = ve_max * p_flow # Assuming no pressure thrust

# Convert numbers to formatted strings:

p_flow_s = str(round(p_flow, 2)) + ' kg/s' if p_flow > 1 else str(round(1000*p_flow, 1)) + ' g/s'
d_bore_s = str(round(d_bore, 2)) + ' m' if d_bore > 1 else str(round(100 * d_bore, 2)) + ' cm'

n_mach_s = str(round(n_mach, 3))
ratio_expansion_s = str(round(a_nozzle_exit / a_throat, 3))
cos_loss_s = str(round(100*(1-cosine_eff), 2)) + '%'
ve_max_s = str(round(ve_max)) + ' m/s'
isp_max_s = str(round(ve_max / 9.81)) + ' s'
thrust_s = str(round(thrust)) + ' N' if thrust < 1000 else str(round(thrust/1000, 2)) + ' kN' if thrust < 10000 else str(round(thrust/1000, 1)) + ' kN'

t_throat_s = str(round(t_throat)) + ' K'
p_throat_s = str(round(p_throat/101300,1)) + ' atm'
a_throat_s = str(round(a_throat, 3)) + ' m^2' if a_throat > .01 else str(round(10000 * a_throat, 3)) + ' cm^2'
d_throat_s = str(round(d_throat, 2)) + ' m' if d_throat > 1 else str(round(100 * d_throat, 2)) + ' cm'
a_nozzle_exit_s = str(round(a_nozzle_exit, 3)) + ' m^2' if a_nozzle_exit > .01 else str(round(10000 * a_nozzle_exit, 3)) + ' cm^2'
d_nozzle_exit_s = str(round(d_nozzle_exit, 2)) + ' m' if d_nozzle_exit > 1 else str(round(100 * d_nozzle_exit, 2)) + ' cm'
nozzle_length_s = str(round(nozzle_length, 2)) + ' m' if nozzle_length > 1 else str(round(100 * nozzle_length, 2)) + ' cm'
bulkhead_force_s = str(round(bulkhead_force)) + ' N' if bulkhead_force < 1000 else str(round(bulkhead_force/1000, 2)) + ' kN' if bulkhead_force < 10000 else str(round(bulkhead_force/1000, 1)) + ' kN'

# Log results:

filename = sys.argv[1][:sys.argv[1].rfind('.')] + '.log'
output = open(filename, 'w')

output.write('---------- Propellant characteristics ----------\n')
output.write('Propellant flow rate: ' + p_flow_s + '\n')
output.write('Suggested minimum bore diameter (to avoid erosive burn): ' + d_bore_s + '\n')

output.write('---------- Theoretical characteristics ----------\n')
output.write('Mach number: ' + n_mach_s + '\n')
output.write('Expansion ratio: ' + ratio_expansion_s + '\n')
output.write('Cosine losses: ' + cos_loss_s + '\n')
output.write('Maximum achievable exhaust velocity: ' + ve_max_s + '\n')
output.write('Maximum achievable specific impulse: ' + isp_max_s + '\n')
output.write('Thrust: ' + thrust_s + '\n')

output.write('---------- Nozzle & Bulkhead characteristics ----------\n')
output.write('Throat temperature: ' + t_throat_s + '\n')
output.write('Throat pressure: ' + p_throat_s + '\n')
output.write('Throat area: ' + a_throat_s + '\n')
output.write('Throat diameter: ' + d_throat_s + '\n')
output.write('Nozzle exit area: ' + a_nozzle_exit_s + '\n')
output.write('Nozzle exit diameter: ' + d_nozzle_exit_s + '\n')
output.write('Nozzle length: ' + nozzle_length_s + '\n')
output.write('Bulkhead ejection force: ' + bulkhead_force_s + '\n')

output.flush()
output.close()