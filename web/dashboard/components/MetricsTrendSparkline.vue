<template>
  <canvas ref="canvas" width="100" height="30"></canvas>
</template>

<script>
export default {
  name: 'MetricsTrendSparkline',
  mounted() {
    fetch('/api/metrics/trend')
      .then(r => r.json())
      .then(d => {
        const data = d.metrics || [];
        const labels = d.timestamps || [];
        /* global Chart */
        new Chart(this.$refs.canvas.getContext('2d'), {
          type: 'line',
          data: {
            labels,
            datasets: [{
              data,
              borderColor: '#e74c3c',
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
