#!/usr/bin/env python3
"""
Test script to demonstrate ANOVA analysis for Aurora flu simulation
"""

from models.seir_model import AuroraFluSimulation

def main():
    print("Aurora Flu Simulation - ANOVA Analysis Test")
    print("=" * 60)
    
    # Define intervention groups to compare
    intervention_groups = {
        'No_Interventions': {
            'population': 15000,
            'initial_infected': 1,
            'transmission_rate': 0.01,
            'infectious_period': 7,
            'simulation_days': 14,
            'incubation_period': 2,
            'vaccination_rate': 0.0,
            'mask_effectiveness': 0.0,
            'social_distancing': 0.0,
            'mortality_rate': 0.0002,
            'vaccination_strategy': 'none',
            'vaccine_supply_per_day': 500,
            'vaccine_delay_days': 0,
            'mask_compliance': 0.0
        },
        'Masks_Only': {
            'population': 15000,
            'initial_infected': 1,
            'transmission_rate': 0.01,
            'infectious_period': 7,
            'simulation_days': 14,
            'incubation_period': 2,
            'vaccination_rate': 0.0,
            'mask_effectiveness': 0.6,
            'social_distancing': 0.0,
            'mortality_rate': 0.0002,
            'vaccination_strategy': 'none',
            'vaccine_supply_per_day': 500,
            'vaccine_delay_days': 0,
            'mask_compliance': 0.8
        },
        'Vaccination_Only': {
            'population': 15000,
            'initial_infected': 1,
            'transmission_rate': 0.01,
            'infectious_period': 7,
            'simulation_days': 14,
            'incubation_period': 2,
            'vaccination_rate': 0.7,
            'mask_effectiveness': 0.0,
            'social_distancing': 0.0,
            'mortality_rate': 0.0002,
            'vaccination_strategy': 'single_dose_first',
            'vaccine_supply_per_day': 500,
            'vaccine_delay_days': 0,
            'mask_compliance': 0.0
        },
        'Social_Distancing_Only': {
            'population': 15000,
            'initial_infected': 1,
            'transmission_rate': 0.01,
            'infectious_period': 7,
            'simulation_days': 14,
            'incubation_period': 2,
            'vaccination_rate': 0.0,
            'mask_effectiveness': 0.0,
            'social_distancing': 0.5,
            'mortality_rate': 0.0002,
            'vaccination_strategy': 'none',
            'vaccine_supply_per_day': 500,
            'vaccine_delay_days': 0,
            'mask_compliance': 0.0
        },
        'Combined_Interventions': {
            'population': 15000,
            'initial_infected': 1,
            'transmission_rate': 0.01,
            'infectious_period': 7,
            'simulation_days': 14,
            'incubation_period': 2,
            'vaccination_rate': 0.7,
            'mask_effectiveness': 0.6,
            'social_distancing': 0.3,
            'mortality_rate': 0.0002,
            'vaccination_strategy': 'single_dose_first',
            'vaccine_supply_per_day': 500,
            'vaccine_delay_days': 0,
            'mask_compliance': 0.8
        }
    }
    
    # Create simulation instance
    sim = AuroraFluSimulation()
    
    print("Intervention Groups:")
    for group_name in intervention_groups.keys():
        print(f"  - {group_name}")
    print()
    
    # Perform ANOVA analysis on attack rate
    print("Running ANOVA analysis on attack rate...")
    anova_results = sim.perform_anova_analysis(
        intervention_groups=intervention_groups,
        metric='attack_rate',
        num_runs_per_group=5  # 5 simulation runs per group
    )
    
    print("\n" + "=" * 60)
    print("ANOVA ANALYSIS RESULTS")
    print("=" * 60)
    
    # Print descriptive statistics
    print("\nDESCRIPTIVE STATISTICS:")
    print("-" * 40)
    for group_name, stats in anova_results['descriptive_statistics'].items():
        print(f"{group_name}:")
        print(f"  Mean: {stats['mean']:.2f}%")
        print(f"  Std:  {stats['std']:.2f}")
        print(f"  Min:  {stats['min']:.2f}%")
        print(f"  Max:  {stats['max']:.2f}%")
        print(f"  N:    {stats['n']}")
        print()
    
    # Print ANOVA results
    print("ANOVA RESULTS:")
    print("-" * 40)
    anova = anova_results['anova_results']
    print(f"F-statistic: {anova['f_statistic']:.4f}")
    print(f"p-value: {anova['p_value']:.6f}")
    print(f"Significant: {anova['significant']}")
    print(f"Effect size (η²): {anova['effect_size_eta_squared']:.4f}")
    print(f"Cohen's f: {anova['effect_size_cohens_f']:.4f}")
    
    # Print assumptions
    print("\nASSUMPTIONS:")
    print("-" * 40)
    assumptions = anova_results['assumptions']
    if assumptions['levene_test_p_value'] is not None:
        print(f"Levene's test p-value: {assumptions['levene_test_p_value']:.4f}")
        print(f"Homogeneity of variance: {assumptions['homogeneity_of_variance']}")
    else:
        print("Levene's test: Not available")
    
    # Print interpretation
    print("\nINTERPRETATION:")
    print("-" * 40)
    interpretation = anova_results['interpretation']
    print(f"Significant difference between groups: {interpretation['significant_difference']}")
    print(f"Effect size interpretation: {interpretation['effect_size_interpretation']}")
    print(f"Practical significance: {interpretation['practical_significance']}")
    
    # Print post-hoc results
    print("\nPOST-HOC ANALYSIS (Tukey's HSD):")
    print("-" * 40)
    print(anova_results['post_hoc']['tukey_hsd_summary'])
    
    return anova_results

if __name__ == "__main__":
    results = main() 