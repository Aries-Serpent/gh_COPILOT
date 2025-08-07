// Primary Copilot: test real-time update DOM mutation.
// Secondary Copilot: verify text content after initialization.
import { initRealTimeUpdates } from '../real_time_updates.js';

test('initRealTimeUpdates updates DOM', () => {
  document.body.innerHTML = '<div id="progress"></div>';
  initRealTimeUpdates();
  expect(document.getElementById('progress').textContent).toBe('Real-time updates active');
});
