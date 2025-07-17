# ==================== app.py ====================
from flask import Flask, render_template, request, jsonify
import json
from models.seir_model import SEIRSimulation
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_simulation', methods=['POST'])
def run_simulation():
    try:
        # Get parameters from request
        params = request.json
        
        # Create and run simulation
        sim = SEIRSimulation(
            population=params.get('population', 15000),
            initial_infected=params.get('initial_infected', 1),
            transmission_rate=params.get('transmission_rate', 0.01),
            infectious_period=params.get('infectious_period', 3),
            simulation_days=params.get('simulation_days', 14),
            incubation_period=params.get('incubation_period', 2),
            vaccination_rate=params.get('vaccination_rate', 0.0),
            mask_effectiveness=params.get('mask_effectiveness', 0.0),
            social_distancing=params.get('social_distancing', 0.0)
        )
        
        # Run multiple simulations for statistical analysis
        num_runs = params.get('num_runs', 100)
        results = sim.run_multiple_simulations(num_runs)
        
        return jsonify({
            'success': True,
            'results': results,
            'statistics': sim.calculate_statistics(),
            'parameters': sim.get_parameters()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/compare_scenarios', methods=['POST'])
def compare_scenarios():
    try:
        scenarios = request.json['scenarios']
        results = {}
        
        for scenario_name, params in scenarios.items():
            sim = SEIRSimulation(**params)
            scenario_results = sim.run_multiple_simulations(50)
            results[scenario_name] = {
                'results': scenario_results,
                'statistics': sim.calculate_statistics()
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

if __name__ == '__main__':
    app.run(debug=True)