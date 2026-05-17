document.addEventListener('DOMContentLoaded', function () {
    fetch('/api/dashboard_data')
        .then(res => res.json())
        .then(data => {
            renderStats(data);
            renderWeeklyGraph(data.weekly_data);
            renderLevelPieChart(data.levels);
            renderImpactBreakdown(data.impact_breakdown);
        })
        .catch(err => console.error('Dashboard fetch error:', err));
});

/* ===== Stat Cards ===== */
function renderStats(data) {
    document.getElementById('totalPredictions').textContent = data.total_predictions || 0;

    const levels = data.levels || [];
    let low = 0, medium = 0, high = 0;
    levels.forEach(l => {
        if (l._id === 'LOW') low = l.count;
        else if (l._id === 'MEDIUM') medium = l.count;
        else if (l._id === 'HIGH') high = l.count;
    });
    document.getElementById('lowCount').textContent = low;
    document.getElementById('mediumCount').textContent = medium;
    document.getElementById('highCount').textContent = high;
}

/* ===== Weekly Graph ===== */
function renderWeeklyGraph(weeklyData) {
    if (!weeklyData || weeklyData.length === 0) return;
    
    const ctx = document.getElementById('weeklyGraphChart').getContext('2d');
    const labels = weeklyData.map(d => d._id);
    const data = weeklyData.map(d => d.total_carbon);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Total Footprint (kg CO₂)',
                data: data,
                borderColor: 'rgba(16, 185, 129, 1)',
                backgroundColor: 'rgba(16, 185, 129, 0.2)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: 'rgba(16, 185, 129, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(15, 25, 35, 0.9)',
                    titleColor: '#e2e8f0',
                    bodyColor: '#94a3b8',
                    cornerRadius: 8
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8' }
                }
            }
        }
    });
}

/* ===== Model Comparison Bar Chart (R² Score) ===== */
function renderModelComparison(metrics) {
    if (!metrics || metrics.length === 0) return;

    const ctx = document.getElementById('modelComparisonChart').getContext('2d');
    const labels = metrics.map(m => m.Model);
    const r2Scores = metrics.map(m => m['R2 Score']);

    const colors = [
        'rgba(59, 130, 246, 0.8)',   // blue
        'rgba(245, 158, 11, 0.8)',   // amber
        'rgba(16, 185, 129, 0.8)',   // green
        'rgba(239, 68, 68, 0.8)'     // red
    ];
    const borderColors = [
        'rgba(59, 130, 246, 1)',
        'rgba(245, 158, 11, 1)',
        'rgba(16, 185, 129, 1)',
        'rgba(239, 68, 68, 1)'
    ];

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'R² Score',
                data: r2Scores,
                backgroundColor: colors,
                borderColor: borderColors,
                borderWidth: 2,
                borderRadius: 8,
                barPercentage: 0.6
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(15, 25, 35, 0.9)',
                    titleColor: '#e2e8f0',
                    bodyColor: '#94a3b8',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    cornerRadius: 8
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8', maxRotation: 15 }
                }
            }
        }
    });
}

/* ===== Pie Chart - Level Distribution ===== */
function renderLevelPieChart(levels) {
    const ctx = document.getElementById('levelPieChart').getContext('2d');

    let low = 0, medium = 0, high = 0;
    (levels || []).forEach(l => {
        if (l._id === 'LOW') low = l.count;
        else if (l._id === 'MEDIUM') medium = l.count;
        else if (l._id === 'HIGH') high = l.count;
    });

    // If no data, show placeholder
    if (low + medium + high === 0) {
        low = 1; medium = 1; high = 1;
    }

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['LOW', 'MEDIUM', 'HIGH'],
            datasets: [{
                data: [low, medium, high],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(239, 68, 68, 0.8)'
                ],
                borderColor: [
                    'rgba(16, 185, 129, 1)',
                    'rgba(245, 158, 11, 1)',
                    'rgba(239, 68, 68, 1)'
                ],
                borderWidth: 2,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#94a3b8', padding: 20, font: { size: 13 } }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 25, 35, 0.9)',
                    titleColor: '#e2e8f0',
                    bodyColor: '#94a3b8',
                    cornerRadius: 8
                }
            }
        }
    });
}

