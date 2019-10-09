import argparse
from math import pi, sqrt

from scipy.constants import G, astronomical_unit

from CustomScaler import CustomScaler
from interpolators.rbf import RbfInterpolator
from simulation_list import SimulationList

parser = argparse.ArgumentParser(description="interpolate water retention rate using RBF",
                                 epilog="returns water retention fraction and mass_retention fraction seperated by a newline")
requiredNamed = parser.add_argument_group('required named arguments')
requiredNamed.add_argument("-a", "--alpha", type=float, required=True, help="the impact angle [degrees]")
requiredNamed.add_argument("-v", "--velocity", type=float, required=True,
                           help="the impact velocity [AU/58d]")
requiredNamed.add_argument("-mp", "--projectile-mass", type=float, required=True, help="mass of the projectile [M_⊙]")
requiredNamed.add_argument("-mt", "--target-mass", type=float, help="mass of the projectile [M_⊙]")

# Massen in Sonnenmassen
# gaussche Gravitationskonstante
# geschwindigkeiten in au/58d
# radius aus der Masse
# Winkel in Grad
# beide Massen statt gamma

args = parser.parse_args()
# print(args)

solar_mass = 1.98847542e+30  # kg
ice_density = 0.9167 / 1000 * 100 ** 3  # TODO: check real numbers
basalt_density = 3 / 1000 * 100 ** 3
water_fraction = 0.15

alpha = args.alpha

target_water_fraction = water_fraction
projectile_water_fraction = water_fraction

projectile_mass_sm = args.projectile_mass
target_mass_sm = args.target_mass
projectile_mass = projectile_mass_sm / solar_mass
target_mass = target_mass_sm / solar_mass


def core_radius(total_mass, water_fraction, density):
    core_mass = total_mass * (1 - water_fraction)
    return (core_mass / density * 3 / 4 / pi) ** (1 / 3)


def total_radius(total_mass, water_fraction, density, inner_radius):
    mantle_mass = total_mass * water_fraction
    return (mantle_mass / density * 3 / 4 / pi + inner_radius ** 3) ** (1 / 3)


target_core_radius = core_radius(target_mass, target_water_fraction, basalt_density)
target_radius = total_radius(target_mass, target_water_fraction, ice_density, target_core_radius)

projectile_core_radius = core_radius(projectile_mass, projectile_water_fraction, basalt_density)
projectile_radius = total_radius(projectile_mass, projectile_water_fraction, ice_density, projectile_core_radius)

escape_velocity = sqrt(2 * G * (target_mass + projectile_mass) / (target_radius + projectile_radius))

velocity_original = args.velocity

const = 365.256 / (2 * pi)  # ~58.13

velocity_si = velocity_original * astronomical_unit / const / (60 * 60 * 24)
velocity = velocity_si / escape_velocity
gamma = args.projectile_mass_sm / args.target_mass_sm

simulations = SimulationList.jsonlines_load()

scaler = CustomScaler()
scaler.fit(simulations.X)

scaled_data = scaler.transform_data(simulations.X)
water_interpolator = RbfInterpolator(scaled_data, simulations.Y_water)
mass_interpolator = RbfInterpolator(scaled_data, simulations.Y_mass)

testinput = [alpha, velocity, projectile_mass, gamma,
             target_water_fraction, projectile_water_fraction]
scaled_input = list(scaler.transform_parameters(testinput))
water_retention = water_interpolator.interpolate(*scaled_input)
mass_retention = mass_interpolator.interpolate(*scaled_input)

print(water_retention)
print(mass_retention)
