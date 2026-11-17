# Contributing

This document describes the contribution conventions used in this repository. It is intended to grow alongside the project; additional guidance for branching, pull requests, code review, and automation can be added as those workflows are adopted.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages.

### Format

```text
<type>(<scope>): <description>
```

- **type** describes the kind of change.
- **scope** identifies the area of the project affected. It is recommended when it adds useful context.
- **description** briefly summarizes the change.

Use lowercase for the type, scope, and description. Do not end the subject with a period. Prefer a concise, imperative description, such as `add`, `update`, `remove`, or `correct`.

### Commit types

| Type | Use it for | Example |
| --- | --- | --- |
| `feat` | A new capability or user-facing behavior | `feat(airflow): add full refresh DAG` |
| `fix` | A bug fix | `fix(spark): correct timestamp parsing` |
| `refactor` | Code or structure changes that do not change external behavior | `refactor(infrastructure): reorganize database directories` |
| `docs` | Documentation changes | `docs(architecture): describe Airflow integration` |
| `test` | Adding or changing tests | `test(silver): add data quality checks` |
| `chore` | Maintenance that does not fit a more specific type, such as housekeeping | `chore(repo): remove obsolete files` |
| `build` | Build system, container image, or build dependency changes | `build(docker): update Spark image` |
| `ci` | Continuous integration and delivery configuration | `ci(github): add validation workflow` |

Choose the type that best describes the primary purpose of the commit. Do not use `chore` as a catch-all when a more specific type applies.

### Scopes

Use short, consistent names for the affected project area. Suggested scopes include:

- `infrastructure` — Docker Compose and shared infrastructure configuration.
- `airflow` — Airflow DAGs and Airflow-specific configuration.
- `spark` — Spark jobs and Spark configuration.
- `iceberg` — Iceberg tables, catalog behavior, and metadata.
- `minio` — Object storage configuration and related tooling.
- `sql` — SQL queries and scripts.
- `tests` — Test infrastructure and test cases.
- `docs` — General project documentation.

Scopes are guidance, not a closed list. Use a more specific scope when it improves clarity.

### Examples

```text
feat(airflow): add full refresh DAG
fix(spark): correct decimal conversion
refactor(infrastructure): reorganize database directories
chore(deps): update Python dependencies
docs(architecture): describe Airflow integration
test(silver): add data quality checks
```

### Commit body and footers

For changes that need more context, add a body separated from the subject by a blank line. Explain **what** changed and **why**, rather than repeating the subject.

```text
refactor(infrastructure): reorganize database directories

- Move Iceberg PostgreSQL initialization scripts.
- Update the Docker Compose bind-mount path.
- Keep the existing PostgreSQL volume unchanged.
```

Use Conventional Commits footers when relevant. In particular, mark incompatible changes with `BREAKING CHANGE: <description>` in the footer. A breaking change may also use an exclamation mark before the colon, for example `feat(api)!: change response format`.

## Before committing

Review the working tree and the staged changes before creating a commit:

```powershell
git status
git diff --check
git diff
git diff --cached
```

Check that the commit contains only files related to the intended change. In particular, do not commit:

- `.env` files, credentials, passwords, tokens, or private keys;
- database dumps or backups unless their inclusion is explicitly intended and reviewed;
- local data, generated output, caches, or temporary files;
- unrelated changes.

If a file is already staged, inspect it with `git diff --cached`; `git diff` alone does not show staged changes.

## Keeping this guide current

This is the initial contribution guide. Branch naming, pull request structure, review expectations, and automated checks will be documented here as the project adopts those practices.
