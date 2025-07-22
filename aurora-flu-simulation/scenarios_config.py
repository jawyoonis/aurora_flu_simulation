#!/usr/bin/env python3
"""
Centralized scenario configurations for Aurora Flu Simulation
Contains all intervention scenarios used across test files and main analysis
EXACT specifications as provided by user
"""

# Scenario definitions with visualization metadata - EXACT USER SPECIFICATIONS
INTERVENTION_SCENARIOS = {
    'No_Interventions': {
        'name': 'No Interventions',
        'description': 'Run 1 - Baseline scenario with no public health interventions',
        'color': '#FF6B6B',
        'params': {
            'population': 15000,
            'initial_infected': 100,
            'transmission_rate': 0.01,
            'infectious_period': 3,
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
        }
    },
    'Masks_Only': {
        'name': 'Masks Only',
        'description': 'Run 2 - Masks with 70% effectiveness and 70% compliance',
        'color': '#4ECDC4',
        'params': {
            'population': 15000,
            'initial_infected': 200,
            'transmission_rate': 0.01,
            'infectious_period': 3,
            'simulation_days': 14,
            'incubation_period': 2,
            'vaccination_rate': 0.0,
            'mask_effectiveness': 0.7,
            'social_distancing': 0.0,
            'mortality_rate': 0.0002,
            'vaccination_strategy': 'none',
            'vaccine_supply_per_day': 500,
            'vaccine_delay_days': 0,
            'mask_compliance': 0.7
        }
    },
    'Social_Distancing_Only': {
        'name': 'Social Distancing Only',
        'description': 'Run 3 - Social distancing with 70% contact reduction',
        'color': '#45B7D1',
        'params': {
            'population': 15000,
            'initial_infected': 100,
            'transmission_rate': 0.01,
            'infectious_period': 3,
            'simulation_days': 14,
            'incubation_period': 2,
            'vaccination_rate': 0.0,
            'mask_effectiveness': 0.0,
            'social_distancing': 0.7,
            'mortality_rate': 0.0002,
            'vaccination_strategy': 'none',
            'vaccine_supply_per_day': 500,
            'vaccine_delay_days': 0,
            'mask_compliance': 0.0
        }
    },
    'Vaccination_Only': {
        'name': 'Vaccination Only',
        'description': 'Run 4 - Vaccination with 10% rate and 7-day delay',
        'color': '#96CEB4',
        'params': {
            'population': 15000,
            'initial_infected': 100,
            'transmission_rate': 0.01,
            'infectious_period': 3,
            'simulation_days': 14,
            'incubation_period': 2,
            'vaccination_rate': 0.1,
            'mask_effectiveness': 0.0,
            'social_distancing': 0.0,
            'mortality_rate': 0.0002,
            'vaccination_strategy': 'single_dose_first',
            'vaccine_supply_per_day': 500,
            'vaccine_delay_days': 7,
            'mask_compliance': 0.0
        }
    },
    'All_Interventions': {
        'name': 'All Interventions Combined',
        'description': 'Run 5 - All interventions implemented simultaneously',
        'color': '#FFEAA7',
        'params': {
            'population': 15000,
            'initial_infected': 100,
            'transmission_rate': 0.01,
            'infectious_period': 3,
            'simulation_days': 14,
            'incubation_period': 2,
            'vaccination_rate': 0.1,
            'mask_effectiveness': 0.7,
            'social_distancing': 0.7,
            'mortality_rate': 0.0002,
            'vaccination_strategy': 'single_dose_first',  # Note: Changed from 'single_dose' to 'single_dose_first'
            'vaccine_supply_per_day': 500,
            'vaccine_delay_days': 7,
            'mask_compliance': 0.7
        }
    }
}

# Legacy scenario formats for backward compatibility with existing test files

# ANOVA test format (matches test_anova.py)
ANOVA_INTERVENTION_GROUPS = {
    scenario_key: scenario_data['params'] 
    for scenario_key, scenario_data in INTERVENTION_SCENARIOS.items()
}

# Add the Combined_Interventions alias for test_anova.py compatibility
ANOVA_INTERVENTION_GROUPS['Combined_Interventions'] = ANOVA_INTERVENTION_GROUPS['All_Interventions']

# Multiple simulations test format (matches test_multiple_simulations.py)
MULTIPLE_SIMULATIONS_PARAMS = INTERVENTION_SCENARIOS['Vaccination_Only']['params']

# Utility functions
def get_scenario_params(scenario_key):
    """Get parameters for a specific scenario"""
    if scenario_key in INTERVENTION_SCENARIOS:
        return INTERVENTION_SCENARIOS[scenario_key]['params']
    else:
        raise ValueError(f"Unknown scenario: {scenario_key}")

def get_all_scenario_params():
    """Get parameters for all scenarios as dict"""
    return {key: data['params'] for key, data in INTERVENTION_SCENARIOS.items()}

