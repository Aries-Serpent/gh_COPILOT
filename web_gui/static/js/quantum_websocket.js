export function connectQuantumWebSocket(endpoint) {
  const socket = new WebSocket(endpoint);
  socket.addEventListener('open', () => {
    console.debug('Quantum websocket connected');
  });
  return socket;
}
