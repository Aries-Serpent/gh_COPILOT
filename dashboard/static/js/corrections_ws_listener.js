export function startCorrectionsListener(onUpdate) {
  function handle(data) {
    try {
      onUpdate(data);
    } catch (e) {
      console.error('corrections listener callback failed', e);
    }
  }
  function connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const url = protocol + window.location.host + '/ws/corrections';
    try {
      const ws = new WebSocket(url);
      ws.onmessage = (ev) => handle(JSON.parse(ev.data));
      ws.onerror = () => fallback();
    } catch (err) {
      fallback();
    }
  }
  function fallback() {
    const es = new EventSource('/corrections_stream');
    es.onmessage = (ev) => handle(JSON.parse(ev.data));
  }
  connect();
}
