import csv

from openpyxl import load_workbook

from job_automation.exporters import export_all, export_csv, export_excel, export_pdf


def test_csv_has_header_and_rows(tmp_path, jobs):
    path = export_csv(jobs, tmp_path / "jobs.csv")
    rows = list(csv.reader(path.open(encoding="utf-8-sig")))
    assert rows[0][:3] == ["Title", "Company", "Location"]
    assert len(rows) == len(jobs) + 1


def test_excel_is_readable_and_styled(tmp_path, jobs):
    path = export_excel(jobs, tmp_path / "jobs.xlsx")
    sheet = load_workbook(path)["Jobs"]
    assert sheet.max_row == len(jobs) + 1
    assert sheet.freeze_panes == "A2"
    assert sheet["A2"].value == "Python Developer"


def test_pdf_is_a_real_pdf(tmp_path, jobs):
    path = export_pdf(jobs, tmp_path / "jobs.pdf")
    assert path.read_bytes().startswith(b"%PDF")


def test_export_all_creates_each_format_once(tmp_path, jobs):
    files = export_all(jobs, ["csv", "pdf", "csv"], tmp_path / "out", "report")
    assert [f.suffix for f in files] == [".csv", ".pdf"]
    assert all(f.exists() for f in files)
