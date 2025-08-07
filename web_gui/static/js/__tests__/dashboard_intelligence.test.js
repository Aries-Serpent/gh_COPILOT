// Primary Copilot: test dashboard initialization orchestration.
// Secondary Copilot: confirm no errors during initialization.
import { initDashboard } from '../dashboard_intelligence.js';

test('initDashboard runs without error', () => {
  document.body.innerHTML = '<div id="progress"></div>';
  global.WebSocket = class { constructor() { this.addEventListener = () => {}; } };
  expect(() => initDashboard()).not.toThrow();
});
