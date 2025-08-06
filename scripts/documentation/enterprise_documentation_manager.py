from __future__ import annotations

import logging
import os
import sqlite3
from pathlib import Path
from typing import Iterable, List

from tqdm import tqdm

from template_engine.auto_generator import (
    DEFAULT_ANALYTICS_DB,
    DEFAULT_COMPLETION_DB,
    TemplateAutoGenerator,
)
from template_engine.template_synchronizer import _compliance_score
from utils.database_utils import get_validated_production_db_connection
from utils.log_utils import _log_event


def _create_simple_pdf(path: Path, text: str) -> None:
    """Create a very basic PDF file with the given text."""

    def _escape(s: str) -> str:
        return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    lines = text.splitlines()
    content_lines = ["BT", "/F1 12 Tf"]
    y = 720
    for line in lines:
        content_lines.append(f"72 {y} Td ({_escape(line)}) Tj")
        y -= 14
    content_lines.append("ET")
    content = "\n".join(content_lines)
    objects = []
    offsets = []

    def _add(obj: str) -> None:
        offsets.append(len(b"".join(objects)))
        objects.append(obj.encode("utf-8") + b"\n")

    _add("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj")
    _add("2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj")
    _add(
        "3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        "/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj"
    )
    _add("4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj")
    _add(f"5 0 obj\n<< /Length {len(content)} >>\nstream\n{content}\nendstream\nendobj")

    xref_start = sum(len(obj) for obj in objects) + len("%PDF-1.4\n")
    xref_entries = ["0000000000 65535 f "] + [f"{off:010} 00000 n " for off in offsets]
    xref_table = "xref\n0 {n}\n".format(n=len(xref_entries)) + "\n".join(xref_entries)
    trailer = f"trailer\n<< /Root 1 0 R /Size {len(xref_entries)} >>"
    pdf_bytes = (
        b"%PDF-1.4\n"
        + b"".join(objects)
        + xref_table.encode("utf-8")
        + trailer.encode("utf-8")
        + f"\nstartxref\n{xref_start}\n%%EOF".encode("utf-8")
    )
    path.write_bytes(pdf_bytes)


def _ensure_accessible_formats(formats: Iterable[str]) -> List[str]:
    """Return output formats ensuring PDFs have a text companion."""
    fmt_list = list(formats)
    if "pdf" in fmt_list and not any(f in {"md", "html"} for f in fmt_list):
        fmt_list.append("md")
    return fmt_list


TEXT_INDICATORS = {
    "start": "[START]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
    "progress": "[PROGRESS]",
    "info": "[INFO]",
}


