"""High-level API for interacting with quantum services.

This module exposes a very small facade used throughout the tests to
simulate execution of quantum tasks.  The real project integrates with
various backends, but for unit testing we only need a deterministic and
side‑effect free implementation.  The :func:`execute_quantum_task` function
therefore wires together the template and websocket helpers defined in the
same package and returns a simple dictionary describing the result of the
operation.
"""

from typing import Any, Dict

from . import quantum_templates, quantum_websocket


def execute_quantum_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a quantum task described by ``task``.

    Parameters
    ----------
    task:
        A dictionary describing the work to perform.  It must contain a
        ``"template"`` key referencing a registered template and may
        optionally include ``"input"`` and ``"url"`` entries.  ``"input"``
        is passed to the template callable and ``"url"`` – when provided –
        will be used to open a simulated websocket connection.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing the ``"result"`` from the template
        execution.  If a ``"url"`` was supplied the returned mapping also
        includes a ``"socket"`` entry describing the opened connection.
    """

    template_name = task.get("template")
    if not template_name:
        raise ValueError("task must include a 'template' field")

    template = quantum_templates.get_template(template_name)
    input_data = task.get("input")
    result = template(input_data)

    socket_info = None
    url = task.get("url")
    if url:
        socket = quantum_websocket.open_quantum_socket(url)
        socket_info = {"url": socket.url}

    response: Dict[str, Any] = {"result": result}
    if socket_info:
        response["socket"] = socket_info
    return response
