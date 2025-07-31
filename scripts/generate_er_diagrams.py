#!/usr/bin/env python3
"""Generate ER diagrams for specified SQLite databases."""
from __future__ import annotations
import argparse
import sqlite3
from pathlib import Path
import subprocess

def build_dot(db_path: Path) -> str:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    nodes = {}
    edges = set()
    for tbl in tables:
        cur.execute(f"PRAGMA table_info('{tbl}')")
        cols = [row[1] for row in cur.fetchall()]
        nodes[tbl] = cols
        cur.execute(f"PRAGMA foreign_key_list('{tbl}')")
        for r in cur.fetchall():
            edges.add((tbl, r[2]))
    conn.close()
    lines = ["digraph G {", "rankdir=LR;"]
    for tbl, cols in nodes.items():
        label = '{%s|%s}' % (tbl, '\\l'.join(cols) + '\\l')
        lines.append(f'"{tbl}" [shape=record,label="{label}"];')
    for src, dst in sorted(edges):
        lines.append(f'"{src}" -> "{dst}";')
    lines.append("}")
    return "\n".join(lines)

def generate_diagram(db_path: Path, output_dir: Path) -> Path:
    dot_text = build_dot(db_path)
    dot_path = output_dir / f"{db_path.stem}_er.dot"
    png_path = output_dir / f"{db_path.stem}_er.png"
    dot_path.write_text(dot_text)
    subprocess.run(["dot", "-Tpng", str(dot_path), "-o", str(png_path)], check=True)
    return png_path

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate ER diagrams for SQLite databases")
    parser.add_argument("--output", type=Path, default=Path("docs/diagrams"), help="Output directory")
    parser.add_argument("db", nargs="+", type=Path, help="Database files")
    args = parser.parse_args(argv)
    args.output.mkdir(parents=True, exist_ok=True)
    for db in args.db:
        generate_diagram(db, args.output)

if __name__ == "__main__":
    main()
  
