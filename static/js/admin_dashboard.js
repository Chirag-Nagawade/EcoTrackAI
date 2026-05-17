document.addEventListener('DOMContentLoaded', function () {
    // Fetch Model Metrics
    fetch('/api/dashboard_data')
        .then(res => res.json())
        .then(data => {
            if (data.metrics && data.metrics.length > 0) {
                renderModelComparison(data.metrics);
                renderErrorComparison(data.metrics);
                renderMetricsTable(data.metrics);
            }
            if (data.feature_importance && data.feature_importance.length > 0) {
                renderFeatureImportance(data.feature_importance);
            }
        })
        .catch(err => console.error('Admin Dashboard fetch error:', err));

    // Fetch Recent Users Data
    fetch('/api/admin/users_data')
        .then(res => res.json())
        .then(data => {
            renderUsersTable(data);
        })
        .catch(err => console.error('Admin Users Data fetch error:', err));
});

/* ===== Model Comparison Bar Chart (R² Score) ===== */
function renderModelComparison(metrics) {
    const ctx = document.getElementById('modelComparisonChart').getContext('2d');
    const labels = metrics.map(m => m.Model);
    const r2Scores = metrics.map(m => m['R2 Score']);

    const colors = ['rgba(59, 130, 246, 0.8)', 'rgba(245, 158, 11, 0.8)', 'rgba(16, 185, 129, 0.8)', 'rgba(239, 68, 68, 0.8)'];
    const borderColors = ['rgba(59, 130, 246, 1)', 'rgba(245, 158, 11, 1)', 'rgba(16, 185, 129, 1)', 'rgba(239, 68, 68, 1)'];

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{ label: 'R² Score', data: r2Scores, backgroundColor: colors, borderColor: borderColors, borderWidth: 2, borderRadius: 8, barPercentage: 0.6 }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false }, tooltip: { backgroundColor: 'rgba(15, 25, 35, 0.9)', titleColor: '#e2e8f0', bodyColor: '#94a3b8', cornerRadius: 8 } },
            scales: { y: { beginAtZero: true, max: 1, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }, x: { grid: { display: false }, ticks: { color: '#94a3b8', maxRotation: 15 } } }
        }
    });
}

/* ===== Feature Importance Chart ===== */
function renderFeatureImportance(features) {
    const ctx = document.getElementById('featureImportanceChart').getContext('2d');
    const labels = features.map(f => f.Feature);
    const values = features.map(f => f.Importance);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{ label: 'Importance', data: values, backgroundColor: 'rgba(16, 185, 129, 0.6)', borderColor: 'rgba(16, 185, 129, 1)', borderWidth: 1, borderRadius: 6, barPercentage: 0.7 }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            plugins: { legend: { display: false }, tooltip: { backgroundColor: 'rgba(15, 25, 35, 0.9)', titleColor: '#e2e8f0', bodyColor: '#94a3b8', cornerRadius: 8 } },
            scales: { x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }, y: { grid: { display: false }, ticks: { color: '#94a3b8', font: { size: 11 } } } }
        }
    });
}

/* ===== Error Comparison (MAE & RMSE) ===== */
function renderErrorComparison(metrics) {
    const ctx = document.getElementById('errorComparisonChart').getContext('2d');
    const labels = metrics.map(m => m.Model);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                { label: 'MAE', data: metrics.map(m => m.MAE), backgroundColor: 'rgba(59, 130, 246, 0.7)', borderColor: 'rgba(59, 130, 246, 1)', borderWidth: 1, borderRadius: 6, barPercentage: 0.5 },
                { label: 'RMSE', data: metrics.map(m => m.RMSE), backgroundColor: 'rgba(239, 68, 68, 0.7)', borderColor: 'rgba(239, 68, 68, 1)', borderWidth: 1, borderRadius: 6, barPercentage: 0.5 }
            ]
        },
        options: {
            responsive: true,
            plugins: { legend: { labels: { color: '#94a3b8', padding: 15 } }, tooltip: { backgroundColor: 'rgba(15, 25, 35, 0.9)', titleColor: '#e2e8f0', bodyColor: '#94a3b8', cornerRadius: 8 } },
            scales: { y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }, x: { grid: { display: false }, ticks: { color: '#94a3b8', maxRotation: 15 } } }
        }
    });
}

/* ===== Metrics Table ===== */
function renderMetricsTable(metrics) {
    const tbody = document.querySelector('#metricsTable tbody');
    tbody.innerHTML = '';

    metrics.forEach(m => {
        const r2Color = m['R2 Score'] >= 0.9 ? 'text-success' : m['R2 Score'] >= 0.7 ? 'text-warning' : 'text-danger';
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

/* ===== Recent Users Table ===== */
function renderUsersTable(usersData) {
    const tbody = document.querySelector('#usersTable tbody');
    tbody.innerHTML = '';

    if (!usersData || usersData.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted py-4">No recent predictions found.</td></tr>`;
        return;
    }

    usersData.forEach(user => {
        let levelBadge = '';
        if (user.carbon_level === 'LOW') {
            levelBadge = `<span class="badge bg-success rounded-pill px-3">LOW</span>`;
        } else if (user.carbon_level === 'MEDIUM') {
            levelBadge = `<span class="badge bg-warning text-dark rounded-pill px-3">MEDIUM</span>`;
        } else {
            levelBadge = `<span class="badge bg-danger rounded-pill px-3">HIGH</span>`;
        }

        const row = `
            <tr>
                <td>${user.timestamp}</td>
                <td class="fw-bold">${user.username}</td>
                <td>${user.predicted_carbon}</td>
                <td>${levelBadge}</td>
            </tr>`;
        tbody.insertAdjacentHTML('beforeend', row);
    });
}
