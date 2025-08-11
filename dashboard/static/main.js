document.addEventListener('DOMContentLoaded', () => {
    console.log('Dashboard assets loaded');
    const details = document.getElementById('metric-details');
    document.querySelectorAll('#score_gauges canvas').forEach((canvas) => {
        canvas.addEventListener('click', () => {
            const id = canvas.dataset.metric;
            const target = document.getElementById(id);
            if (!target) return;
            details.textContent = `${target.title} Current value: ${target.textContent}`;
            details.removeAttribute('hidden');
        });
    });
});

