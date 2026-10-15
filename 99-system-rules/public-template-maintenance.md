# Maintaining the public template

## Suitable public content

- Directory structure, fields, controlled stages, and generic workflows.
- Rewritten role, email, interview, and record templates.
- Independently authored and clearly labeled fictional people, projects, dates, and outcomes.
- Example email addresses and URLs under `example.com`; `{{...}}` placeholders for company, location, compensation, contacts, and formal terms.

## Private materials

Keep real resumes, portfolios, photos, contacts, platform cards and IDs, email text, interview evaluations, compensation, addresses, internal booking or onboarding links, sending payloads, automation logs, and local paths in the private workspace. Do not copy them into the public repository and redact them afterward.

**Replacing names alone is insufficient.** Schools, work history, project descriptions, timelines, evaluation wording, and attachment names may identify someone in combination. Public examples must not correspond one-to-one with real people. Rewrite those fields independently, and omit anything whose public status is uncertain.

Do not import a private repository's `.git` directory, commits, branches, tags, issues, or remote configuration. Public PR titles, descriptions, screenshots, and logs must not expose that material either.

## Before publishing

1. Review `git status --short`, the staged file list, and the complete staged diff. Include only intended template files.
2. Inspect filenames, text, CSV, HTML, links, images, attachments, and metadata. Exclude real materials and platform exports.
3. Check emails, phone numbers, platform IDs, external URLs, absolute paths, company personnel, and internal terms. Example addresses must use reserved example domains.
4. Inspect outgoing commits and their history. Removing a working file does not remove sensitive content from an earlier commit.
5. Run `python3 scripts/build_console.py --check` and `git diff --check`; confirm that tables, directories, links, and HTML agree.
6. Publish fictional template content only. If real information has been published, stop further publication and notify the repository maintainer.

`.gitignore` and scripts cannot identify all sensitive information, especially indirect identity clues in narrative histories. Human review remains necessary.
