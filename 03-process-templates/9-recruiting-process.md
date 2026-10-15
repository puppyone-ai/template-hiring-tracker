# Recruiting process

```text
Received -> Awaiting screening -> Awaiting first interview scheduling
         -> First interview -> Awaiting second interview scheduling
         -> Second interview -> Awaiting decision -> Offer discussion
         -> Awaiting start -> Hired (move to 91-hired)

Human-confirmed end without a hire -> Archived (move to 90-archive)
```

Add a third interview when the role requires it, or pause while awaiting verification. Use the controlled values in [fields and statuses](../99-system-rules/fields-and-statuses.md). Do not add an unnecessary interview round.

## Every transition

1. Record the facts, timing, evidence, and human confirmation.
2. Update stage and human decision in the table. AI must not decide the outcome independently.
3. Record follow-up actions and dates in the communication log or hiring todos.
4. Regenerate HTML and check paths, counts, and field consistency.

## Closing an application

After human confirmation of `Do not advance`, `Rejected`, `Withdrawn`, or `Offer declined`, and within the authorized scope, write the full row to the archive table, set stage to `Archived`, and move the folder to `90-archive/<candidate-slug>/`. After human confirmation of a hire, write the row to the hired table, set both stage and decision to `Hired`, and move the folder to `91-hired/<candidate-slug>/`.

Finish the destination record and folder before removing the current row and renumbering. Repair relative links and regenerate HTML. Preserve candidate ID and original intake date.

These changes do not automatically send emails, update a platform, or publish materials.
