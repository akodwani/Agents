from __future__ import annotations

import json
import re
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from zipfile import ZIP_DEFLATED, ZipFile

BASE_DIR = Path(__file__).parent
LOG_PATH = BASE_DIR / "logs" / "verify_events.jsonl"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
INDEX_PATH = BASE_DIR / "templates" / "index.html"


def ensure_dirs() -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def append_verify_event(event_type: str, payload: dict) -> None:
    ensure_dirs()
    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "event": event_type,
        "payload": payload,
    }
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def make_job_output(jd_text: str) -> str:
    words = [w for w in jd_text.split() if w.strip()]
    return (
        "Job Machine output:\n"
        f"- Input length: {len(jd_text)} chars\n"
        f"- Keyword count: {len(words)}\n"
        "- Suggested focus: prioritize measurable impact, ownership, and stack fit."
    )


def make_consultant_output(problem: str, context: str) -> str:
    return (
        "Consultant output:\n"
        f"1) Problem framing: {problem[:120]}\n"
        f"2) Context lens: {context[:120]}\n"
        "3) Recommendation: run a 2-week pilot with clear KPIs and weekly checkpoints."
    )


def xml_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def create_simple_xlsx(path: Path, snapshot: str, analysis: str) -> None:
    content_types = """<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">
    <Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>
    <Default Extension=\"xml\" ContentType=\"application/xml\"/>
    <Override PartName=\"/xl/workbook.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml\"/>
    <Override PartName=\"/xl/worksheets/sheet1.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml\"/>
</Types>"""
    rels = """<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">
    <Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"xl/workbook.xml\"/>
</Relationships>"""
    workbook = """<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\">
  <sheets><sheet name=\"Analysis\" sheetId=\"1\" r:id=\"rId1\"/></sheets>
</workbook>"""
    workbook_rels = """<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">
  <Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\" Target=\"worksheets/sheet1.xml\"/>
</Relationships>"""

    rows = [
        ("Company Snapshot", snapshot),
        ("Analyst Summary", analysis),
        ("Generated At", datetime.utcnow().isoformat() + "Z"),
    ]
    row_xml = []
    for idx, (k, v) in enumerate(rows, start=1):
        row_xml.append(
            f"<row r=\"{idx}\"><c r=\"A{idx}\" t=\"inlineStr\"><is><t>{xml_escape(k)}</t></is></c>"
            f"<c r=\"B{idx}\" t=\"inlineStr\"><is><t>{xml_escape(v)}</t></is></c></row>"
        )
    sheet = """<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"><sheetData>%s</sheetData></worksheet>""" % "".join(row_xml)

    with ZipFile(path, "w", ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("xl/workbook.xml", workbook)
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        zf.writestr("xl/worksheets/sheet1.xml", sheet)


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, text: str, content_type: str = "text/plain; charset=utf-8") -> None:
        body = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def do_GET(self) -> None:  # noqa: N802
        ensure_dirs()
        path = urlparse(self.path).path
        if path == "/":
            self._send_text(INDEX_PATH.read_text(encoding="utf-8"), "text/html; charset=utf-8")
            return

        if path == "/budget":
            status = {
                "currency": "USD",
                "allocated": 100000,
                "spent": 46750,
                "remaining": 53250,
                "health": "on_track",
            }
            append_verify_event("budget", {"remaining": status["remaining"]})
            self._send_json(status)
            return

        if path == "/verify-events":
            if not LOG_PATH.exists():
                self._send_json({"lines": []})
                return
            lines = LOG_PATH.read_text(encoding="utf-8").splitlines()[-20:]
            self._send_json({"lines": lines})
            return

        artifact_match = re.match(r"^/artifacts/(.+)$", path)
        if artifact_match:
            filename = artifact_match.group(1)
            file_path = ARTIFACTS_DIR / filename
            if file_path.exists() and file_path.is_file():
                data = file_path.read_bytes()
                self.send_response(200)
                self.send_header(
                    "Content-Type",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
                self.send_header("Content-Disposition", f'attachment; filename="{file_path.name}"')
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

        self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        ensure_dirs()
        path = urlparse(self.path).path
        payload = self._read_json()

        if path == "/job":
            jd_text = payload.get("jd_text", "")
            output = make_job_output(jd_text)
            append_verify_event("job", {"jd_text_length": len(jd_text)})
            self._send_json({"output": output})
            return

        if path == "/consultant":
            problem = payload.get("problem", "")
            context = payload.get("context", "")
            output = make_consultant_output(problem, context)
            append_verify_event(
                "consultant",
                {"problem_length": len(problem), "context_length": len(context)},
            )
            self._send_json({"output": output})
            return

        if path == "/analyst":
            snapshot = payload.get("company_snapshot", "")
            analysis = (
                "Analyst output:\n"
                f"- Snapshot size: {len(snapshot)} chars\n"
                "- Signal: healthy growth potential with execution risk in GTM consistency.\n"
                "- Next step: validate pipeline conversion and gross margin trend."
            )
            filename = f"analyst_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
            create_simple_xlsx(ARTIFACTS_DIR / filename, snapshot[:300], analysis)
            append_verify_event("analyst", {"snapshot_length": len(snapshot), "xlsx": filename})
            self._send_json({"output": analysis, "xlsx_link": f"/artifacts/{filename}"})
            return

        self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)


if __name__ == "__main__":
    ensure_dirs()
    server = ThreadingHTTPServer(("0.0.0.0", 8000), Handler)
    print("Server running at http://0.0.0.0:8000")
    server.serve_forever()
