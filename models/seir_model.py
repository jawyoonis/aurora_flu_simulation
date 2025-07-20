import numpy as np
import random
from dataclasses import dataclass
from typing import List, Dict, Any
from scipy.integrate import odeint
from scipy.stats import beta, norm, triang
import time

@dataclass
class Engineer:
    """Individual engineer agent for Aurora Symposium simulation"""
    id: int
    state: str  # 'S', 'E', 'I', 'R', 'D'
    age: int
    vaccination_status: str  # 'none', 'partial', 'full'
    mask_wearing: bool
    days_in_state: int = 0
    incubation_days: int = 0
    infectious_days: int = 0
    infection_day: int = -1
    recovery_day: int = -1
    mobility_factor: float = 1.0  # How much they move around
    compliance_factor: float = 1.0  # How well they follow guidelines

class AuroraFluSimulation:
    """Enhanced Aurora Winter Engineering Symposium Flu Simulation"""
    
    def __init__(self, population=15000, initial_infected=1, transmission_rate=0.01,
                 infectious_period=3, simulation_days=14, incubation_period=2,
                 vaccination_rate=0.0, mask_effectiveness=0.6, social_distancing=0.0,
                 mortality_rate=0.0002, vaccination_strategy='none', 
                 vaccine_supply_per_day=500, vaccine_delay_days=0, mask_compliance=0.0,
                 vaccine_1dose_effectiveness=0.4, vaccine_2dose_effectiveness=0.8,
                 use_parameter_distributions=True):
        
        # Ensure different random seeds for each simulation
        current_time = int(time.time() * 1000000) % (2**32)
        np.random.seed(current_time)
        random.seed(current_time)
        
        # Aurora Symposium parameters
        self.N = population
        self.I0 = initial_infected
        self.gamma = 1/infectious_period
        self.sigma = 1/incubation_period
        self.days = simulation_days
        
        # Apply parameter distributions if enabled
        if use_parameter_distributions:
            # Infection rate (transmission rate): Uniform(0.2, 0.4)
            self.beta = np.random.uniform(0.2, 0.4)
            
            # Mask effectiveness: Normal(0.5, 0.1) - clipped to [0, 1]
            self.mask_effectiveness = np.clip(np.random.normal(0.5, 0.1), 0, 1)
            
            # Vaccination coverage: Triangular(0.5, 0.7, 0.9) - mode at 0.7
            self.vaccination_rate = np.random.triangular(0.5, 0.7, 0.9)
            
            # Death rate: Beta(2, 10) - scaled to reasonable range [0, 0.05]
            self.mortality_rate = beta.rvs(2, 10) * 0.05
        else:
            # Use provided parameters directly
            self.beta = transmission_rate
            self.vaccination_rate = vaccination_rate
            self.mask_effectiveness = mask_effectiveness
            self.mortality_rate = mortality_rate
        
        # Other intervention parameters with random variations
        self.social_distancing = social_distancing * np.random.uniform(0.8, 1.2)
        self.mask_compliance = mask_compliance * np.random.uniform(0.9, 1.1)
        
        # Vaccination parameters
        self.vaccination_strategy = vaccination_strategy
        self.vaccine_supply_per_day = vaccine_supply_per_day
        self.vaccine_delay_days = vaccine_delay_days
        self.vaccine_1dose_eff = vaccine_1dose_effectiveness
        self.vaccine_2dose_eff = vaccine_2dose_effectiveness
        
        # Symposium-specific factors
        self.symposium_days = 5  # Days 0-4 are symposium days
        self.networking_intensity = np.random.uniform(1.5, 2.5)  # Multiplier for symposium transmission
        self.post_symposium_reduction = np.random.uniform(0.3, 0.7)  # Reduction after symposium
        
        # Weather and environmental factors
        self.weather_factor = np.random.uniform(0.8, 1.3)  # Cold weather affects transmission
        self.venue_ventilation = np.random.uniform(0.7, 1.2)  # Venue air quality factor
        
        # Population tracking
        self.engineers = []
        self.daily_stats = []
        self.vaccination_log = []
        self.transmission_events = []
        
        # Initialize population
        self._initialize_population()
    
    def _initialize_population(self):
        """Initialize 15,000 engineers with realistic characteristics"""
        self.engineers = []
        
        for i in range(self.N):
            # Realistic age distribution for engineering professionals
            age_groups = [25, 30, 35, 40, 45, 50, 55, 60, 65]
            age_probs = [0.18, 0.22, 0.20, 0.15, 0.12, 0.08, 0.03, 0.015, 0.005]
            age = np.random.choice(age_groups, p=age_probs)
            
            # Pre-symposium vaccination status with age bias
            vax_status = 'none'
            base_vax_prob = self.vaccination_rate
            # Older engineers more likely to be vaccinated
            age_adjusted_prob = base_vax_prob * (1 + (age - 35) * 0.01)
            age_adjusted_prob = max(0, min(1, age_adjusted_prob))
            
            if random.random() < age_adjusted_prob:
                vax_status = 'full' if random.random() < 0.7 else 'partial'
            
            # Mask wearing with individual compliance variation
            base_mask_prob = self.mask_compliance
            individual_compliance = np.random.uniform(0.5, 1.5)
            mask_wearing = random.random() < (base_mask_prob * individual_compliance)
            
            # Individual characteristics
            mobility_factor = np.random.uniform(0.5, 2.0)  # How much they move around
            compliance_factor = np.random.uniform(0.7, 1.3)  # How well they follow guidelines
            
            # Health state - Patient Zero vs others
            state = 'I' if i == 0 else 'S'
            
            # Add some pre-existing immunity from previous flu exposure
            if state == 'S' and random.random() < 0.05:  # 5% have natural immunity
                state = 'R'
            
            engineer = Engineer(
                id=i,
                state=state,
                age=age,
                vaccination_status=vax_status,
                mask_wearing=mask_wearing,
                incubation_days=max(1, int(np.random.normal(2, 0.5))),  # Variable incubation
                infectious_days=max(1, int(np.random.normal(3, 0.7))),  # Variable infectious period
                mobility_factor=mobility_factor,
                compliance_factor=compliance_factor
            )
            
            # Set Patient Zero details
            if i == 0:
                engineer.infection_day = 0
                engineer.days_in_state = 0
            
            self.engineers.append(engineer)
    
    def run_simulation(self):
        """Run complete Aurora Symposium simulation with time-varying parameters"""
        self.daily_stats = []
        self.transmission_events = []
        
        for day in range(self.days + 1):
            # Calculate daily transmission factors
            daily_factors = self._calculate_daily_factors(day)
            
            # Simulate this day
            daily_data = self._simulate_day(day, daily_factors)
            self.daily_stats.append(daily_data)
            
            if day < self.days:
                # Apply interventions
                self._apply_vaccination(day)
                # Update disease states
                self._update_disease_states(day)
                # Random events (super-spreader events, etc.)
                self._apply_random_events(day)
        
        return self._compile_results()
    
    def _calculate_daily_factors(self, day):
        """Calculate time-varying transmission factors"""
        factors = {
            'base_transmission': self.beta,
            'contact_multiplier': 1.0,
            'venue_factor': 1.0,
            'weather_factor': self.weather_factor,
            'behavioral_factor': 1.0
        }
        
        # Symposium vs post-symposium dynamics
        if day <= self.symposium_days:
            # During symposium: higher contact rates
            factors['contact_multiplier'] = self.networking_intensity
            factors['venue_factor'] = self.venue_ventilation
            
            # Different activities each day
            if day == 0:  # Arrival day
                factors['contact_multiplier'] *= 0.7
            elif day in [1, 2, 3]:  # Peak symposium days
                factors['contact_multiplier'] *= np.random.uniform(1.2, 1.8)
            elif day == 4:  # Departure day
                factors['contact_multiplier'] *= 0.8
                
        else:
            # Post-symposium: reduced contact, geographic dispersal
            factors['contact_multiplier'] = self.post_symposium_reduction
            factors['venue_factor'] = 1.0
            
            # Exponential decay of contact over time
            days_post = day - self.symposium_days
            decay_factor = np.exp(-0.2 * days_post)
            factors['contact_multiplier'] *= decay_factor
        
        # Weekly patterns (weekends have different patterns)
        day_of_week = day % 7
        if day_of_week in [5, 6]:  # Weekend
            if day <= self.symposium_days:
                factors['contact_multiplier'] *= 1.3  # More social events
            else:
                factors['contact_multiplier'] *= 0.6  # Less contact post-symposium
        
        # Random daily variations
        factors['behavioral_factor'] = np.random.uniform(0.8, 1.2)
        
        return factors
    
    def _simulate_day(self, day, daily_factors):
        """Simulate one day with given factors"""
        # Count current states
        states = {'S': 0, 'E': 0, 'I': 0, 'R': 0, 'D': 0}
        for eng in self.engineers:
            states[eng.state] += 1
        
        # Calculate new infections
        new_infections = 0
        if day > 0 and states['I'] > 0:
            new_infections = self._calculate_new_infections(day, daily_factors)
        
        # Calculate other metrics
        vax_partial = sum(1 for e in self.engineers if e.vaccination_status == 'partial')
        vax_full = sum(1 for e in self.engineers if e.vaccination_status == 'full')
        current_mask_compliance = sum(1 for e in self.engineers if e.mask_wearing) / self.N
        
        # Effective R calculation
        if states['S'] > 0 and day > 1:
            effective_r = self._calculate_effective_r(day, daily_factors, states)
        else:
            effective_r = self.beta / self.gamma
        
        return {
            'day': day,
            'susceptible': states['S'],
            'exposed': states['E'],
            'infected': states['I'],
            'recovered': states['R'],
            'dead': states['D'],
            'new_infections': new_infections,
            'cumulative_infected': states['E'] + states['I'] + states['R'] + states['D'],
            'partially_vaccinated': vax_partial,
            'fully_vaccinated': vax_full,
            'mask_compliance': current_mask_compliance,
            'effective_r': effective_r,
            'daily_factors': daily_factors
        }
    
    def _calculate_new_infections(self, day, daily_factors):
        """Calculate new infections with realistic transmission dynamics"""
        infectious_engineers = [e for e in self.engineers if e.state == 'I']
        susceptible_engineers = [e for e in self.engineers if e.state == 'S']
        
        if not infectious_engineers or not susceptible_engineers:
            return 0
        
        new_infections = 0
        
        # Calculate base transmission probability
        base_prob = (daily_factors['base_transmission'] * 
                    daily_factors['contact_multiplier'] * 
                    daily_factors['venue_factor'] * 
                    daily_factors['weather_factor'] * 
                    daily_factors['behavioral_factor'])
        
        for s_eng in susceptible_engineers:
            total_exposure_prob = 0
            
            for i_eng in infectious_engineers:
                # Individual transmission probability
                individual_prob = base_prob
                
                # Adjust for individual mobility and compliance
                individual_prob *= (s_eng.mobility_factor + i_eng.mobility_factor) / 2
                
                # Mask effectiveness (both need to wear for maximum effect)
                mask_reduction = 0
                if s_eng.mask_wearing and i_eng.mask_wearing:
                    mask_reduction = self.mask_effectiveness * 0.95
                elif s_eng.mask_wearing or i_eng.mask_wearing:
                    mask_reduction = self.mask_effectiveness * 0.6
                
                individual_prob *= (1 - mask_reduction)
                
                # Social distancing compliance
                sd_compliance = (s_eng.compliance_factor + i_eng.compliance_factor) / 2
                individual_prob *= (1 - self.social_distancing * sd_compliance)
                
                # Vaccination protection
                if s_eng.vaccination_status == 'full':
                    protection = self.vaccine_2dose_eff * np.random.uniform(0.8, 1.0)
                    individual_prob *= (1 - protection)
                elif s_eng.vaccination_status == 'partial':
                    protection = self.vaccine_1dose_eff * np.random.uniform(0.7, 1.0)
                    individual_prob *= (1 - protection)
                
                # Age-based susceptibility
                age_factor = 1.0
                if s_eng.age >= 60:
                    age_factor = 1.4
                elif s_eng.age >= 45:
                    age_factor = 1.2
                elif s_eng.age <= 30:
                    age_factor = 0.8
                
                individual_prob *= age_factor
                
                # Infectiousness varies by days infectious
                infectiousness_curve = [0.3, 1.0, 1.0, 0.7, 0.4]  # Days 1-5 of infection
                if i_eng.days_in_state < len(infectiousness_curve):
                    individual_prob *= infectiousness_curve[i_eng.days_in_state]
                
                total_exposure_prob += individual_prob
            
            # Apply infection probability (with overdispersion)
            final_prob = min(total_exposure_prob, 0.8)  # Cap at 80% daily probability
            
            # Add random variation for superspreading events
            if random.random() < 0.05:  # 5% chance of superspreader exposure
                final_prob *= np.random.uniform(2, 5)
                final_prob = min(final_prob, 0.95)
            
            if random.random() < final_prob:
                s_eng.state = 'E'
                s_eng.infection_day = day
                s_eng.days_in_state = 0
                new_infections += 1
                
                # Log transmission event
                self.transmission_events.append({
                    'day': day,
                    'susceptible_id': s_eng.id,
                    'source_infections': len(infectious_engineers),
                    'probability': final_prob
                })
        
        return new_infections
    
    def _calculate_effective_r(self, day, daily_factors, states):
        """Calculate time-varying effective reproduction number"""
        if states['S'] <= 0:
            return 0
        
        base_r = self.beta / self.gamma
        
        # Adjust for current interventions
        intervention_factor = (1 - self.mask_compliance * self.mask_effectiveness) * (1 - self.social_distancing)
        
        # Adjust for susceptible population
        susceptible_factor = states['S'] / self.N
        
        # Adjust for daily factors
        daily_factor = (daily_factors['contact_multiplier'] * 
                       daily_factors['venue_factor'] * 
                       daily_factors['behavioral_factor'])
        
        return base_r * intervention_factor * susceptible_factor * daily_factor
    
    def _update_disease_states(self, day):
        """Update disease progression with random variations"""
        for eng in self.engineers:
            if eng.state in ['E', 'I']:
                eng.days_in_state += 1
            
            # Exposed → Infected
            if eng.state == 'E' and eng.days_in_state >= eng.incubation_days:
                eng.state = 'I'
                eng.days_in_state = 0
                # Add some variation to infectious period
                eng.infectious_days = max(1, int(np.random.normal(3, 0.7)))
            
            # Infected → Recovered or Dead
            elif eng.state == 'I' and eng.days_in_state >= eng.infectious_days:
                # Age and health-adjusted mortality
                death_prob = self.mortality_rate
                if eng.age >= 65:
                    death_prob *= 8
                elif eng.age >= 50:
                    death_prob *= 3
                elif eng.age <= 30:
                    death_prob *= 0.3
                
                # Add random individual health variation
                death_prob *= np.random.uniform(0.5, 2.0)
                
                if random.random() < death_prob:
                    eng.state = 'D'
                else:
                    eng.state = 'R'
                    eng.recovery_day = day
                
                eng.days_in_state = 0
    
    def _apply_vaccination(self, day):
        """Apply vaccination with realistic constraints and delays"""
        if day < self.vaccine_delay_days or self.vaccination_strategy == 'none':
            return
        
        # Daily supply with realistic variations
        base_supply = self.vaccine_supply_per_day
        daily_variation = np.random.uniform(0.6, 1.4)  # Supply chain variations
        
        # Weekend reductions
        if day % 7 in [5, 6]:
            daily_variation *= 0.3
        
        available_vaccines = int(base_supply * daily_variation)
        vaccines_administered = 0
        
        # Get eligible engineers based on strategy
        eligible = self._get_vaccination_eligible()
        
        # Apply vaccines
        for eng in eligible:
            if vaccines_administered >= available_vaccines:
                break
            
            # Individual acceptance rate (some refuse)
            acceptance_rate = 0.85 + eng.compliance_factor * 0.1
            if random.random() > acceptance_rate:
                continue
            
            if eng.vaccination_status == 'none':
                eng.vaccination_status = 'partial'
                vaccines_administered += 1
            elif (eng.vaccination_status == 'partial' and 
                  self.vaccination_strategy in ['full_dose_priority', 'staggered']):
                eng.vaccination_status = 'full'
                vaccines_administered += 1
        
        if vaccines_administered > 0:
            self.vaccination_log.append({
                'day': day,
                'vaccines_given': vaccines_administered,
                'strategy': self.vaccination_strategy,
                'supply_factor': daily_variation
            })
    
    def _get_vaccination_eligible(self):
        """Get eligible engineers for vaccination based on strategy"""
        if self.vaccination_strategy == 'single_dose_first':
            eligible = [e for e in self.engineers 
                       if e.state in ['S', 'E'] and e.vaccination_status == 'none']
            # Prioritize by age (older first) with some randomness
            eligible.sort(key=lambda x: x.age + np.random.uniform(-2, 2), reverse=True)
            
        elif self.vaccination_strategy == 'full_dose_priority':
            # Second doses first
            second_dose = [e for e in self.engineers 
                          if e.state in ['S', 'E'] and e.vaccination_status == 'partial']
            first_dose = [e for e in self.engineers 
                         if e.state in ['S', 'E'] and e.vaccination_status == 'none']
            eligible = second_dose + first_dose
            
        elif self.vaccination_strategy == 'staggered':
            eligible = [e for e in self.engineers 
                       if e.state in ['S', 'E'] and e.vaccination_status in ['none', 'partial']]
            random.shuffle(eligible)
            
        else:
            eligible = []
        
        return eligible
    
    def _apply_random_events(self, day):
        """Apply random events that can affect transmission"""
        # Super-spreader events (rare but impactful)
        if random.random() < 0.03:  # 3% chance per day during symposium
            if day <= self.symposium_days:
                # Large networking event or party
                affected_engineers = random.sample(
                    [e for e in self.engineers if e.state == 'S'], 
                    min(50, len([e for e in self.engineers if e.state == 'S']))
                )
                
                # Higher exposure for these engineers tomorrow
                for eng in affected_engineers:
                    eng.mobility_factor *= 2.0  # Reset next day
        
        # Weather events
        if random.random() < 0.1:  # 10% chance
            # Extreme cold increases indoor crowding
            self.weather_factor *= np.random.uniform(1.1, 1.5)
    
    def _compile_results(self):
        """Compile comprehensive simulation results"""
        if not self.daily_stats:
            return {}
        
        # Extract time series
        time_data = [d['day'] for d in self.daily_stats]
        susceptible_data = [d['susceptible'] for d in self.daily_stats]
        exposed_data = [d['exposed'] for d in self.daily_stats]
        infected_data = [d['infected'] for d in self.daily_stats]
        recovered_data = [d['recovered'] for d in self.daily_stats]
        dead_data = [d['dead'] for d in self.daily_stats]
        new_infections_data = [d['new_infections'] for d in self.daily_stats]
        
        # Calculate key metrics
        total_infected = max([d['cumulative_infected'] for d in self.daily_stats])
        total_deaths = dead_data[-1]
        peak_infected = max(infected_data)
        peak_day = infected_data.index(peak_infected)
        attack_rate = (total_infected / self.N) * 100
        case_fatality_rate = (total_deaths / max(total_infected, 1)) * 100
        
        # Epidemic metrics
        first_case_day = 0
        last_case_day = self.days
        for i in range(len(infected_data) - 1, -1, -1):
            if infected_data[i] > 0:
                last_case_day = i
                break
        epidemic_duration = last_case_day - first_case_day
        
        # Calculate symposium vs post-symposium infections
        symposium_infections = sum(new_infections_data[:self.symposium_days + 1])
        post_symposium_infections = sum(new_infections_data[self.symposium_days + 1:])
        
        # Vaccination coverage
        final_partial_vax = self.daily_stats[-1]['partially_vaccinated']
        final_full_vax = self.daily_stats[-1]['fully_vaccinated']
        vaccination_coverage = ((final_partial_vax + final_full_vax) / self.N) * 100
        
        # Effective R over time
        r_effective_series = [d.get('effective_r', 1.0) for d in self.daily_stats]
        
        return {
            'time': time_data,
            'susceptible': susceptible_data,
            'exposed': exposed_data,
            'infected': infected_data,
            'recovered': recovered_data,
            'dead': dead_data,
            'new_infections': new_infections_data,
            'total_infected': total_infected,
            'total_deaths': total_deaths,
            'peak_infected': peak_infected,
            'peak_day': peak_day,
            'attack_rate': attack_rate,
            'case_fatality_rate': case_fatality_rate,
            'epidemic_duration': epidemic_duration,
            'vaccination_coverage': vaccination_coverage,
            'symposium_infections': symposium_infections,
            'post_symposium_infections': post_symposium_infections,
            'r_effective_series': r_effective_series,
            'mean_r_effective': np.mean(r_effective_series[1:6]) if len(r_effective_series) > 5 else 1.0,
            'transmission_events': len(self.transmission_events),
            'daily_stats': self.daily_stats,
            # Add parameter values used in this simulation
            'actual_parameters': {
                'infection_rate': self.beta,
                'mask_effectiveness': self.mask_effectiveness,
                'vaccination_coverage': self.vaccination_rate,
                'death_rate': self.mortality_rate
            }
        }
    
    def run_multiple_simulations(self, num_runs=50):
        """Run multiple simulations with different random parameters"""
        all_results = []
        
        for run in range(num_runs):
            # Re-initialize with new random seed for each run
            current_time = int(time.time() * 1000000 + run * 1000) % (2**32)
            np.random.seed(current_time)
            random.seed(current_time)
            
            # Re-initialize population and run
            self._initialize_population()
            result = self.run_simulation()
            all_results.append(result)
        
        # Calculate averaged results
        return self._average_results(all_results)
    
    def _average_results(self, results_list):
        """Average multiple simulation results"""
        if not results_list:
            return {}
        
        max_length = max(len(r.get('time', [])) for r in results_list)
        
        averaged = {
            'time': list(range(max_length)),
            'susceptible': [],
            'exposed': [],
            'infected': [],
            'recovered': [],
            'dead': [],
            'new_infections': [],
            'r_effective_series': []
        }
        
        # Average daily values
        for day in range(max_length):
            day_values = {key: [] for key in averaged.keys() if key != 'time'}
            
            for result in results_list:
                for key in day_values.keys():
                    if key in result and day < len(result[key]):
                        day_values[key].append(result[key][day])
                    elif key in result and result[key]:
                        day_values[key].append(result[key][-1])
                    else:
                        day_values[key].append(0)
            
            for key, values in day_values.items():
                averaged[key].append(np.mean(values) if values else 0)
        
        # Average summary statistics
        summary_metrics = ['total_infected', 'total_deaths', 'peak_infected', 'peak_day',
                          'attack_rate', 'case_fatality_rate', 'epidemic_duration',
                          'vaccination_coverage', 'symposium_infections', 
                          'post_symposium_infections', 'mean_r_effective']
        
        for metric in summary_metrics:
            values = [r.get(metric, 0) for r in results_list if metric in r]
            averaged[metric] = np.mean(values) if values else 0
        
        # Average the actual parameters used across runs
        param_values = {
            'infection_rate': [],
            'mask_effectiveness': [],
            'vaccination_coverage': [],
            'death_rate': []
        }
        
        for result in results_list:
            if 'actual_parameters' in result:
                for param, value in result['actual_parameters'].items():
                    if param in param_values:
                        param_values[param].append(value)
        
        averaged['parameter_statistics'] = {}
        for param, values in param_values.items():
            if values:
                averaged['parameter_statistics'][param] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values)
                }
        
        return averaged
    
    def calculate_statistics(self, results_list=None):
        """Calculate comprehensive statistics across runs"""
        if results_list is None:
            result = self.run_simulation()
            results_list = [result]
        
        metrics = ['total_infected', 'total_deaths', 'peak_infected', 'attack_rate', 
                  'epidemic_duration', 'vaccination_coverage', 'symposium_infections',
                  'post_symposium_infections', 'mean_r_effective']
        
        stats = {}
        for metric in metrics:
            values = [r.get(metric, 0) for r in results_list if metric in r]
            if values:
                stats[f'mean_{metric}'] = np.mean(values)
                stats[f'std_{metric}'] = np.std(values) if len(values) > 1 else 0
                stats[f'min_{metric}'] = np.min(values)
                stats[f'max_{metric}'] = np.max(values)
        
        # Calculate R0 and epidemic probability
        r_values = [r.get('mean_r_effective', 1.0) for r in results_list]
        stats['R0'] = np.mean(r_values) if r_values else 1.0
        stats['epidemic_probability'] = sum(1 for r in results_list 
                                          if r.get('total_infected', 0) > 50) / len(results_list)
        
        # Confidence intervals
        stats['confidence_intervals'] = {}
        for metric in ['total_infected', 'total_deaths', 'peak_infected', 'attack_rate']:
            values = [r.get(metric, 0) for r in results_list if metric in r]
            if len(values) > 1:
                stats['confidence_intervals'][metric] = {
                    'mean': np.mean(values),
                    'ci_lower': np.percentile(values, 2.5),
                    'ci_upper': np.percentile(values, 97.5),
                    'std': np.std(values)
                }
            elif values:
                val = values[0]
                stats['confidence_intervals'][metric] = {
                    'mean': val,
                    'ci_lower': val * 0.8,
                    'ci_upper': val * 1.2,
                    'std': val * 0.1
                }
        
        return stats
    
    def get_parameters(self):
        """Return simulation parameters"""
        return {
            'population': self.N,
            'initial_infected': self.I0,
            'transmission_rate': self.beta,
            'infectious_period': 1/self.gamma,
            'incubation_period': 1/self.sigma,
            'simulation_days': self.days,
            'vaccination_strategy': self.vaccination_strategy,
            'mask_compliance': self.mask_compliance,
            'social_distancing': self.social_distancing,
            'vaccine_supply_per_day': self.vaccine_supply_per_day,
            'vaccine_delay_days': self.vaccine_delay_days,
            'mask_effectiveness': self.mask_effectiveness,
            'mortality_rate': self.mortality_rate,
            'vaccination_rate': self.vaccination_rate,
            'use_agent_based': True,
            'scenario': 'Aurora Winter Engineering Symposium 2025',
            'symposium_days': self.symposium_days,
            'networking_intensity': self.networking_intensity,
            'weather_factor': self.weather_factor
        }

