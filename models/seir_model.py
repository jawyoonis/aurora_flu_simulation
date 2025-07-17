# ==================== models/seir_model.py ====================
import numpy as np
import scipy.stats as stats
from scipy.integrate import odeint
import random

class SEIRSimulation:
    def __init__(self, population=15000, initial_infected=1, transmission_rate=0.01,
                 infectious_period=3, simulation_days=14, incubation_period=2,
                 vaccination_rate=0.0, mask_effectiveness=0.0, social_distancing=0.0):
        
        self.N = population  # Total population
        self.I0 = initial_infected  # Initial infected
        self.beta = transmission_rate  # Transmission rate
        self.gamma = 1/infectious_period  # Recovery rate
        self.sigma = 1/incubation_period  # Incubation rate
        self.days = simulation_days
        self.vaccination_rate = vaccination_rate
        self.mask_effectiveness = mask_effectiveness
        self.social_distancing = social_distancing
        
        # Initialize compartments
        self.S0 = self.N - self.I0 - int(self.N * vaccination_rate)  # Susceptible
        self.E0 = 0  # Exposed
        self.R0_initial = int(self.N * vaccination_rate)  # Initially recovered (vaccinated)
        
        # Adjust transmission rate based on interventions
        self.effective_beta = self.beta * (1 - mask_effectiveness) * (1 - social_distancing)
        
        self.results_history = []
        self.statistics = {}
    
    def seir_model(self, y, t):
        """SEIR differential equation model"""
        S, E, I, R = y
        
        # Differential equations
        dSdt = -self.effective_beta * S * I / self.N
        dEdt = self.effective_beta * S * I / self.N - self.sigma * E
        dIdt = self.sigma * E - self.gamma * I
        dRdt = self.gamma * I
        
        return [dSdt, dEdt, dIdt, dRdt]
    
    def run_single_simulation(self):
        """Run a single SEIR simulation"""
        # Time points
        t = np.linspace(0, self.days, self.days + 1)
        
        # Initial conditions
        y0 = [self.S0, self.E0, self.I0, self.R0_initial]
        
        # Solve ODE
        solution = odeint(self.seir_model, y0, t)
        
        # Extract results
        S, E, I, R = solution.T
        
        return {
            'time': t.tolist(),
            'susceptible': S.tolist(),
            'exposed': E.tolist(),
            'infected': I.tolist(),
            'recovered': R.tolist(),
            'total_infected': (self.N - S[-1]),
            'peak_infected': max(I),
            'peak_day': int(np.argmax(I))
        }
    
    def run_stochastic_simulation(self):
        """Run a stochastic version of the simulation"""
        S, E, I, R = self.S0, self.E0, self.I0, self.R0_initial
        
        results = {
            'time': [],
            'susceptible': [],
            'exposed': [],
            'infected': [],
            'recovered': []
        }
        
        for day in range(self.days + 1):
            results['time'].append(day)
            results['susceptible'].append(S)
            results['exposed'].append(E)
            results['infected'].append(I)
            results['recovered'].append(R)
            
            if day < self.days:
                # Stochastic transitions
                new_exposed = np.random.binomial(int(S), min(self.effective_beta * I / self.N, 1.0))
                new_infected = np.random.binomial(int(E), min(self.sigma, 1.0))
                new_recovered = np.random.binomial(int(I), min(self.gamma, 1.0))
                
                # Update compartments
                S -= new_exposed
                E = E + new_exposed - new_infected
                I = I + new_infected - new_recovered
                R += new_recovered
        
        results['total_infected'] = self.N - S
        results['peak_infected'] = max(results['infected'])
        results['peak_day'] = results['infected'].index(results['peak_infected'])
        
        return results
    
    def run_multiple_simulations(self, num_runs=100):
        """Run multiple simulations for statistical analysis"""
        all_results = []
        
        for _ in range(num_runs):
            if num_runs <= 10:  # Use deterministic for small runs
                result = self.run_single_simulation()
            else:  # Use stochastic for larger runs
                result = self.run_stochastic_simulation()
            all_results.append(result)
        
        self.results_history = all_results
        self.calculate_statistics()
        
        # Return average results for plotting
        avg_results = self.calculate_average_results()
        return avg_results
    
    def calculate_average_results(self):
        """Calculate average results across all simulations"""
        if not self.results_history:
            return None
        
        # Initialize arrays
        time_points = self.results_history[0]['time']
        avg_S = np.zeros(len(time_points))
        avg_E = np.zeros(len(time_points))
        avg_I = np.zeros(len(time_points))
        avg_R = np.zeros(len(time_points))
        
        # Calculate averages
        for result in self.results_history:
            avg_S += np.array(result['susceptible'])
            avg_E += np.array(result['exposed'])
            avg_I += np.array(result['infected'])
            avg_R += np.array(result['recovered'])
        
        num_sims = len(self.results_history)
        
        return {
            'time': time_points,
            'susceptible': (avg_S / num_sims).tolist(),
            'exposed': (avg_E / num_sims).tolist(),
            'infected': (avg_I / num_sims).tolist(),
            'recovered': (avg_R / num_sims).tolist(),
            'confidence_intervals': self.calculate_confidence_intervals()
        }
    
    def calculate_confidence_intervals(self):
        """Calculate 95% confidence intervals for key metrics"""
        if not self.results_history:
            return {}
        
        # Extract key metrics from all runs
        total_infected = [r['total_infected'] for r in self.results_history]
        peak_infected = [r['peak_infected'] for r in self.results_history]
        peak_day = [r['peak_day'] for r in self.results_history]
        
        def ci_95(data):
            return {
                'mean': np.mean(data),
                'std': np.std(data),
                'ci_lower': np.percentile(data, 2.5),
                'ci_upper': np.percentile(data, 97.5)
            }
        
        return {
            'total_infected': ci_95(total_infected),
            'peak_infected': ci_95(peak_infected),
            'peak_day': ci_95(peak_day)
        }
    
    def calculate_statistics(self):
        """Calculate comprehensive statistics"""
        if not self.results_history:
            return {}
        
        # Calculate R0 (basic reproduction number)
        R0 = self.effective_beta / self.gamma
        
        # Extract metrics
        total_infected = [r['total_infected'] for r in self.results_history]
        attack_rate = [ti / self.N * 100 for ti in total_infected]
        
        self.statistics = {
            'R0': R0,
            'mean_total_infected': np.mean(total_infected),
            'mean_attack_rate': np.mean(attack_rate),
            'std_total_infected': np.std(total_infected),
            'confidence_intervals': self.calculate_confidence_intervals(),
            'epidemic_probability': sum(1 for ti in total_infected if ti > 10) / len(total_infected)
        }
        
        return self.statistics
    
    def get_parameters(self):
        """Return simulation parameters"""
        return {
            'population': self.N,
            'initial_infected': self.I0,
            'transmission_rate': self.beta,
            'effective_transmission_rate': self.effective_beta,
            'infectious_period': 1/self.gamma,
            'incubation_period': 1/self.sigma,
            'vaccination_rate': self.vaccination_rate,
            'mask_effectiveness': self.mask_effectiveness,
            'social_distancing': self.social_distancing,
            'simulation_days': self.days
        }