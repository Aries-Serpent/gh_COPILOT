import json
import pathlib
import subprocess
import textwrap

import pytest


PANELS = [
    (
        "codex_changes/stubs/templates/compliance_panel.html",
        "fetch_compliance_metrics",
        "gauge_compliance",
        73,
    ),
    (
        "codex_changes/stubs/templates/monitoring_panel.html",
        "fetch_monitoring_metrics",
        "gauge_monitoring",
        64,
    ),
    (
        "codex_changes/stubs/templates/synchronization_panel.html",
        "fetch_synchronization_metrics",
        "gauge_synchronization",
        52,
    ),
]


def _extract_function(path: str, func_name: str) -> str:
    text = pathlib.Path(path).read_text(encoding="utf-8")
    start = text.index(f"async function {func_name}")
    brace = 0
    fn_chars = []
    for ch in text[start:]:
        fn_chars.append(ch)
        if ch == "{":
            brace += 1
        elif ch == "}":
            brace -= 1
            if brace == 0:
                break
    return "".join(fn_chars)


@pytest.mark.parametrize("html_path, func_name, gauge_name, value", PANELS)
def test_panel_updates_chart(html_path: str, func_name: str, gauge_name: str, value: int):
    fn_code = _extract_function(html_path, func_name)
    js = textwrap.dedent(
        f"""
        const metricValue = {value};
        globalThis.fetch = async () => {{
            return {{ ok: true, json: async () => {{ return {{ metrics: {{ value: metricValue }} }}; }} }};
        }};
        const {gauge_name} = {{
            data: {{ datasets: [{{ data: [0, 100] }}] }},
            options: {{ plugins: {{ tooltip: {{ enabled: false }}, thresholds: {{ current: 0 }} }} }},
            updateCalled: false,
            update() {{ this.updateCalled = true; }}
        }};
        {fn_code}
        (async () => {{
            await {func_name}();
            console.log(JSON.stringify({gauge_name}));
        }})();
        """
    )
    result = subprocess.run(
        ["node", "-e", js], capture_output=True, text=True, check=True
    )
    gauge = json.loads(result.stdout.strip())
    assert gauge["data"]["datasets"][0]["data"][0] == value
    assert gauge["updateCalled"] is True
    assert gauge["options"]["plugins"]["tooltip"]["enabled"] is True
    assert gauge["options"]["plugins"]["thresholds"]["current"] == value

