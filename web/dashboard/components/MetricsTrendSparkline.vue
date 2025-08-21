<template>
  <canvas ref="canvas" width="100" height="30"></canvas>
</template>

<script>
export default {
  name: 'MetricsTrendSparkline',
  mounted() {
    Promise.all([
      fetch('/metrics/trend').then(r => r.json()),
      fetch('/api/thresholds').then(r => r.json()),
    ]).then(([d, t]) => {
      const data = d.metrics || [];
      const labels = d.timestamps || [];
      const latest = data[data.length - 1] || 0;
      const bounds = t.composite_score || {};
      let color = '#2ecc71';
      if (bounds.critical !== undefined && latest < bounds.critical) {
        color = '#e74c3c';
      } else if (bounds.warning !== undefined && latest < bounds.warning) {
        color = '#f1c40f';
      }
      /* global Chart */
      new Chart(this.$refs.canvas.getContext('2d'), {
        type: 'line',
        data: {
          labels,
          datasets: [{
            data,
            borderColor: color,
            fill: false,
            tension: 0.3,
          }],
        },
        options: {
          plugins: { legend: { display: false } },
          scales: { x: { display: false }, y: { display: false } },
          elements: { point: { radius: 0 } },
        },
      });
    });
  },
};
</script>