class EnterpriseDocumentationManager:
    """Generate documentation files from ``documentation.db``."""

    def __init__(
        self,
        workspace: Path | None = None,
        db_path: Path | None = None,
        analytics_db: Path = DEFAULT_ANALYTICS_DB,
        completion_db: Path = DEFAULT_COMPLETION_DB,
    ) -> None:
        self.workspace = Path(workspace or os.getenv("GH_COPILOT_WORKSPACE", Path(__file__).resolve().parents[2]))
        self.db_path = Path(
            db_path
            or os.getenv(
                "DOCUMENTATION_DB_PATH",
                self.workspace / "archives" / "documentation.db",
            )
        )
        self.output_dir = self.workspace / "documentation" / "generated" / "enterprise_docs"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.generator = TemplateAutoGenerator(analytics_db, completion_db)

    # ------------------------------------------------------------------
    def query_documentation(self, doc_type: str) -> list[tuple[str, str, str | None]]:
        """Return ``doc_id``, ``content`` and ``source_path`` for the given ``doc_type``."""
        if not self.db_path.exists():
            self.logger.error(f"{TEXT_INDICATORS['error']} Missing database {self.db_path}")
            return []
        query = "SELECT doc_id, content, source_path FROM enterprise_documentation WHERE doc_type=?"
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute(query, (doc_type,)).fetchall()

    # ------------------------------------------------------------------
    def select_template(self, doc_type: str) -> str:
        """Return best template for ``doc_type`` using ``TemplateAutoGenerator``."""
        template = self.generator.select_best_template(doc_type)
        if not template:
            self.logger.info(f"{TEXT_INDICATORS['info']} No template found for {doc_type}")
        return template

    # ------------------------------------------------------------------
    def calculate_compliance(self, content: str) -> float:
        """Return compliance score using analytics rules."""
        score = _compliance_score(content)
        self.logger.info(f"{TEXT_INDICATORS['info']} Compliance score {score:.2f}")
        return score

    # ------------------------------------------------------------------
    def generate_files(self, doc_type: str, output_formats: Iterable[str] | None = None) -> List[Path]:
        """Generate documentation files for ``doc_type`` in multiple formats.

        If ``pdf`` is requested without a text-based format, a Markdown copy is
        automatically produced to preserve accessible structure.
        """
        formats = _ensure_accessible_formats(output_formats or ["md"])  # default markdown for backward compat
        docs = self.query_documentation(doc_type)
        if not docs:
            return []
        template = self.select_template(doc_type)
        generated: List[Path] = []
        self.logger.info(f"{TEXT_INDICATORS['start']} Generating {doc_type} documentation")
        # record generation details in production.db
        with get_validated_production_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS documentation_status (
                    doc_id TEXT PRIMARY KEY,
                    path TEXT,
                    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            with tqdm(total=len(docs), desc=f"{TEXT_INDICATORS['progress']} docs", unit="doc") as bar:
                cross_links = 0
                for doc_id, content, source in docs:
                    base_text = template.replace("{content}", content) if template else content
                    score = self.calculate_compliance(base_text)
                    _log_event(
                        {
                            "event": "doc_generated",
                            "doc_id": doc_id,
                            "compliance_score": score,
                        },
                        table="correction_logs",
                        db_path=self.generator.analytics_db,
                        test_mode=False,
                    )
                    if score < 60.0:
                        self.logger.info(f"{TEXT_INDICATORS['info']} Skipping {doc_id} due to low score {score:.2f}")
                        bar.update(1)
                        continue
                    main_path = None
                    for fmt in formats:
                        path = self.output_dir / f"{doc_id}.{fmt}"
                        links = [self.output_dir / f"{doc_id}.{f}" for f in formats if f != fmt]
                        links_text = " | ".join(p.name for p in links)
                        comp_link = f"analytics://correction_logs/{doc_id}"
                        audit_link = f"analytics://audit_log/{doc_id}"
                        code_link = f"code://{source}" if source else "code://"
                        audit_record_link = f"logs://audit_logs/{doc_id}"
                        body = (
                            f"Code Path: {code_link}\n"
                            f"Compliance Log: {comp_link}\n"
                            f"Audit Record: {audit_link}\n"
                            f"Audit Log: {audit_record_link}\n"
                            f"Linked: {links_text}\n\n{base_text}"
                        )
                        if fmt == "html":
                            html_body = body.replace("\n", "<br>")
                            text = f"<html><body>{html_body}</body></html>"
                        else:
                            text = body
                        if fmt == "pdf":
                            try:
                                from reportlab.lib.pagesizes import letter
                                from reportlab.pdfgen import canvas

                                c = canvas.Canvas(str(path), pagesize=letter)
                                text_obj = c.beginText(40, 750)
                                for line in body.splitlines():
                                    text_obj.textLine(line)
                                c.drawText(text_obj)
                                c.save()
                            except Exception:  # pragma: no cover - fallback if reportlab missing
                                _create_simple_pdf(path, body)
                        else:
                            path.write_text(text, encoding="utf-8")
                        generated.append(path)
                        if main_path is None:
                            main_path = path
                        for link in links:
                            _log_event(
                                {"file_path": str(path), "linked_path": str(link)},
                                table="cross_link_events",
                                db_path=self.generator.analytics_db,
                                test_mode=False,
                            )
                            cross_links += 1
                    cur.execute(
                        """
                        INSERT INTO documentation_status (doc_id, path, generated_at)
                        VALUES (?, ?, CURRENT_TIMESTAMP)
                        ON CONFLICT(doc_id) DO UPDATE SET
                            path=excluded.path,
                            generated_at=excluded.generated_at
                        """,
                        (doc_id, str(main_path)),
                    )
                    bar.update(1)
                _log_event(
                    {"actions": len(docs), "links": cross_links},
                    table="cross_link_summary",
                    db_path=self.generator.analytics_db,
                    test_mode=False,
                )
            conn.commit()
        self.logger.info(f"{TEXT_INDICATORS['success']} Generated {len(generated)} {doc_type} files")
        return generated


__all__ = ["EnterpriseDocumentationManager"]
