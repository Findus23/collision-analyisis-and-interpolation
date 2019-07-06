from glob import glob
from os import path

from simulation import Simulation
from simulation_list import SimulationList

simulation_sets = {
    "original": sorted(glob("../data/*")),
    # "first_try": sorted(glob("/media/lukas/d27a6119-721c-4584-983f-598c78432a14/simulations/first_try/results/*")),
    # "new": sorted(glob("/media/lukas/d27a6119-721c-4584-983f-598c78432a14/simulations/results/*"))
    "cloud":sorted(glob("../new_simulations/results/*"))
}
simulations = SimulationList()

for set_type, directories in simulation_sets.items():
    for dir in directories:
        original = set_type == "original"
        spheres_file = dir + "/spheres_ini_log"
        aggregates_file = dir + ("/sim/aggregates.txt" if original else "/aggregates.txt")
        if not path.exists(spheres_file) or not path.exists(aggregates_file):
            print(f"skipping {dir}")
            continue
        if "id" not in dir and original:
            continue
        sim = Simulation()
        if set_type == "original":
            sim.load_params_from_dirname(path.basename(dir))
        else:
            sim.load_params_from_json(dir + "/parameters.json")
        sim.type = set_type
        sim.load_params_from_spheres_ini_log(spheres_file)
        sim.load_params_from_aggregates_txt(aggregates_file)
        sim.assert_all_loaded()
        simulations.append(sim)
        # print(vars(sim))

    print(len(simulations.simlist))

simulations.jsonlines_save()
