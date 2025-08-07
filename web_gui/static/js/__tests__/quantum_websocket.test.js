// Primary Copilot: test websocket creation.
// Secondary Copilot: ensure returned object matches mock.
import { connectQuantumWebSocket } from '../quantum_websocket.js';

test('connectQuantumWebSocket returns a WebSocket', () => {
  class MockWebSocket {
    constructor() { this.events = {}; }
    addEventListener(type, handler) { this.events[type] = handler; }
  }
  global.WebSocket = MockWebSocket;
  const socket = connectQuantumWebSocket('ws://example');
  expect(socket).toBeInstanceOf(MockWebSocket);
});