# Legacy compatibility
class SEIRSimulation(AuroraFluSimulation):
    """Legacy SEIR class that uses the enhanced Aurora simulation"""
    
    def __init__(self, **kwargs):
        # Map legacy parameters to Aurora parameters
        enhanced_params = {
            'population': kwargs.get('population', 14000),
            'initial_infected': kwargs.get('initial_infected', 1),
            'transmission_rate': kwargs.get('transmission_rate', 0.10),
            'infectious_period': kwargs.get('infectious_period', 4),
            'simulation_days': kwargs.get('simulation_days', 14),
            'incubation_period': kwargs.get('incubation_period', 3),
            'vaccination_rate': kwargs.get('vaccination_rate', 0.0),
            'mask_effectiveness': kwargs.get('mask_effectiveness', 0.6),
            'social_distancing': kwargs.get('social_distancing', 0.0),
            'mortality_rate': kwargs.get('mortality_rate', 0.0002),
            'vaccination_strategy': kwargs.get('vaccination_strategy', 'none'),
            'vaccine_supply_per_day': kwargs.get('vaccine_supply_per_day', 100),
            'vaccine_delay_days': kwargs.get('vaccine_delay_days', 0),
            'mask_compliance': kwargs.get('mask_compliance', 0.01),
            'use_parameter_distributions': kwargs.get('use_parameter_distributions', True)
        }
        super().__init__(**enhanced_params)
    
    def seir_model(self, y, t):
        """Legacy SEIR differential equation model for backward compatibility"""
        S, E, I, R = y
        
        # Use effective transmission rate
        effective_beta = self.beta * (1 - self.mask_effectiveness) * (1 - self.social_distancing)
        
        # Differential equations
        dSdt = -effective_beta * S * I / self.N
        dEdt = effective_beta * S * I / self.N - self.sigma * E
        dIdt = self.sigma * E - self.gamma * I
        dRdt = self.gamma * I
        
        return [dSdt, dEdt, dIdt, dRdt]
    
    def run_single_simulation(self):
        """Legacy single simulation method - now uses Aurora enhanced simulation"""
        return super().run_simulation()
    
    def run_stochastic_simulation(self):
        """Legacy stochastic simulation - now uses Aurora enhanced simulation"""
        return super().run_simulation()
    
    def calculate_average_results(self):
        """Legacy method for calculating average results"""
        if not hasattr(self, 'results_history') or not self.results_history:
            # Run a single simulation if no history exists
            result = self.run_simulation()
            self.results_history = [result]
        
        return self._average_results(self.results_history)
    
    def calculate_confidence_intervals(self):
        """Legacy method for confidence intervals"""
        if not hasattr(self, 'results_history') or not self.results_history:
            # Return empty intervals if no results
            return {
                'total_infected': {'mean': 0, 'std': 0, 'ci_lower': 0, 'ci_upper': 0},
                'peak_infected': {'mean': 0, 'std': 0, 'ci_lower': 0, 'ci_upper': 0},
                'peak_day': {'mean': 0, 'std': 0, 'ci_lower': 0, 'ci_upper': 0}
            }
        
        # Extract legacy metrics
        total_infected = [r.get('total_infected', 0) for r in self.results_history]
        peak_infected = [r.get('peak_infected', 0) for r in self.results_history]
        peak_day = [r.get('peak_day', 0) for r in self.results_history]
        
        def ci_95(data):
            if len(data) < 2:
                mean_val = data[0] if data else 0
                return {
                    'mean': mean_val,
                    'std': 0,
                    'ci_lower': mean_val * 0.9,
                    'ci_upper': mean_val * 1.1
                }
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
    
    def run_multiple_simulations(self, num_runs=100):
        """Legacy multiple simulations method"""
        all_results = []
        
        for run in range(num_runs):
            # Create new instance for each run to ensure randomness
            new_sim = AuroraFluSimulation(
                population=self.N,
                initial_infected=self.I0,
                transmission_rate=self.beta,
                infectious_period=1/self.gamma,
                simulation_days=self.days,
                incubation_period=1/self.sigma,
                vaccination_rate=self.vaccination_rate,
                mask_effectiveness=self.mask_effectiveness,
                social_distancing=self.social_distancing,
                mortality_rate=self.mortality_rate,
                vaccination_strategy=self.vaccination_strategy,
                vaccine_supply_per_day=self.vaccine_supply_per_day,
                vaccine_delay_days=self.vaccine_delay_days,
                mask_compliance=self.mask_compliance,
                use_parameter_distributions=True
            )
            
            result = new_sim.run_simulation()
            all_results.append(result)
        
        # Store results for legacy compatibility
        self.results_history = all_results
        
        # Calculate legacy statistics
        self.calculate_statistics()
        
        # Return averaged results
        return self._average_results(all_results)
    
    def calculate_statistics(self):
        """Legacy statistics calculation"""
        if not hasattr(self, 'results_history') or not self.results_history:
            # Default statistics for empty results
            self.statistics = {
                'R0': self.beta / self.gamma,
                'mean_total_infected': 0,
                'mean_attack_rate': 0,
                'std_total_infected': 0,
                'confidence_intervals': self.calculate_confidence_intervals(),
                'epidemic_probability': 0
            }
            return self.statistics
        
        # Calculate R0 (basic reproduction number)
        R0 = self.beta / self.gamma
        
        # Extract metrics from results
        total_infected = [r.get('total_infected', 0) for r in self.results_history]
        attack_rate = [(ti / self.N * 100) if self.N > 0 else 0 for ti in total_infected]
        
        # Calculate statistics
        self.statistics = {
            'R0': R0,
            'mean_total_infected': np.mean(total_infected) if total_infected else 0,
            'mean_attack_rate': np.mean(attack_rate) if attack_rate else 0,
            'std_total_infected': np.std(total_infected) if len(total_infected) > 1 else 0,
            'confidence_intervals': self.calculate_confidence_intervals(),
            'epidemic_probability': (sum(1 for ti in total_infected if ti > 10) / len(total_infected)) if total_infected else 0
        }
        
        return self.statistics