def get_scenario_info(scenario_key):
    """Get full scenario information including metadata"""
    if scenario_key in INTERVENTION_SCENARIOS:
        return INTERVENTION_SCENARIOS[scenario_key]
    else:
        raise ValueError(f"Unknown scenario: {scenario_key}")

def print_scenario_summary():
    """Print summary of all scenarios with EXACT parameter specifications"""
    print("Available Intervention Scenarios - EXACT USER SPECIFICATIONS:")
    print("=" * 70)
    
    run_numbers = ['Run 1', 'Run 2', 'Run 3', 'Run 4', 'Run 5']
    scenario_keys = list(INTERVENTION_SCENARIOS.keys())
    
    for i, (key, scenario) in enumerate(INTERVENTION_SCENARIOS.items()):
        print(f"\n{run_numbers[i]} - {key}:")
        print(f"  Name: {scenario['name']}")
        print(f"  Description: {scenario['description']}")
        
        # Print ALL parameters to verify exact match
        params = scenario['params']
        print(f"  Parameters:")
        for param_name, param_value in params.items():
            print(f"    {param_name}={param_value}")
        
        # Highlight key interventions
        interventions = []
        if params['mask_effectiveness'] > 0:
            interventions.append(f"Masks ({params['mask_effectiveness']*100:.0f}% eff, {params['mask_compliance']*100:.0f}% compliance)")
        if params['social_distancing'] > 0:
            interventions.append(f"Social Distancing ({params['social_distancing']*100:.0f}% reduction)")
        if params['vaccination_rate'] > 0:
            interventions.append(f"Vaccination ({params['vaccination_rate']*100:.0f}% rate, {params['vaccine_delay_days']} day delay, {params['vaccination_strategy']})")
        
        if interventions:
            print(f"  Active Interventions: {', '.join(interventions)}")
        else:
            print(f"  Active Interventions: None (baseline)")

def verify_exact_specifications():
    """Verify scenarios match exact user specifications"""
    print("\n🔍 VERIFICATION - Checking scenarios match exact specifications:")
    print("=" * 70)
    
    expected_specs = [
        # Run 1 - No intervention
        {
            'run': 'Run 1',
            'key': 'No_Interventions',
            'check_params': {
                'vaccination_rate': 0.0,
                'mask_effectiveness': 0.0,
                'social_distancing': 0.0,
                'vaccination_strategy': 'none',
                'mask_compliance': 0.0
            }
        },
        # Run 2 - Masks
        {
            'run': 'Run 2', 
            'key': 'Masks_Only',
            'check_params': {
                'vaccination_rate': 0.0,
                'mask_effectiveness': 0.7,
                'social_distancing': 0.0,
                'vaccination_strategy': 'none',
                'mask_compliance': 0.7
            }
        },
        # Run 3 - Social distancing
        {
            'run': 'Run 3',
            'key': 'Social_Distancing_Only', 
            'check_params': {
                'vaccination_rate': 0.0,
                'mask_effectiveness': 0.0,
                'social_distancing': 0.7,
                'vaccination_strategy': 'none',
                'mask_compliance': 0.0
            }
        },
        # Run 4 - Vaccination
        {
            'run': 'Run 4',
            'key': 'Vaccination_Only',
            'check_params': {
                'vaccination_rate': 0.1,
                'mask_effectiveness': 0.0,
                'social_distancing': 0.0,
                'vaccination_strategy': 'single_dose_first',
                'vaccine_delay_days': 7,
                'mask_compliance': 0.0
            }
        },
        # Run 5 - All interventions
        {
            'run': 'Run 5',
            'key': 'All_Interventions',
            'check_params': {
                'vaccination_rate': 0.1,
                'mask_effectiveness': 0.7,
                'social_distancing': 0.7,
                'vaccination_strategy': 'single_dose_first',  # Note: User said 'single_dose' but model uses 'single_dose_first'
                'vaccine_delay_days': 7,
                'mask_compliance': 0.7
            }
        }
    ]
    
    all_match = True
    for spec in expected_specs:
        print(f"\n✅ {spec['run']} ({spec['key']}):")
        scenario_params = INTERVENTION_SCENARIOS[spec['key']]['params']
        
        for param, expected_value in spec['check_params'].items():
            actual_value = scenario_params[param]
            if actual_value == expected_value:
                print(f"   ✓ {param}: {actual_value} (matches)")
            else:
                print(f"   ❌ {param}: {actual_value} (expected {expected_value})")
                all_match = False
    
    print(f"\n{'🎉 ALL SCENARIOS MATCH USER SPECIFICATIONS!' if all_match else '⚠️ SOME MISMATCHES FOUND'}")
    
    # Note about vaccination strategy
    if INTERVENTION_SCENARIOS['All_Interventions']['params']['vaccination_strategy'] == 'single_dose_first':
        print(f"\n📝 Note: vaccination_strategy 'single_dose_first' used instead of 'single_dose'")
        print(f"   This matches the simulation model's expected parameter names.")
    
    return all_match

if __name__ == "__main__":
    print_scenario_summary()
    verify_exact_specifications()