(function () {
  function emit(data) {
    window.dispatchEvent(new CustomEvent('corrections-update', { detail: data }));
  }
  function startSSE() {
    const source = new EventSource('/corrections_stream');
    source.onmessage = (e) => emit(JSON.parse(e.data));
  }
  try {
    const ws = new WebSocket((location.origin.replace('http', 'ws')) + '/ws/corrections');
    ws.onmessage = (e) => emit(JSON.parse(e.data));
    ws.onerror = startSSE;
    ws.onclose = startSSE;
  } catch (err) {
    startSSE();
  }
})();
