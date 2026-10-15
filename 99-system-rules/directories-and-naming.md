# Directories and naming

| Directory | Purpose |
| --- | --- |
| `00-console/` | Current table, browser, todos, and short sync log |
| `01-roles/` | `<role-id>-<English-Role-Name>/`, with JD, role card, and screening criteria |
| `02-candidates/` | `<role-slug>/<candidate-slug>/`; append the candidate ID for a same-name collision |
| `03-process-templates/` | Reusable blank documents and workflows |
| `04-assessments/` | Candidate exercise and separate reviewer template |
| `05-boss-zhipin/` | Channel conventions and intake-log template |
| `90-archive/` | `<candidate-slug>/`, closed applications without a hire and their table |
| `91-hired/` | `<candidate-slug>/`, confirmed hires and their table |
| `99-system-rules/` | Collaboration, fields, naming, sync, and public-template rules |

Create slugs by lowercasing the English display name, replacing runs of non-alphanumeric characters with hyphens, and trimming leading or trailing hyphens. For example, `Product Designer` becomes `product-designer` and `Sample Candidate A` becomes `sample-candidate-a`. For a same-name collision, append the unchanged candidate ID after a hyphen.

Active candidate cards link to the current table with `../../../00-console/candidates.csv`. Archived and hired cards link to their respective table one directory up. Repair card links, CSV paths, and HTML after moving a folder.

Do not use hiring stages as directory levels. Keep active folders stable until a person confirms archival or a hire.

Recommended files: `candidate-card.md`, `interview-questions.md`, `communication-log.md`, and `first-interview-YYYY-MM-DD.md`. Mark unknown information Needs verification and unconfirmed documents Draft. Use `YYYY-MM-DD` dates and relative links.

Public source materials use `sample-background.md` with a clear fictional label. They contain no real attachments or attachment filenames. Original-file preservation rules apply only in a separate private workspace.
