import sys
import xml.etree.ElementTree as ET


def main(path: str, threshold: float = 90.0) -> None:
    tree = ET.parse(path)
    root = tree.getroot()
    tests = int(root.attrib.get("tests", 0))
    failures = int(root.attrib.get("failures", 0))
    errors = int(root.attrib.get("errors", 0))
    skipped = int(root.attrib.get("skipped", 0))
    executed = tests - skipped
    passed = executed - failures - errors
    if executed == 0:
        print("Pass rate: 0.00% (0/0)")
        sys.exit(1)
    rate = (passed / executed) * 100
    print(f"Pass rate: {rate:.2f}% ({passed}/{executed})")
    if rate < threshold:
        sys.exit(1)


if __name__ == "__main__":
    file_path = sys.argv[1]
    thr = float(sys.argv[2]) if len(sys.argv) > 2 else 90.0
    main(file_path, thr)
