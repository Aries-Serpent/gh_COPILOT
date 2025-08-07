// Primary Copilot: establish WebSocket communication channel.
// Secondary Copilot: monitor connection state for diagnostics.

export function connectQuantumWebSocket(endpoint, onMessage = () => {}) {
  const socket = new WebSocket(endpoint);
  socket.addEventListener('open', () => {
    console.debug('Quantum websocket connected');
  });
  socket.addEventListener('message', (event) => {
    onMessage(event.data);
  });
  return socket;
}
