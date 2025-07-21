#!/usr/bin/env python3
"""
Test script to run multiple simulations and see the stats output
"""

from models.seir_model import AuroraFluSimulation

def main():
    print("Running Multiple Aurora Flu Simulations...")
    print("=" * 50)
    
    # Create simulation
    sim = AuroraFluSimulation(
        population=15000,
        initial_infected=1,
        transmission_rate=0.01,
        infectious_period=3,
        simulation_days=14,
        incubation_period=2,
        vaccination_rate=0.1,
        mask_effectiveness=0.0,
        social_distancing=0.0,
        mortality_rate=0.0002,
        vaccination_strategy='single_dose_first',
        vaccine_supply_per_day=500,
        vaccine_delay_days=7,
        mask_compliance=0.0
    )

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
    print("Now calling calculate_statistics() to see the print(stats) output:")
    print("=" * 50)
    
    # This will trigger the print(stats) statement
    stats = sim.calculate_statistics([result])
    
    print("=" * 50)
    print("Statistics calculation completed!")
    #print(stats)

if __name__ == "__main__":
    main() 