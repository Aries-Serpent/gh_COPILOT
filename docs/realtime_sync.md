# Real-time Synchronization

The `SyncEngine` can propagate changes to connected peers over a WebSocket
channel. To enable WebSocket-based synchronization:

1. Start a WebSocket server that broadcasts messages to all participants.
2. Set the environment variable `SYNC_ENGINE_WS_URL` to the server's URL
   (for example `ws://localhost:8765`).
3. Create a `SyncEngine` instance and call
   `await engine.open_websocket(os.environ["SYNC_ENGINE_WS_URL"], apply)`
   where `apply` is a callback that applies received changes locally.

Queued local changes are sent automatically, and remote changes are applied
in real time, enabling bi-directional updates across clients.

