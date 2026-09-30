"""Export jobs to CSV, Excel and PDF."""

from __future__ import annotations

import csv
import logging
from collections import Counter
from collections.abc import Callable, Sequence
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from job_automation.models import Job

logger = logging.getLogger(__name__)

# (Job attribute, column header, Excel column width)
_COLUMNS = (
    ("title", "Title", 34),
    ("company", "Company", 28),
    ("location", "Location", 32),
    ("posted_date", "Posted", 12),
    ("url", "Details URL", 48),
    ("apply_url", "Apply URL", 48),
    ("description", "Description", 60),
)


def export_csv(jobs: Sequence[Job], path: Path) -> Path:
    """UTF-8 with BOM so Excel opens accented characters correctly."""
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow([header for _, header, _ in _COLUMNS])
        for job in jobs:
            writer.writerow([getattr(job, attr) for attr, _, _ in _COLUMNS])
    return path


def export_excel(jobs: Sequence[Job], path: Path) -> Path:
    """Styled workbook: bold header, frozen row, filters, clickable links."""
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Jobs"
    sheet.append([header for _, header, _ in _COLUMNS])

    header_fill = PatternFill("solid", fgColor="1F4E78")
    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = header_fill
        cell.alignment = Alignment(vertical="center")

    for job in jobs:
        sheet.append([getattr(job, attr) for attr, _, _ in _COLUMNS])
    for row in sheet.iter_rows(min_row=2):
        for cell in row:
            if isinstance(cell.value, str) and cell.value.startswith("http"):
                cell.hyperlink = cell.value
                cell.style = "Hyperlink"

    for index, (_, _, width) in enumerate(_COLUMNS, start=1):
        sheet.column_dimensions[sheet.cell(row=1, column=index).column_letter].width = width
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    workbook.save(path)
    return path


def _top(counter: Counter, n: int = 5) -> str:
    return ", ".join(f"{name} ({count})" for name, count in counter.most_common(n)) or "-"


def export_pdf(jobs: Sequence[Job], path: Path, title: str = "Job Search Report") -> Path:
    """Landscape A4 report with a short summary and a paginated table."""
    styles = getSampleStyleSheet()
    cell_style = ParagraphStyle("cell", parent=styles["BodyText"], fontSize=8, leading=10)
    doc = SimpleDocTemplate(
        str(path), pagesize=landscape(A4), title=title,
        leftMargin=15 * mm, rightMargin=15 * mm, topMargin=15 * mm, bottomMargin=15 * mm,
    )

    story = [
        Paragraph(escape(title), styles["Title"]),
        Paragraph(
            f"Generated {datetime.now():%Y-%m-%d %H:%M} &nbsp;|&nbsp; Total jobs: <b>{len(jobs)}</b>",
            styles["Normal"],
        ),
        Paragraph(f"Top locations: {escape(_top(Counter(j.location for j in jobs)))}", styles["Normal"]),
        Paragraph(f"Top companies: {escape(_top(Counter(j.company for j in jobs)))}", styles["Normal"]),
        Spacer(1, 6 * mm),
    ]

    def link(url: str) -> str:
        return f'<link href="{escape(url, {chr(34): "&quot;"})}" color="blue">Apply</link>' if url else "-"

    rows = [["Title", "Company", "Location", "Posted", "Apply"]]
    for job in jobs:
        rows.append([
            Paragraph(escape(job.title), cell_style),
            Paragraph(escape(job.company), cell_style),
            Paragraph(escape(job.location), cell_style),
            Paragraph(escape(job.posted_date or "-"), cell_style),
            Paragraph(link(job.apply_url), cell_style),
        ])

    table = Table(rows, colWidths=[75 * mm, 60 * mm, 70 * mm, 27 * mm, 35 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6FA")]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(table)
    doc.build(story)
    return path


EXPORTERS: dict[str, tuple[Callable[[Sequence[Job], Path], Path], str]] = {
    "csv": (export_csv, ".csv"),
    "excel": (export_excel, ".xlsx"),
    "pdf": (export_pdf, ".pdf"),
}


def export_all(jobs: Sequence[Job], formats: Sequence[str], output_dir: Path, stem: str) -> list[Path]:
    """Write ``jobs`` in every requested format and return the created paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    for fmt in dict.fromkeys(formats):  # de-duplicate, keep order
        exporter, extension = EXPORTERS[fmt]
        path = exporter(jobs, output_dir / f"{stem}{extension}")
        logger.info("Exported %d jobs -> %s", len(jobs), path)
        created.append(path)
    return created
