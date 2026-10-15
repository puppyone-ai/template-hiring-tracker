# Recruit Template Version

A lightweight recruiting workspace for people and AI assistants. Keep roles, candidate profiles, and interview notes in Markdown, track stages in CSV, and browse candidates in a local HTML view. No database, account, or online service is required.

> **Public template. All examples are fictional.** People, schools, projects, dates, communications, and hiring outcomes were written specifically for this demonstration and do not correspond to real recruiting records. Example email addresses use `example.com`. No real resumes, contact details, interview evaluations, platform exports, internal links, or private repository history are included.

## Quick start

1. Copy this template into your own **private workspace**. Use the public repository to maintain the template; keep real recruiting materials separately.
2. Choose or create a role in the [role directory](01-roles/README.md). Fill in the job description, role card, and screening criteria. Replace every `{{...}}` placeholder before use.
3. Explore the [fictional candidates](02-candidates/README.md), then create records with the [candidate card template](03-process-templates/9-candidate-card.md). Before adding real candidates to a private copy, remove the fictional rows from all three CSV files and remove their example folders. Keep the CSV headers.
4. Maintain current stages in the [candidate table](00-console/candidates.csv) and next actions in [hiring todos](00-console/hiring-todos.md). Keep AI suggestions separate from human decisions.
5. Open the [candidate browser](00-console/candidates.html) locally. After editing the CSV, regenerate the HTML using Python 3.9 or later; only the standard library is needed:

   ```sh
   python3 scripts/build_console.py
   python3 scripts/build_console.py --check
   ```

You can edit CSV and Markdown without Python. The HTML is a derived view and must be regenerated after CSV changes.

## Workspace guide

| Directory | Contents |
| --- | --- |
| [00-console](00-console/candidates.csv) | Current candidates, HTML browser, todos, and sync log |
| [01-roles](01-roles/README.md) | Generic design, engineering, and operations roles |
| [02-candidates](02-candidates/README.md) | Fictional candidate cards, sample materials, and communication logs grouped by role |
| [03-process-templates](03-process-templates/9-recruiting-process.md) | Outreach, interviews, rejections, offers, candidate cards, and record templates |
| [04-assessments](04-assessments/candidate-exercise.md) | Generic technical exercise and separate reviewer guide |
| [05-boss-zhipin](05-boss-zhipin/README.md) | Channel record conventions and a blank intake log |
| [90-archive](90-archive/README.md) | Fictional closed applications without a hire |
| [91-hired](91-hired/README.md) | Fictional hired-candidate example |
| [99-system-rules](99-system-rules/human-ai-collaboration.md) | Fields, stages, naming, sync, and public-template maintenance rules |

## Daily workflow

1. Confirm the role and source scope, then check that the supplied materials are readable.
2. Check current, archived, and hired records together to avoid duplicate profiles.
3. Allocate a unique candidate ID and create `02-candidates/<role-slug>/<candidate-slug>/`. Preserve original materials in the private workspace and cite their sources.
4. AI may organize facts, flag missing evidence, and draft questions. A person confirms progression, interview conclusions, and stage changes.
5. Update the CSV first, then regenerate HTML. Keep communication dates and next actions in todos or communication logs.
6. After human confirmation, move closed applications to the archive and hired candidates to the hired directory. Remove both from the current table.

See [AGENTS.md](AGENTS.md) and the [recruiting process](03-process-templates/9-recruiting-process.md) for full rules. Use the explicit decision `Do not advance` rather than the ambiguous word "pass"; see [fields and statuses](99-system-rules/fields-and-statuses.md).

## Maintaining the public template

Follow the [public-template maintenance rules](99-system-rules/public-template-maintenance.md). Reuse structure and workflows, and write fictional examples independently. Replacing names alone does not anonymize a real record. `.gitignore` is only a supporting measure; review staged content, filenames, links, and Git history before publication.

This repository retains its original [LICENSE](LICENSE).
