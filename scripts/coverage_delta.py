import sys
import subprocess
import xml.etree.ElementTree as ET


def read_rate(xml_content: str) -> float:
    root = ET.fromstring(xml_content)
    return float(root.attrib.get("line-rate", 0)) * 100


def main(current_path: str, base_ref: str = "origin/main:reports/coverage/coverage.xml") -> None:
    current_xml = open(current_path).read()
    current = read_rate(current_xml)
    try:
        base_xml = subprocess.check_output(["git", "show", base_ref], text=True)
    except subprocess.CalledProcessError:
        print("Base coverage file not found; skipping delta check")
        return
    base = read_rate(base_xml)
    delta = current - base
    print(f"Base coverage: {base:.2f}% | Current coverage: {current:.2f}% | Delta: {delta:.2f}%")
    if delta < 0:
        sys.exit(1)


if __name__ == "__main__":
    path = sys.argv[1]
    ref = sys.argv[2] if len(sys.argv) > 2 else "origin/main:reports/coverage/coverage.xml"
    main(path, ref)
