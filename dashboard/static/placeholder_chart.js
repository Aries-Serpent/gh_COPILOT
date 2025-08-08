document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('placeholderChart');
    if (!canvas || typeof Chart === 'undefined') {
        return;
    }
    const ctx = canvas.getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Placeholders',
                data: [],
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    function update(history) {
        chart.data.labels = history.map(h => h.date);
        chart.data.datasets[0].data = history.map(h => h.count);
        chart.update();
    }

    window.updatePlaceholderChart = update;

    fetch('/metrics').then(r => r.json()).then(data => {
        update(data.placeholder_history || []);
    });
});
