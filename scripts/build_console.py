#!/usr/bin/env python3
"""Validate the three CSV tables and render the current table, using stdlib only."""

import argparse
import csv
from datetime import date
from html import escape
from pathlib import Path
import re
import sys
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
FIELDS = (
    "sequence", "candidate_id", "name", "role", "school", "source", "intake_date",
    "stage", "human_decision", "ai_recommendation", "role_id", "candidate_directory", "updated_at",
)
LABELS = (
    "No.", "Candidate ID", "Name", "Role", "School", "Source", "Intake date",
    "Stage", "Human decision", "AI suggestion", "Role ID", "Candidate materials", "Updated",
)
STAGES = {
    "Pending confirmation", "Received", "Awaiting screening",
    "Awaiting first interview scheduling", "First interview",
    "Awaiting second interview scheduling", "Second interview",
    "Awaiting third interview scheduling", "Third interview", "Awaiting decision",
    "Offer discussion", "Awaiting start", "Hired", "Paused", "Closed", "Archived",
}
DECISIONS = {"", "Advance", "Do not advance", "Rejected", "Withdrawn", "Offer declined", "Offer accepted", "Hired"}
ARCHIVE_DECISIONS = {"Do not advance", "Rejected", "Withdrawn", "Offer declined"}
TABLES = (
    ("00-console/candidates.csv", "02-candidates"),
    ("90-archive/archived-candidates.csv", "90-archive"),
    ("91-hired/hired-candidates.csv", "91-hired"),
)
OUTPUT = ROOT / "00-console/candidates.html"


def fail(message):
    raise ValueError(message)


def slug(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def role_index():
    roles = {}
    for card in sorted((ROOT / "01-roles").glob("*/role-card.md")):
        text = card.read_text(encoding="utf-8")
        role_id = re.search(r"^\| Role ID \| ([^|]+) \|$", text, re.M)
        name = re.search(r"^\| Role name \| ([^|]+) \|$", text, re.M)
        if not role_id or not name:
            fail(f"{card.relative_to(ROOT)}: missing role ID or name")
        key = role_id[1].strip()
        if not re.fullmatch(r"J-\d{6}-[A-Z0-9]+", key) or key in roles:
            fail(f"{card.relative_to(ROOT)}: invalid or duplicate role ID")
        if not card.parent.name.startswith(key + "-"):
            fail(f"{card.relative_to(ROOT)}: directory does not match role ID")
        for required in ("JD.md", "screening-criteria.md"):
            if not (card.parent / required).is_file():
                fail(f"{card.parent.relative_to(ROOT)}: missing {required}")
        roles[key] = name[1].strip()
    return roles


def load_tables():
    roles = role_index()
    seen_ids, seen_paths = set(), set()
    tables = []
    for relative, bucket in TABLES:
        rows = []
        with (ROOT / relative).open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != list(FIELDS):
                fail(f"{relative}: incorrect CSV header or column order")
            for row in reader:
                if not any(value for value in row.values()):
                    continue
                if set(row) != set(FIELDS) or any(v is None for v in row.values()):
                    fail(f"{relative}: wrong field count at line {reader.line_num}")
                for key, value in row.items():
                    if value != value.strip():
                        fail(f"{relative}: surrounding whitespace in {key} at line {reader.line_num}")
                cid, job_id = row["candidate_id"], row["role_id"]
                if not re.fullmatch(r"C-\d{6}-\d{3}", cid) or cid in seen_ids:
                    fail(f"{relative}: invalid candidate ID or duplicate across tables")
                if row["sequence"] != str(len(rows) + 1):
                    fail(f"{relative}: sequence numbers are not consecutive")
                if roles.get(job_id) != row["role"]:
                    fail(f"{relative}: role ID and display name do not match")
                for field in ("intake_date", "updated_at"):
                    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row[field]):
                        fail(f"{relative}: {field} must use YYYY-MM-DD")
                    date.fromisoformat(row[field])
                if row["intake_date"] > row["updated_at"]:
                    fail(f"{relative}: update date precedes intake date")
                stage, decision = row["stage"], row["human_decision"]
                if stage not in STAGES or decision not in DECISIONS:
                    fail(f"{relative}: stage or decision is not a controlled value")
                if row["ai_recommendation"] and not row["ai_recommendation"].startswith("AI suggestion: "):
                    fail(f"{relative}: AI recommendation is missing its label")
                if bucket == "02-candidates" and (
                    stage in {"Archived", "Hired"} or decision in ARCHIVE_DECISIONS | {"Hired"}
                ):
                    fail(f"{relative}: current table contains an ended record")
                if bucket == "90-archive" and (stage != "Archived" or decision not in ARCHIVE_DECISIONS):
                    fail(f"{relative}: incorrect archive stage or decision")
                if bucket == "91-hired" and (stage != "Hired" or decision != "Hired"):
                    fail(f"{relative}: incorrect hired stage or decision")
                path = Path(row["candidate_directory"])
                depth = 3 if bucket == "02-candidates" else 2
                if path.is_absolute() or ".." in path.parts or len(path.parts) != depth:
                    fail(f"{relative}: candidate directory is not an allowed relative path")
                if path.parts[0] != bucket or (depth == 3 and path.parts[1] != slug(row["role"])):
                    fail(f"{relative}: incorrect candidate bucket or role directory")
                if path.name not in {slug(row["name"]), slug(row["name"]) + "-" + cid}:
                    fail(f"{relative}: candidate directory does not match name")
                folder = (ROOT / path).resolve()
                if not folder.is_relative_to(ROOT) or folder in seen_paths:
                    fail(f"{relative}: candidate directory is outside the workspace or repeated")
                card = folder / "candidate-card.md"
                if not card.is_file() or cid not in card.read_text(encoding="utf-8"):
                    fail(f"{relative}: missing candidate card or mismatched ID")
                seen_ids.add(cid)
                seen_paths.add(folder)
                rows.append(row)
        if rows != sorted(rows, key=lambda r: (r["role_id"], r["candidate_id"])):
            fail(f"{relative}: rows are not sorted by role ID and candidate ID")
        tables.append(rows)
    for _, bucket in TABLES:
        for card in (ROOT / bucket).rglob("candidate-card.md"):
            if card.parent.resolve() not in seen_paths:
                fail(f"{card.relative_to(ROOT)}: candidate folder has no table entry")
    return tables


