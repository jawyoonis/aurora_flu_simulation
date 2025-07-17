# ==================== models/seird_model.py ====================
import numpy as np
import scipy.stats as stats
from scipy.integrate import odeint
import random
from typing import Dict, List, Tuple, Optional

class SEIRDSimulation:
    """
    Enhanced SEIRD model with death compartment and advanced interventions
    """
    def __init__(self, population=15000, initial_infected=1, transmission_rate=0.01,
                 infectious_period=7, simulation_days=14, incubation_period=3,
                 mortality_rate=0.002, hospitalization_rate=0.05,
                 vaccination_rate=0.0, mask_effectiveness=0.0, social_distancing=0.0,
                 vaccine_supply_delay=0, second_dose_delay=21, vaccine_effectiveness_1dose=0.5,
                 vaccine_effectiveness_2dose=0.85, mask_compliance=1.0, 
                 social_distancing_compliance=1.0, location_type="office"):
        
        self.N = int(population)
        self.I0 = int(initial_infected)
        self.beta = float(transmission_rate)
        self.gamma = float(1/infectious_period)
        self.sigma = float(1/incubation_period)
        self.mu = float(mortality_rate)  # Death rate
        self.hospitalization_rate = float(hospitalization_rate)
        self.days = int(simulation_days)
        
        # Vaccination parameters
        self.vaccination_rate = float(vaccination_rate)
        self.vaccine_supply_delay = int(vaccine_supply_delay)
        self.second_dose_delay = int(second_dose_delay)
        self.vaccine_effectiveness_1dose = float(vaccine_effectiveness_1dose)
        self.vaccine_effectiveness_2dose = float(vaccine_effectiveness_2dose)
        
        # Intervention parameters
        self.mask_effectiveness = float(mask_effectiveness)
        self.social_distancing = float(social_distancing)
        self.mask_compliance = float(mask_compliance)
        self.social_distancing_compliance = float(social_distancing_compliance)
        
        # Location-specific parameters
        self.location_type = str(location_type)
        self.contact_matrix = self._get_contact_matrix()
        
        # Initialize compartments
        self.S0 = self.N - self.I0
        self.E0 = 0
        self.R0_initial = 0
        self.D0 = 0
        self.V1_0 = 0  # First dose vaccinated
        self.V2_0 = 0  # Fully vaccinated
        
        # Calculate effective transmission rate
        self.effective_beta = self._calculate_effective_beta()
        
        self.results_history = []
        self.statistics = {}
        
    def _get_contact_matrix(self) -> float:
        """Get contact rate based on location type"""
        contact_rates = {
            "office": 1.0,
            "classroom": 1.2,
            "restaurant": 0.8,
            "home": 0.3,
            "outdoor": 0.1
        }
        return float(contact_rates.get(self.location_type, 1.0))
    
    def _calculate_effective_beta(self) -> float:
        """Calculate effective transmission rate with interventions"""
        # Base transmission adjusted for location
        base_beta = self.beta * self.contact_matrix
        
        # Apply mask effectiveness with compliance
        mask_reduction = self.mask_effectiveness * self.mask_compliance
        
        # Apply social distancing with compliance
        distancing_reduction = self.social_distancing * self.social_distancing_compliance
        
        # Combined effect (assuming multiplicative)
        effective_beta = base_beta * (1 - mask_reduction) * (1 - distancing_reduction)
        
        return float(effective_beta)
    
    def _convert_to_python_types(self, obj):
        """Convert numpy types to Python native types for JSON serialization"""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, list):
            return [self._convert_to_python_types(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self._convert_to_python_types(value) for key, value in obj.items()}
        else:
            return obj
    
    def seird_model(self, y, t):
        """Extended SEIRD differential equation model"""
        S, E, I, R, D, V1, V2 = y
        
        # Vaccination dynamics
        vaccination_start = self.vaccine_supply_delay
        if t >= vaccination_start:
            # First dose vaccination rate
            v1_rate = min(self.vaccination_rate, S / self.N) if S > 0 else 0
            # Second dose vaccination rate (after delay)
            v2_rate = min(self.vaccination_rate, V1 / self.N) if t >= vaccination_start + self.second_dose_delay and V1 > 0 else 0
        else:
            v1_rate = v2_rate = 0
        
        # Effective susceptibility (reduced by vaccination)
        S_eff = S + V1 * (1 - self.vaccine_effectiveness_1dose) + V2 * (1 - self.vaccine_effectiveness_2dose)
        
        # Infection force
        infection_force = self.effective_beta * I * S_eff / self.N
        
        # Differential equations
        dSdt = -infection_force - v1_rate * S
        dEdt = infection_force - self.sigma * E
        dIdt = self.sigma * E - self.gamma * I - self.mu * I
        dRdt = self.gamma * I - v1_rate * R - v2_rate * R
        dDdt = self.mu * I
        dV1dt = v1_rate * (S + R) - v2_rate * V1
        dV2dt = v2_rate * (V1 + R)
        
        return [dSdt, dEdt, dIdt, dRdt, dDdt, dV1dt, dV2dt]
    
    def run_single_simulation(self):
        """Run a single SEIRD simulation"""
        t = np.linspace(0, self.days, self.days + 1)
        y0 = [self.S0, self.E0, self.I0, self.R0_initial, self.D0, self.V1_0, self.V2_0]
        
        solution = odeint(self.seird_model, y0, t)
        S, E, I, R, D, V1, V2 = solution.T
        
        # Calculate derived metrics
        total_infected = self.N - S[-1] - V1[-1] - V2[-1]
        peak_infected = np.max(I)
        peak_day = int(np.argmax(I))
        
        # Calculate hospitalization
        hospitalized = I * self.hospitalization_rate
        peak_hospitalized = np.max(hospitalized)
        
        # Calculate epidemic duration
        epidemic_threshold = 1
        epidemic_days = np.where(I > epidemic_threshold)[0]
        epidemic_duration = len(epidemic_days) if len(epidemic_days) > 0 else 0
        
        result = {
            'time': t.tolist(),
            'susceptible': S.tolist(),
            'exposed': E.tolist(),
            'infected': I.tolist(),
            'recovered': R.tolist(),
            'deaths': D.tolist(),
            'vaccinated_1dose': V1.tolist(),
            'vaccinated_2dose': V2.tolist(),
            'hospitalized': hospitalized.tolist(),
            'total_infected': float(total_infected),
            'total_deaths': float(D[-1]),
            'peak_infected': float(peak_infected),
            'peak_hospitalized': float(peak_hospitalized),
            'peak_day': int(peak_day),
            'epidemic_duration': int(epidemic_duration),
            'final_vaccination_rate': float((V1[-1] + V2[-1]) / self.N),
            'case_fatality_rate': float(D[-1] / max(total_infected, 1)),
            'attack_rate': float(total_infected / self.N)
        }
        
        return self._convert_to_python_types(result)
    
    def run_stochastic_simulation(self):
        """Run stochastic version with binomial transitions"""
        S, E, I, R, D, V1, V2 = float(self.S0), float(self.E0), float(self.I0), float(self.R0_initial), float(self.D0), float(self.V1_0), float(self.V2_0)
        
        results = {
            'time': [],
            'susceptible': [],
            'exposed': [],
            'infected': [],
            'recovered': [],
            'deaths': [],
            'vaccinated_1dose': [],
            'vaccinated_2dose': [],
            'hospitalized': []
        }
        
        for day in range(self.days + 1):
            # Record current state
            results['time'].append(day)
            results['susceptible'].append(S)
            results['exposed'].append(E)
            results['infected'].append(I)
            results['recovered'].append(R)
            results['deaths'].append(D)
            results['vaccinated_1dose'].append(V1)
            results['vaccinated_2dose'].append(V2)
            results['hospitalized'].append(I * self.hospitalization_rate)
            
            if day < self.days:
                # Stochastic transitions
                # Vaccination
                if day >= self.vaccine_supply_delay:
                    new_v1 = min(np.random.poisson(self.vaccination_rate * self.N), int(S + R))
                    if day >= self.vaccine_supply_delay + self.second_dose_delay:
                        new_v2 = min(np.random.poisson(self.vaccination_rate * self.N), int(V1))
                    else:
                        new_v2 = 0
                else:
                    new_v1 = new_v2 = 0
                
                # Infection
                S_eff = S + V1 * (1 - self.vaccine_effectiveness_1dose) + V2 * (1 - self.vaccine_effectiveness_2dose)
                infection_prob = min(self.effective_beta * I / self.N, 1.0)
                new_exposed = np.random.binomial(max(int(S_eff), 0), infection_prob)
                
                # Disease progression
                new_infected = np.random.binomial(max(int(E), 0), min(self.sigma, 1.0))
                new_recovered = np.random.binomial(max(int(I), 0), min(self.gamma, 1.0))
                new_deaths = np.random.binomial(max(int(I), 0), min(self.mu, 1.0))
                
                # Update compartments
                total_sr = max(S + R, 1)
                S = max(0, S - new_exposed - new_v1 * S / total_sr)
                E = max(0, E + new_exposed - new_infected)
                I = max(0, I + new_infected - new_recovered - new_deaths)
                R = max(0, R + new_recovered - new_v1 * R / total_sr)
                D = D + new_deaths
                V1 = max(0, V1 + new_v1 - new_v2)
                V2 = V2 + new_v2
        
        # Calculate final metrics
        total_infected = self.N - S
        total_deaths = D
        peak_infected = max(results['infected'])
        peak_day = results['infected'].index(peak_infected)
        
        # Add derived metrics
        results.update({
            'total_infected': float(total_infected),
            'total_deaths': float(total_deaths),
            'peak_infected': float(peak_infected),
            'peak_day': int(peak_day),
            'epidemic_duration': int(len([x for x in results['infected'] if x > 1])),
            'final_vaccination_rate': float((V1 + V2) / self.N),
            'case_fatality_rate': float(total_deaths / max(total_infected, 1)),
            'attack_rate': float(total_infected / self.N)
        })
        
        return self._convert_to_python_types(results)
    
    def run_multiple_simulations(self, num_runs=100):
        """Run multiple simulations for statistical analysis"""
        all_results = []
        
        for _ in range(num_runs):
            if num_runs <= 10:
                result = self.run_single_simulation()
            else:
                result = self.run_stochastic_simulation()
            all_results.append(result)
        
        self.results_history = all_results
        self.calculate_statistics()
        
        return self.calculate_average_results()
    
    def calculate_average_results(self):
        """Calculate average results with confidence intervals"""
        if not self.results_history:
            return None
        
        time_points = self.results_history[0]['time']
        num_sims = len(self.results_history)
        
        # Initialize arrays for averaging
        compartments = ['susceptible', 'exposed', 'infected', 'recovered', 'deaths', 
                       'vaccinated_1dose', 'vaccinated_2dose', 'hospitalized']
        
        avg_results = {'time': time_points}
        
        for comp in compartments:
            values = np.array([result[comp] for result in self.results_history])
            avg_results[comp] = np.mean(values, axis=0).tolist()
            
            # Calculate confidence intervals
            ci_lower = np.percentile(values, 2.5, axis=0).tolist()
            ci_upper = np.percentile(values, 97.5, axis=0).tolist()
            avg_results[f'{comp}_ci_lower'] = ci_lower
            avg_results[f'{comp}_ci_upper'] = ci_upper
        
        return self._convert_to_python_types(avg_results)
    
    def calculate_statistics(self):
        """Calculate comprehensive statistics with confidence intervals"""
        if not self.results_history:
            return {}
        
        # Calculate R0 (basic reproduction number)
        R0 = self.effective_beta / self.gamma
        
        # Extract key metrics
        metrics = ['total_infected', 'total_deaths', 'peak_infected', 'peak_day', 
                  'epidemic_duration', 'attack_rate', 'case_fatality_rate', 
                  'final_vaccination_rate']
        
        def calculate_ci(data):
            data = np.array(data)
            return {
                'mean': float(np.mean(data)),
                'std': float(np.std(data)),
                'median': float(np.median(data)),
                'ci_lower': float(np.percentile(data, 2.5)),
                'ci_upper': float(np.percentile(data, 97.5)),
                'min': float(np.min(data)),
                'max': float(np.max(data))
            }
        
        statistics = {'R0': float(R0)}
        
        for metric in metrics:
            values = [result[metric] for result in self.results_history]
            statistics[metric] = calculate_ci(values)
        
        # Calculate epidemic probability (more than 1% of population infected)
        epidemic_threshold = 0.01 * self.N
        epidemic_prob = sum(1 for result in self.results_history 
                          if result['total_infected'] > epidemic_threshold) / len(self.results_history)
        
        statistics['epidemic_probability'] = float(epidemic_prob)
        
        self.statistics = self._convert_to_python_types(statistics)
        return self.statistics
    
    def get_parameters(self):
        """Return comprehensive simulation parameters"""
        params = {
            'population': self.N,
            'initial_infected': self.I0,
            'transmission_rate': self.beta,
            'effective_transmission_rate': self.effective_beta,
            'infectious_period': 1/self.gamma,
            'incubation_period': 1/self.sigma,
            'mortality_rate': self.mu,
            'hospitalization_rate': self.hospitalization_rate,
            'vaccination_rate': self.vaccination_rate,
            'vaccine_supply_delay': self.vaccine_supply_delay,
            'second_dose_delay': self.second_dose_delay,
            'vaccine_effectiveness_1dose': self.vaccine_effectiveness_1dose,
            'vaccine_effectiveness_2dose': self.vaccine_effectiveness_2dose,
            'mask_effectiveness': self.mask_effectiveness,
            'mask_compliance': self.mask_compliance,
            'social_distancing': self.social_distancing,
            'social_distancing_compliance': self.social_distancing_compliance,
            'location_type': self.location_type,
            'simulation_days': self.days,
            'R0': self.effective_beta / self.gamma
        }
        
        return self._convert_to_python_types(params)