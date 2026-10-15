# Fields and statuses

## Three tables

- Current: `00-console/candidates.csv`, the source of truth for active stages and human decisions.
- Archived: `90-archive/archived-candidates.csv`, with stage `Archived`.
- Hired: `91-hired/hired-candidates.csv`, with both stage and decision `Hired`.
- HTML displays the current table only. All CSV files use UTF-8 and the same column order.

```text
sequence,candidate_id,name,role,school,source,intake_date,stage,human_decision,ai_recommendation,role_id,candidate_directory,updated_at
```

| Field | Convention |
| --- | --- |
| sequence | Consecutive numbers starting at 1 within each table; not a stable ID |
| candidate_id | `C-YYYYMM-NNN`; unique across all three tables and retained permanently |
| name | Verified from a reliable source; public examples use explicit fictional labels such as Sample Candidate A |
| role | Matches the role card; its lowercase hyphenated slug is the active directory's middle level |
| school | Record verified information only; use Needs verification when unknown; sample institutions are fictional |
| source | Public examples use Sample application; define actual channels in a private copy |
| intake_date | `YYYY-MM-DD`; do not change after initial intake |
| stage | A controlled value below; real transitions require human confirmation |
| human_decision | May be empty; requires human confirmation; nonempty example values are fictional |
| ai_recommendation | Starts with `AI suggestion: ` and never replaces a human decision |
| role_id | `J-YYYYMM-CODE`; requires an existing role card |
| candidate_directory | Path relative to the repository root; no absolute local paths |
| updated_at | `YYYY-MM-DD`; latest substantive update |

## Controlled values

Stages: `Pending confirmation`, `Received`, `Awaiting screening`, `Awaiting first interview scheduling`, `First interview`, `Awaiting second interview scheduling`, `Second interview`, `Awaiting third interview scheduling`, `Third interview`, `Awaiting decision`, `Offer discussion`, `Awaiting start`, `Hired`, `Paused`, `Closed`, `Archived`.

Human decisions: empty, `Advance`, `Do not advance`, `Rejected`, `Withdrawn`, `Offer declined`, `Offer accepted`, `Hired`.

`Do not advance` is the explicit replacement for the former decision "pass", which meant stop rather than proceed. Ask for clarification if a human uses ambiguous language.

Archived decisions are limited to `Do not advance`, `Rejected`, `Withdrawn`, and `Offer declined`. Hired records use `Hired`. Leave unresolved cases in the current table rather than ending the process automatically.

## Ordering and relationships

Group each table by role ID and sort by candidate ID within each role. Insert one blank row between role groups. Blank rows do not count as candidates.

Example dates use `2030-01` only to show sequence, not current recruiting activity. Allocate new IDs using the actual intake month in a private copy, checking all three tables.
