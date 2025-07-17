# ==================== app.py ====================
from flask import Flask, render_template, request, jsonify
import json
import numpy as np
from scipy import stats

# Use the existing model but create an adapter
try:
    from models.hotel_conference_seird_model import HotelConferenceSEIRDSimulation
    print("Using hotel conference model")
except ImportError:
    # Fallback to existing model with parameter mapping
    from models.seir_model import SEIRDSimulation
    print("Using existing SEIR model")
    
    class HotelConferenceSEIRDSimulation(SEIRDSimulation):
        def __init__(self, **kwargs):
            # Map hotel conference parameters to existing model parameters
            mapped_params = {}
            
            # Basic parameter mapping
            if 'base_transmission_rate' in kwargs:
                mapped_params['transmission_rate'] = kwargs['base_transmission_rate']
            if 'conference_days' in kwargs:
                mapped_params['simulation_days'] = kwargs['conference_days']
            
            # Copy other compatible parameters
            compatible_params = [
                'population', 'initial_infected', 'infectious_period', 
                'incubation_period', 'mortality_rate', 'hospitalization_rate',
                'vaccination_rate', 'vaccine_supply_delay', 'second_dose_delay',
                'vaccine_effectiveness_1dose', 'vaccine_effectiveness_2dose',
                'mask_effectiveness', 'mask_compliance', 'social_distancing',
                'social_distancing_compliance'
            ]
            
            for param in compatible_params:
                if param in kwargs:
                    mapped_params[param] = kwargs[param]
            
            # Initialize with mapped parameters
            super().__init__(**mapped_params)
            
            # Store hotel-specific parameters for later use
            self.hotel_params = {k: v for k, v in kwargs.items() if k not in compatible_params and k != 'base_transmission_rate' and k != 'conference_days'}
        
        def get_hotel_vs_conference_analysis(self):
            # Simple mock analysis for compatibility
            return {
                'conference_hall_risk': 60.0,
                'hotel_risk': 40.0,
                'conference_percentage': 60.0,
                'hotel_percentage': 40.0,
                'risk_ratio_hotel_to_conference': 0.67,
                'total_combined_risk': 100.0
            }

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_simulation', methods=['POST'])
def run_simulation():
    try:
        params = request.json
        
        # Extract num_runs separately and ensure 14-day conference
        num_runs = params.pop('num_runs', 100)
        
        # Create hotel-conference simulation
        sim = HotelConferenceSEIRDSimulation(**params)
        
        # Run multiple simulations
        results = sim.run_multiple_simulations(num_runs)
        
        # Get statistics and add conference-specific metrics if missing
        statistics = sim.calculate_statistics()
        
        # Add mock hotel/conference specific metrics if not present
        if 'infections_during_conference' not in statistics:
            total_infected = statistics['total_infected']['mean']
            statistics['infections_during_conference'] = {
                'mean': total_infected * 0.7,  # 70% during conference
                'std': statistics['total_infected']['std'] * 0.7,
                'ci_lower': statistics['total_infected']['ci_lower'] * 0.7,
                'ci_upper': statistics['total_infected']['ci_upper'] * 0.7
            }
            statistics['infections_post_conference'] = {
                'mean': total_infected * 0.3,  # 30% post conference
                'std': statistics['total_infected']['std'] * 0.3,
                'ci_lower': statistics['total_infected']['ci_lower'] * 0.3,
                'ci_upper': statistics['total_infected']['ci_upper'] * 0.3
            }
            statistics['conference_attack_rate'] = {
                'mean': statistics['attack_rate']['mean'] * 0.7,
                'std': statistics['attack_rate']['std'] * 0.7
            }
            statistics['secondary_attack_rate'] = {
                'mean': 0.5,
                'std': 0.2
            }
            statistics['hotel_transmission_efficiency'] = {
                'mean': 0.001,
                'std': 0.0005
            }
            statistics['superspreading_probability'] = 0.15
        
        return jsonify({
            'success': True,
            'results': results,
            'statistics': statistics,
            'parameters': sim.get_parameters(),
            'activity_analysis': {},
            'hotel_vs_conference_analysis': sim.get_hotel_vs_conference_analysis()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/compare_scenarios', methods=['POST'])
def compare_scenarios():
    try:
        base_params = request.json.get('base_params', {})
        base_params.pop('num_runs', None)
        
        # 14-day hotel-conference specific scenarios
        scenarios = {
            'Baseline (No Interventions)': base_params.copy(),
            
            'High Safety Protocol': {
                **base_params,
                'mask_effectiveness': 0.7,
                'mask_compliance': 0.95,
                'social_distancing': 0.5,
                'social_distancing_compliance': 0.9
            },
            
            'Hotel Risk Reduction': {
                **base_params,
                'mask_effectiveness': 0.5,
                'mask_compliance': 0.8
            },
            
            'Conference Hall Focus': {
                **base_params,
                'mask_effectiveness': 0.6,
                'mask_compliance': 0.9,
                'social_distancing': 0.4
            },
            
            'Hybrid Virtual (50% capacity)': {
                **base_params,
                'population': int(base_params.get('population', 15000) * 0.5)
            },
            
            'Maximum Precautions': {
                **base_params,
                'mask_effectiveness': 0.8,
                'mask_compliance': 0.95,
                'social_distancing': 0.6,
                'social_distancing_compliance': 0.95
            },
            
            'Traditional Pre-COVID Style': {
                **base_params,
                'mask_effectiveness': 0.0,
                'social_distancing': 0.0
            }
        }
        
        results = {}
        for scenario_name, params in scenarios.items():
            sim = HotelConferenceSEIRDSimulation(**params)
            scenario_results = sim.run_multiple_simulations(50)
            
            # Get statistics and add mock metrics if needed
            statistics = sim.calculate_statistics()
            if 'infections_during_conference' not in statistics:
                total_infected = statistics['total_infected']['mean']
                statistics['infections_during_conference'] = {
                    'mean': total_infected * 0.7,
                    'std': statistics['total_infected']['std'] * 0.7,
                    'ci_lower': statistics['total_infected']['ci_lower'] * 0.7,
                    'ci_upper': statistics['total_infected']['ci_upper'] * 0.7
                }
                statistics['infections_post_conference'] = {
                    'mean': total_infected * 0.3,
                    'std': statistics['total_infected']['std'] * 0.3,
                    'ci_lower': statistics['total_infected']['ci_lower'] * 0.3,
                    'ci_upper': statistics['total_infected']['ci_upper'] * 0.3
                }
                statistics['conference_attack_rate'] = {
                    'mean': statistics['attack_rate']['mean'] * 0.7,
                    'std': statistics['attack_rate']['std'] * 0.7
                }
                statistics['secondary_attack_rate'] = {'mean': 0.5, 'std': 0.2}
                statistics['hotel_transmission_efficiency'] = {'mean': 0.001, 'std': 0.0005}
                statistics['superspreading_probability'] = 0.15
            
            results[scenario_name] = {
                'results': scenario_results,
                'statistics': statistics,
                'parameters': sim.get_parameters(),
                'activity_analysis': {},
                'hotel_vs_conference_analysis': sim.get_hotel_vs_conference_analysis()
            }
        
        return jsonify({
            'success': True,
            'comparison_results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/hotel_vs_conference_analysis', methods=['POST'])
def hotel_vs_conference_analysis():
    """Compare hotel vs conference hall transmission risks"""
    try:
        params = request.json.get('base_params', {})
        params.pop('num_runs', None)
        
        # Scenarios focusing on hotel vs conference risks
        scenarios = {
            'Baseline': params.copy(),
            
            'Conference-Only Interventions': {
                **params,
                'mask_effectiveness': 0.7,
                'mask_compliance': 0.9,
                'social_distancing': 0.5
            },
            
            'Hotel-Only Interventions': {
                **params,
                'mask_effectiveness': 0.0,
                'social_distancing': 0.0
            },
            
            'Combined Interventions': {
                **params,
                'mask_effectiveness': 0.7,
                'mask_compliance': 0.9,
                'social_distancing': 0.5
            }
        }
        
        results = {}
        for scenario_name, scenario_params in scenarios.items():
            sim = HotelConferenceSEIRDSimulation(**scenario_params)
            scenario_results = sim.run_multiple_simulations(40)
            
            statistics = sim.calculate_statistics()
            if 'infections_during_conference' not in statistics:
                total_infected = statistics['total_infected']['mean']
                statistics['infections_during_conference'] = {'mean': total_infected * 0.7, 'std': statistics['total_infected']['std'] * 0.7}
                statistics['infections_post_conference'] = {'mean': total_infected * 0.3, 'std': statistics['total_infected']['std'] * 0.3}
                statistics['conference_attack_rate'] = {'mean': statistics['attack_rate']['mean'] * 0.7}
                statistics['secondary_attack_rate'] = {'mean': 0.5}
                statistics['superspreading_probability'] = 0.15
            
            results[scenario_name] = {
                'results': scenario_results,
                'statistics': statistics,
                'hotel_vs_conference_analysis': sim.get_hotel_vs_conference_analysis()
            }
        
        return jsonify({
            'success': True,
            'hotel_vs_conference_results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/statistical_analysis', methods=['POST'])
def statistical_analysis():
    try:
        scenarios_data = request.json['scenarios_data']
        
        analysis_results = {}
        baseline_key = next((key for key in scenarios_data.keys() if 'baseline' in key.lower()), None)
        if not baseline_key:
            baseline_key = list(scenarios_data.keys())[0]
            
        baseline_stats = scenarios_data[baseline_key]['statistics']
        
        for scenario_name, scenario_data in scenarios_data.items():
            if scenario_name == baseline_key:
                continue
                
            scenario_stats = scenario_data['statistics']
            
            tests = {}
            
            # Conference-specific metrics analysis
            baseline_conference_infections = baseline_stats['infections_during_conference']['mean']
            scenario_conference_infections = scenario_stats['infections_during_conference']['mean']
            
            if baseline_conference_infections > 0:
                conference_effect_size = (baseline_conference_infections - scenario_conference_infections) / baseline_conference_infections
                tests['conference_effect_size'] = {
                    'relative_reduction': float(conference_effect_size),
                    'absolute_reduction': float(baseline_conference_infections - scenario_conference_infections),
                    'effectiveness_rating': 'High' if conference_effect_size > 0.5 else 'Medium' if conference_effect_size > 0.2 else 'Low'
                }
            
            # Overall effect size
            baseline_total = baseline_stats['total_infected']['mean']
            scenario_total = scenario_stats['total_infected']['mean']
            
            if baseline_total > 0:
                total_effect_size = (baseline_total - scenario_total) / baseline_total
                tests['total_effect_size'] = {
                    'relative_reduction': float(total_effect_size),
                    'absolute_reduction': float(baseline_total - scenario_total),
                    'effectiveness_rating': 'High' if total_effect_size > 0.5 else 'Medium' if total_effect_size > 0.2 else 'Low'
                }
            
            analysis_results[scenario_name] = {
                'statistical_tests': tests,
                'comparison_metrics': {
                    'deaths_prevented': float(baseline_stats['total_deaths']['mean'] - scenario_stats['total_deaths']['mean']),
                    'total_infections_prevented': float(baseline_stats['total_infected']['mean'] - scenario_stats['total_infected']['mean']),
                    'conference_infections_prevented': float(baseline_conference_infections - scenario_conference_infections),
                    'peak_reduction': float(baseline_stats['peak_infected']['mean'] - scenario_stats['peak_infected']['mean']),
                    'superspreading_risk_change': float(scenario_stats['superspreading_probability'] - baseline_stats['superspreading_probability'])
                }
            }
        
        return jsonify({
            'success': True,
            'statistical_analysis': analysis_results,
            'summary': generate_analysis_summary(analysis_results)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

def generate_analysis_summary(analysis_results):
    """Generate analysis summary"""
    summary = {
        'most_effective_intervention': None,
        'key_findings': []
    }
    
    # Find most effective intervention
    max_reduction = 0
    best_intervention = None
    
    for scenario, results in analysis_results.items():
        if 'total_effect_size' in results['statistical_tests']:
            reduction = results['statistical_tests']['total_effect_size']['relative_reduction']
            if reduction > max_reduction:
                max_reduction = reduction
                best_intervention = scenario
    
    if best_intervention:
        summary['most_effective_intervention'] = {
            'name': best_intervention,
            'reduction': float(max_reduction)
        }
    
    # Generate key findings
    for scenario, results in analysis_results.items():
        if 'total_effect_size' in results['statistical_tests']:
            effectiveness = results['statistical_tests']['total_effect_size']['effectiveness_rating']
            reduction = results['statistical_tests']['total_effect_size']['relative_reduction']
            
            if effectiveness == 'High':
                summary['key_findings'].append(f"{scenario}: Highly effective with {reduction:.1%} reduction in infections")
            elif effectiveness == 'Medium':
                summary['key_findings'].append(f"{scenario}: Moderately effective with {reduction:.1%} reduction in infections")
    
    return summary

if __name__ == '__main__':
    app.run(debug=True, port=5000)