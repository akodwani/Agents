from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable
from zipfile import ZIP_DEFLATED, ZipFile


def run_council_aggregation(members: list[dict]) -> dict:
    """Aggregate mock council opinions and classify disagreement types."""
    votes = [member.get("vote", "abstain") for member in members]
    rationales = [member.get("rationale", "") for member in members]

    disagreement_types: set[str] = set()
    if len(set(votes)) > 1:
        disagreement_types.add("outcome_disagreement")

    confidence_levels = [member.get("confidence") for member in members if "confidence" in member]
    if len(set(confidence_levels)) > 1:
        disagreement_types.add("confidence_disagreement")

    if len(set(rationales)) > 1:
        disagreement_types.add("rationale_disagreement")

    return {
        "member_count": len(members),
        "votes": votes,
        "disagreement_types": sorted(disagreement_types),
    }


def run_job_machine(job_descriptions: list[str]) -> list[dict]:
    """Screen JDs with simple deterministic rejection rules."""
    results = []
    for jd in job_descriptions:
        lowered = jd.lower()
        reject_markers = ["unpaid", "commission only", "night shift only", "no benefits"]
        rejected = any(marker in lowered for marker in reject_markers)
        results.append({"jd": jd, "decision": "reject" if rejected else "accept"})
    return results


def run_consultant(problem_statement: str) -> str:
    """Return a consultant brief with required decision-forcer sections."""
    return (
        f"# Consultant Brief\n\n"
        f"Problem: {problem_statement}\n\n"
        "## Decision Forcer\n"
        "- Define a go/no-go trigger and owner.\n\n"
        "## Decision Forcer: Constraints\n"
        "- Bound timeline, budget, and risk tolerance.\n\n"
        "## Recommendation\n"
        "- Execute the highest-confidence path first.\n"
    )


def _minimal_xlsx_bytes(rows: Iterable[tuple[str, str]]) -> bytes:
    """Create a minimal XLSX workbook from string rows without external dependencies."""
    rows_xml = []
    for row_idx, (metric, value) in enumerate(rows, start=1):
        rows_xml.append(
            f"<row r=\"{row_idx}\">"
            f"<c r=\"A{row_idx}\" t=\"inlineStr\"><is><t>{metric}</t></is></c>"
            f"<c r=\"B{row_idx}\" t=\"inlineStr\"><is><t>{value}</t></is></c>"
            "</row>"
        )

    sheet_xml = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">"
        f"<sheetData>{''.join(rows_xml)}</sheetData>"
        "</worksheet>"
    )

    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>"""

    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""

    workbook = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="Analysis" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>"""

    workbook_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>"""

    from io import BytesIO

    buffer = BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("xl/workbook.xml", workbook)
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)
    return buffer.getvalue()


def run_analyst(data: dict[str, str], output_path: str | Path) -> Path:
    """Generate an XLSX artifact from analyst metrics."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    xlsx_bytes = _minimal_xlsx_bytes(data.items())
    destination.write_bytes(xlsx_bytes)
    return destination


def trigger_verification(events: list[dict], output_path: str | Path) -> Path:
    """Persist verification events to a JSONL file."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event) + "\n")
    return destination
