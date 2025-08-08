// Primary Copilot: orchestrate dashboard initialization.
// Secondary Copilot: confirm subsystems readiness.

import { initRealTimeUpdates } from './real_time_updates.js';
import { connectQuantumWebSocket } from './quantum_websocket.js';
import { validateSecurity } from './security_validation.js';

export function initDashboard() {
  initRealTimeUpdates();
  connectQuantumWebSocket('ws://localhost/updates');
  validateSecurity();
}

document.addEventListener('DOMContentLoaded', initDashboard);
