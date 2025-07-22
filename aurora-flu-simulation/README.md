# aurora_flu_simulation
# Aurora Flu Simulation - ANOVA Analysis

A comprehensive epidemiological simulation framework for analyzing intervention effectiveness during the Aurora Winter Engineering Symposium 2025.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the analysis:**
   ```bash
   python main.py
   ```

## What it does

The simulation analyzes 5 different intervention scenarios:
- **No Interventions** (baseline)
- **Masks Only** (70% effectiveness, 70% compliance)
- **Social Distancing Only** (70% contact reduction)
- **Vaccination Only** (10% rate, 7-day delay)
- **All Interventions Combined**

Each scenario runs multiple simulations and performs statistical ANOVA analysis to determine which interventions are most effective at reducing disease spread.

## Key Features

- **Agent-based simulation** with 15,000 individual engineers
- **Statistical analysis** using one-way ANOVA with post-hoc comparisons
- **Multiple metrics** including attack rate, peak infections, and total deaths
- **Realistic parameters** with random distributions for robustness
- **Comprehensive reporting** with effect sizes and confidence intervals

## Output

The analysis produces:
- Descriptive statistics for each intervention group
- ANOVA results with F-statistic and p-values
- Effect size calculations (eta-squared)
- Post-hoc pairwise comparisons
- Summary recommendations for policy decisions

## Requirements

- Python 3.7+
- NumPy, SciPy, and other scientific computing libraries (see requirements.txt)

## Project Structure

```
aurora-flu-simulation/
├── main.py                      # Main analysis script (runs all tests)
├── requirements.txt             # Python dependencies
├── scenarios_config.py          # Intervention scenario definitions
├── test_anova.py               # ANOVA statistical analysis tests
├── test_multiple_simulations.py # Multiple simulation runs and averaging
└── models/
    └── seir_model.py           # Core simulation engine with ANOVA methods
```

## Files Description

- **`main.py`** - Entry point that orchestrates all analysis components
- **`test_anova.py`** - Performs statistical ANOVA analysis comparing intervention effectiveness
- **`test_multiple_simulations.py`** - Runs multiple simulation instances for robust statistical analysis
- **`scenarios_config.py`** - Centralized configuration for all intervention scenarios with exact parameter specifications
- **`requirements.txt`** - Python package dependencies
- **`models/seir_model.py`** - Core epidemiological simulation engine with integrated ANOVA methods

## Individual Test Files

You can also run individual components:

```bash
# Run ANOVA analysis only by 
python test_anova.py

# Run multiple simulations analysis only
python test_multiple_simulations.py
```

---

*Run time: ~2-5 minutes depending on number of simulations per group*