def render(rows):
    parts = []
    previous = None
    for row in rows:
        if row["role_id"] != previous:
            if previous is not None:
                parts.append('<tr class="spacer" aria-hidden="true"><td colspan="13"></td></tr>')
            previous = row["role_id"]
        cells = []
        for field in FIELDS:
            value = escape(row[field] or "—")
            if field == "candidate_directory":
                target = "../" + quote(row[field] + "/candidate-card.md", safe="/")
                value = f'<a href="{target}">View candidate card</a>'
            cells.append(f"<td>{value}</td>")
        parts.append("<tr>" + "".join(cells) + "</tr>")
    if not rows:
        parts.append('<tr><td colspan="13">No current candidates</td></tr>')
    headers = "".join(f'<th scope="col">{escape(label)}</th>' for label in LABELS)
    body = "\n".join(parts)
    groups = len({row["role_id"] for row in rows})
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="referrer" content="no-referrer">
<title>Candidate tracker · Recruit Template Version</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;padding:40px 24px;background:#f5f6f8;color:#1d2939;font:15px/1.6 system-ui,sans-serif}}
main{{max-width:1600px;margin:auto}}h1{{font-size:28px;margin:0 0 8px}}a{{color:#2452a1;text-underline-offset:3px}}
.notice{{padding:14px 18px;border:1px solid #dfc97b;background:#fff9e9;border-radius:8px;margin:20px 0}}
.meta{{color:#475467}}.table-wrap{{overflow-x:auto;border:1px solid #d0d5dd;border-radius:8px;background:white}}
table{{width:100%;border-collapse:collapse;text-align:left}}caption{{text-align:left;padding:16px;font-weight:600}}
th,td{{padding:12px 14px;border-bottom:1px solid #eaecf0;vertical-align:top;min-width:110px}}
th{{background:#f0f3f8;white-space:nowrap}}td:nth-child(10){{min-width:260px}}td:nth-child(2),td:nth-child(11){{white-space:nowrap}}
.spacer td{{padding:5px;background:#f5f6f8}}footer{{margin-top:20px;color:#475467}}
@media(max-width:640px){{body{{padding:24px 12px}}h1{{font-size:24px}}}}
</style>
</head>
<body><main>
<p class="meta">Recruit Template Version · Local browser</p>
<h1>Candidate tracker</h1>
<p class="notice">All records in this public template are fictional and do not correspond to real people. Do not publish this page after adding real information to a private copy.</p>
<p><a href="candidates.csv">CSV source of truth</a> · <a href="hiring-todos.md">Hiring todos</a> · <a href="../README.md">User guide</a></p>
<p class="meta">Current candidates: {len(rows)} · Roles: {groups}. Archived and hired records are excluded.</p>
<div class="table-wrap"><table>
<caption>Current candidates, grouped by role</caption>
<thead><tr>{headers}</tr></thead>
<tbody>
{body}
</tbody></table></div>
<footer>This page is generated from CSV. Maintain stages in CSV, then run <code>python3 scripts/build_console.py</code>.</footer>
</main></body></html>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate without writing; fail if HTML is stale")
    args = parser.parse_args()
    try:
        tables = load_tables()
        expected = render(tables[0])
        if args.check:
            if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
                fail("HTML is missing or stale; run python3 scripts/build_console.py")
        else:
            OUTPUT.write_text(expected, encoding="utf-8")
        counts = ", ".join(str(len(table)) for table in tables)
        print(f"OK: current/archive/hired = {counts}; CSV, directories and HTML are consistent.")
    except (ValueError, OSError, csv.Error) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
