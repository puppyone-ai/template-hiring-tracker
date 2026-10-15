# Technical exercise: fictional task query assistant

> Generic example, unrelated to any company's business or internal systems. Before use, the recruiting team must fill in expected effort, deadline, and submission method.

## Scenario

Build a task query assistant for a fictional team. This is the complete sample dataset:

| Task ID | Project | Status | Priority |
| --- | --- | --- | --- |
| T-001 | Sample Project Blue | Pending | High |
| T-002 | Sample Project Blue | In progress | Medium |
| T-003 | Sample Project Green | Completed | Low |
| T-004 | Sample Project Green | Pending | Medium |

## Requirements

1. Provide a runnable command line or simple interface that queries project, status, and priority, returning task IDs and the basis for results.
2. Answer "Which tasks are pending?" and "Which tasks belong to Sample Project Blue?" Handle nonexistent projects, unknown fields, and empty results explicitly; do not invent tasks.
3. Keep the source dataset read-only. Any additional test data must also be fictional.
4. Submit running instructions, key tests, and a short explanation of tradeoffs. Rules or a model are both acceptable; explain your choice. Read external-service configuration from the environment and never commit keys.
5. Describe AI assistance and the checks you performed yourself.

Suggested effort: {{Duration}}. Submission deadline: {{Date, time, and time zone}}. Submission method: {{Confirmed private entry}}.

No real business-system integration is required. Do not use private code or data from former employers, clients, or third parties.
