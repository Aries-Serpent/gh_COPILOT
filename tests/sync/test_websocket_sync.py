import asyncio
from typing import List

import websockets

from src.sync.engine import Change, SyncEngine


async def _websocket_roundtrip() -> None:
    peers = set()

    async def handler(ws):
        peers.add(ws)
        try:
            async for msg in ws:
                for peer in peers:
                    if peer is not ws:
                        await peer.send(msg)
        finally:
            peers.remove(ws)

    server = await websockets.serve(handler, "localhost", 8765)

    engine_a = SyncEngine()
    engine_b = SyncEngine()
    applied_a = []
    applied_b = []

    task_a = asyncio.create_task(
        engine_a.open_websocket("ws://localhost:8765", lambda c: applied_a.append(c))
    )
    task_b = asyncio.create_task(
        engine_b.open_websocket("ws://localhost:8765", lambda c: applied_b.append(c))
    )

    await asyncio.sleep(0.1)

    change_a = Change(id="a", payload={"n": 1}, timestamp=0.0)
    engine_a.notify_change(change_a)
    await asyncio.sleep(0.1)
    assert applied_b == [change_a]

    change_b = Change(id="b", payload={"n": 2}, timestamp=0.0)
    engine_b.notify_change(change_b)
    await asyncio.sleep(0.1)
    assert applied_a == [change_b]

    task_a.cancel()
    task_b.cancel()
    await asyncio.gather(task_a, task_b, return_exceptions=True)
    server.close()
    await server.wait_closed()


def test_websocket_bidirectional_sync() -> None:
    asyncio.run(_websocket_roundtrip())


async def _websocket_multi_roundtrip() -> None:
    peers = set()

    async def handler(ws):
        peers.add(ws)
        try:
            async for msg in ws:
                for peer in peers:
                    if peer is not ws:
                        await peer.send(msg)
        finally:
            peers.remove(ws)

    server = await websockets.serve(handler, "localhost", 8766)

    engine_a = SyncEngine()
    engine_b = SyncEngine()
    applied_a: List[Change] = []
    applied_b: List[Change] = []

    task_a = asyncio.create_task(
        engine_a.open_websocket("ws://localhost:8766", lambda c: applied_a.append(c))
    )
    task_b = asyncio.create_task(
        engine_b.open_websocket("ws://localhost:8766", lambda c: applied_b.append(c))
    )

    await asyncio.sleep(0.1)

    for i in range(2):
        change = Change(id=f"a{i}", payload={"n": i}, timestamp=float(i))
        engine_a.notify_change(change)
    for i in range(2):
        change = Change(id=f"b{i}", payload={"n": i}, timestamp=float(i))
        engine_b.notify_change(change)

    await asyncio.sleep(0.2)
    assert applied_b == [Change(id="a0", payload={"n": 0}, timestamp=0.0), Change(id="a1", payload={"n": 1}, timestamp=1.0)]
    assert applied_a == [Change(id="b0", payload={"n": 0}, timestamp=0.0), Change(id="b1", payload={"n": 1}, timestamp=1.0)]

    task_a.cancel()
    task_b.cancel()
    await asyncio.gather(task_a, task_b, return_exceptions=True)
    server.close()
    await server.wait_closed()


def test_websocket_multi_message_sync() -> None:
    asyncio.run(_websocket_multi_roundtrip())

