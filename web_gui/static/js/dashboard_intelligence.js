// Primary Copilot: orchestrate dashboard initialization.
// Secondary Copilot: confirm subsystems readiness.

import { initRealTimeUpdates } from './real_time_updates.js';
import { connectQuantumWebSocket } from './quantum_websocket.js';
import { validateSecurity } from './security_validation.js';

async function renderComplianceChart() {
  try {
    const resp = await fetch('/api/compliance_scores');
    const data = await resp.json();
    const ctx = document.getElementById('complianceChart');
    if (ctx && window.Chart) {
      const labels = data.scores.map((s) => s.timestamp);
      const scores = data.scores.map((s) => s.composite);
      // eslint-disable-next-line no-new
      new Chart(ctx, {
        type: 'line',
        data: { labels, datasets: [{ label: 'Compliance', data: scores }] },
      });
    }
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('Failed to render compliance chart', err);
  }
}

export async function initDashboard() {
  initRealTimeUpdates();
  connectQuantumWebSocket('ws://localhost/updates');
  validateSecurity();
  await renderComplianceChart();
}

document.addEventListener('DOMContentLoaded', initDashboard);
