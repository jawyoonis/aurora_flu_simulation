
#!/usr/bin/env python3
"""
Test script to run multiple simulations and see the stats output
Modified to be imported by main.py
"""

from models.seir_model import AuroraFluSimulation
from scenarios_config import MULTIPLE_SIMULATIONS_PARAMS

def run_multiple_simulations_test():
    """Run multiple simulations test and return results"""
    print("Running Multiple Aurora Flu Simulations...")
    print("=" * 50)
    
    # Use centralized simulation parameters
    sim_params = MULTIPLE_SIMULATIONS_PARAMS
    
    # Create simulation with centralized parameters
    sim = AuroraFluSimulation(**sim_params)

    print("Simulation parameters:")
    print(f"Population: {sim.N}")
    print(f"Initial infected: {sim.I0}")
    print(f"Transmission rate: {sim.beta:.4f}")
    print(f"Simulation days: {sim.days}")
    print("=" * 50)
    
    # Run the simulation
    print("Running simulation...")
    result = sim.run_multiple_simulations(num_runs=5)
    
    print("=" * 50)
    print("Simulation completed!")
    print(f"Total infected: {result.get('total_infected', 0)}")
    print(f"Attack rate: {result.get('attack_rate', 0):.2f}%")
    print(f"Peak infected: {result.get('peak_infected', 0)}")
    print(f"Peak day: {result.get('peak_day', 0)}")
    
    print("=" * 50)
    print("Now calling calculate_statistics() to see the stats output:")
    print("=" * 50)
    
    # This will trigger the statistics calculation
    stats = sim.calculate_statistics([result])
    
    print("=" * 50)
    print("Statistics calculation completed!")
    
    return {
        'simulation_result': result,
        'statistics': stats,
        'simulation_parameters': sim.get_parameters()
    }

# if __name__ == "__main__":
#     run_multiple_simulations_test()