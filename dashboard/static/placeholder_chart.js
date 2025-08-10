document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('placeholderChart');
    const tableBody = document.getElementById('unresolvedBody');
    const openCount = document.getElementById('placeholderOpenCount');
    const resolvedCount = document.getElementById('placeholderResolvedCount');
    if (!canvas || typeof Chart === 'undefined') {
        return;
    }
    const ctx = canvas.getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Open',
                    data: [],
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)'
                },
                {
                    label: 'Resolved',
                    data: [],
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)'
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    function refresh() {
        fetch('/api/placeholder_audit').then(r => r.json()).then(data => {
            const history = data.history || [];
            chart.data.labels = history.map(h => new Date(h.timestamp * 1000).toLocaleString());
            chart.data.datasets[0].data = history.map(h => h.open);
            chart.data.datasets[1].data = history.map(h => h.resolved);
            chart.update();
            if (history.length && openCount && resolvedCount) {
                const latest = history[history.length - 1];
                openCount.textContent = latest.open;
                resolvedCount.textContent = latest.resolved;
            }
            if (tableBody) {
                tableBody.innerHTML = '';
                (data.unresolved || []).forEach(row => {
                    const tr = document.createElement('tr');
                    const fileTd = document.createElement('td');
                    fileTd.textContent = row.file;
                    const lineTd = document.createElement('td');
                    lineTd.textContent = row.line;
                    const typeTd = document.createElement('td');
                    typeTd.textContent = row.type;
                    tr.appendChild(fileTd);
                    tr.appendChild(lineTd);
                    tr.appendChild(typeTd);
                    if (row.context) {
                        tr.title = row.context;
                    }
                    tableBody.appendChild(tr);
                });
            }
        });
    }

    refresh();
    setInterval(refresh, 5000);
});
