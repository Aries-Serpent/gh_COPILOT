<template>
  <canvas ref="canvas" width="100" height="30"></canvas>
</template>

<script>
export default {
  name: 'CodeQualitySparkline',
  props: {
    metric: { type: String, default: 'composite_score' }
  },
  mounted() {
    fetch('/api/code_quality_history')
      .then(r => r.json())
      .then(d => {
        const data = d[this.metric] || [];
        const labels = d.timestamps || [];
        /* global Chart */
        new Chart(this.$refs.canvas.getContext('2d'), {
          type: 'line',
          data: {
            labels,
            datasets: [{
              data,
              borderColor: '#2e86de',
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
