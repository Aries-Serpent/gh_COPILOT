(function () {
  function updateLogs(data) {
    if (window && typeof window.dispatchEvent === 'function') {
      window.dispatchEvent(new CustomEvent('corrections-update', { detail: data }));
    }
  }
  function connect() {
    var protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    var url = protocol + window.location.host + '/ws/corrections';
    try {
      var ws = new WebSocket(url);
      ws.onmessage = function (ev) {
        updateLogs(JSON.parse(ev.data));
      };
      ws.onerror = function () {
        fallback();
      };
    } catch (e) {
      fallback();
    }
    function fallback() {
      var es = new EventSource('/corrections_stream');
      es.onmessage = function (ev) {
        updateLogs(JSON.parse(ev.data));
      };
    }
  }
  if (document.readyState !== 'loading') {
    connect();
  } else {
    document.addEventListener('DOMContentLoaded', connect);
  }
})();