/* ===== Impact Breakdown Chart ===== */
function renderImpactBreakdown(breakdownData) {
    if (!breakdownData || breakdownData.length === 0) return;
    
    const ctx = document.getElementById('impactBreakdownChart').getContext('2d');
    const labels = breakdownData.map(d => d.category);
    const data = breakdownData.map(d => d.impact);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Carbon Impact (kg CO₂)',
                data: data,
                backgroundColor: [
                    'rgba(59, 130, 246, 0.8)',   // Transport (Blue)
                    'rgba(245, 158, 11, 0.8)',   // Electricity (Yellow)
                    'rgba(16, 185, 129, 0.8)',   // Diet (Green)
                    'rgba(239, 68, 68, 0.8)',    // Waste (Red)
                    'rgba(168, 85, 247, 0.8)'    // Screen Time (Purple)
                ],
                borderColor: [
                    'rgba(59, 130, 246, 1)',
                    'rgba(245, 158, 11, 1)',
                    'rgba(16, 185, 129, 1)',
                    'rgba(239, 68, 68, 1)',
                    'rgba(168, 85, 247, 1)'
                ],
                borderWidth: 2,
                borderRadius: 6
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: { backgroundColor: 'rgba(15, 25, 35, 0.9)', titleColor: '#e2e8f0', bodyColor: '#94a3b8', cornerRadius: 8 }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8', font: { size: 12 } }
                }
            }
        }
    });
}

/* ===== Feature Importance Chart ===== */
function renderFeatureImportance(features) {
    if (!features || features.length === 0) return;

    const ctx = document.getElementById('featureImportanceChart').getContext('2d');
    const labels = features.map(f => f.Feature);
    const values = features.map(f => f.Importance);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Importance',
                data: values,
                backgroundColor: 'rgba(16, 185, 129, 0.6)',
                borderColor: 'rgba(16, 185, 129, 1)',
                borderWidth: 1,
                borderRadius: 6,
                barPercentage: 0.7
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(15, 25, 35, 0.9)',
                    titleColor: '#e2e8f0',
                    bodyColor: '#94a3b8',
                    cornerRadius: 8
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8', font: { size: 11 } }
                }
            }
        }
    });
}

/* ===== Error Comparison (MAE & RMSE) ===== */
function renderErrorComparison(metrics) {
    if (!metrics || metrics.length === 0) return;

    const ctx = document.getElementById('errorComparisonChart').getContext('2d');
    const labels = metrics.map(m => m.Model);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'MAE',
                    data: metrics.map(m => m.MAE),
                    backgroundColor: 'rgba(59, 130, 246, 0.7)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 1,
                    borderRadius: 6,
                    barPercentage: 0.5
                },
                {
                    label: 'RMSE',
                    data: metrics.map(m => m.RMSE),
                    backgroundColor: 'rgba(239, 68, 68, 0.7)',
                    borderColor: 'rgba(239, 68, 68, 1)',
                    borderWidth: 1,
                    borderRadius: 6,
                    barPercentage: 0.5
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: { color: '#94a3b8', padding: 15 }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 25, 35, 0.9)',
                    titleColor: '#e2e8f0',
                    bodyColor: '#94a3b8',
                    cornerRadius: 8
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8', maxRotation: 15 }
                }
            }
        }
    });
}

/* ===== Metrics Table ===== */
function renderMetricsTable(metrics) {
    if (!metrics || metrics.length === 0) return;

    const tbody = document.querySelector('#metricsTable tbody');
    tbody.innerHTML = '';

    metrics.forEach(m => {
        const r2Color = m['R2 Score'] >= 0.9 ? 'text-success' :
                        m['R2 Score'] >= 0.7 ? 'text-warning' : 'text-danger';
        const row = `
            <tr>
                <td class="fw-bold">${m.Model}</td>
                <td>${m.MAE}</td>
                <td>${m.RMSE}</td>
                <td class="${r2Color} fw-bold">${m['R2 Score']}</td>
            </tr>`;
        tbody.insertAdjacentHTML('beforeend', row);
    });
}
