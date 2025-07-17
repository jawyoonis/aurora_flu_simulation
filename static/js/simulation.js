let currentResults = null;

function getFormData() {
    return {
        population: parseInt(document.getElementById('population').value),
        initial_infected: parseInt(document.getElementById('initial_infected').value),
        transmission_rate: parseFloat(document.getElementById('transmission_rate').value),
        infectious_period: parseInt(document.getElementById('infectious_period').value),
        incubation_period: parseInt(document.getElementById('incubation_period').value),
        simulation_days: parseInt(document.getElementById('simulation_days').value),
        num_runs: parseInt(document.getElementById('num_runs').value),
        vaccination_rate: parseFloat(document.getElementById('vaccination_rate').value),
        mask_effectiveness: parseFloat(document.getElementById('mask_effectiveness').value),
        social_distancing: parseFloat(document.getElementById('social_distancing').value)
    };
}

function showLoading() {
    const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
    modal.show();
}

function hideLoading() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
    if (modal) modal.hide();
}

function runSimulation() {
    const formData = getFormData();
    showLoading();
    
    fetch('/run_simulation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            currentResults = data;
            plotResults(data.results);
            displayStatistics(data.statistics);
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
        alert('Error running simulation');
    });
}

function plotResults(results) {
    const traces = [
        {
            x: results.time,
            y: results.susceptible,
            name: 'Susceptible',
            type: 'scatter',
            mode: 'lines',
            line: { color: '#28a745', width: 2 }
        },
        {
            x: results.time,
            y: results.exposed,
            name: 'Exposed',
            type: 'scatter',
            mode: 'lines',
            line: { color: '#ffc107', width: 2 }
        },
        {
            x: results.time,
            y: results.infected,
            name: 'Infected',
            type: 'scatter',
            mode: 'lines',
            line: { color: '#dc3545', width: 2 }
        },
        {
            x: results.time,
            y: results.recovered,
            name: 'Recovered',
            type: 'scatter',
            mode: 'lines',
            line: { color: '#6f42c1', width: 2 }
        }
    ];
    
    const layout = {
        title: 'SEIR Model - Disease Progression Over Time',
        xaxis: { title: 'Days' },
        yaxis: { title: 'Number of People' },
        hovermode: 'x unified',
        showlegend: true,
        margin: { t: 50, r: 30, b: 50, l: 60 }
    };
    
    Plotly.newPlot('plotContainer', traces, layout, {responsive: true});
}

function displayStatistics(stats) {
    const panel = document.getElementById('statisticsPanel');
    
    const html = `
        <div class="statistics-item">
            <span class="statistics-label">R₀ (Basic Reproduction Number):</span>
            <span class="statistics-value">${stats.R0.toFixed(2)}</span>
        </div>
        <div class="statistics-item">
            <span class="statistics-label">Mean Total Infected:</span>
            <span class="statistics-value">${Math.round(stats.mean_total_infected)}</span>
        </div>
        <div class="statistics-item">
            <span class="statistics-label">Attack Rate:</span>
            <span class="statistics-value">${stats.mean_attack_rate.toFixed(1)}%</span>
        </div>
        <div class="statistics-item">
            <span class="statistics-label">Epidemic Probability:</span>
            <span class="statistics-value">${(stats.epidemic_probability * 100).toFixed(1)}%</span>
        </div>
        <hr>
        <h6>95% Confidence Intervals</h6>
        <div class="statistics-item">
            <span class="statistics-label">Total Infected:</span>
            <span class="statistics-value">
                ${Math.round(stats.confidence_intervals.total_infected.ci_lower)} - 
                ${Math.round(stats.confidence_intervals.total_infected.ci_upper)}
            </span>
        </div>
        <div class="statistics-item">
            <span class="statistics-label">Peak Infected:</span>
            <span class="statistics-value">
                ${Math.round(stats.confidence_intervals.peak_infected.ci_lower)} - 
                ${Math.round(stats.confidence_intervals.peak_infected.ci_upper)}
            </span>
        </div>
    `;
    
    panel.innerHTML = html;
}

function compareScenarios() {
    const baseParams = getFormData();
    
    const scenarios = {
        'Baseline': baseParams,
        'With Masks (50% effective)': {
            ...baseParams,
            mask_effectiveness: 0.5
        },
        'With Vaccination (30%)': {
            ...baseParams,
            vaccination_rate: 0.3
        },
        'Combined Interventions': {
            ...baseParams,
            mask_effectiveness: 0.5,
            vaccination_rate: 0.3,
            social_distancing: 0.3
        }
    };
    
    showLoading();
    
    fetch('/compare_scenarios', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({scenarios: scenarios})
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            plotComparison(data.comparison_results);
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
        alert('Error running comparison');
    });
}

function plotComparison(comparisonResults) {
    const colors = ['#dc3545', '#28a745', '#ffc107', '#6f42c1'];
    const traces = [];
    
    let colorIndex = 0;
    for (const [scenarioName, scenarioData] of Object.entries(comparisonResults)) {
        traces.push({
            x: scenarioData.results.time,
            y: scenarioData.results.infected,
            name: scenarioName,
            type: 'scatter',
            mode: 'lines',
            line: { color: colors[colorIndex % colors.length], width: 2 }
        });
        colorIndex++;
    }
    
    const layout = {
        title: 'Scenario Comparison - Infected Population',
        xaxis: { title: 'Days' },
        yaxis: { title: 'Number of Infected People' },
        hovermode: 'x unified',
        showlegend: true,
        margin: { t: 50, r: 30, b: 50, l: 60 }
    };
    
    Plotly.newPlot('comparisonContainer', traces, layout, {responsive: true});
}

// Initialize with default simulation on page load
document.addEventListener('DOMContentLoaded', function() {
    // You can uncomment the line below to run a default simulation on page load
    // runSimulation();
});