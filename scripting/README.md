# Scripting — should this `terraform apply` proceed?

`script.py` takes a Terraform plan converted to JSON, parses it, and decides
whether the apply should proceed.

## The two checks

| Check | Rule | Fails when |
|-------|------|-----------|
| 1 | The plan must only contain **create** or **modify** steps | a resource is destroyed, or destroyed-and-recreated (a replacement) |
| 2 | A **modify** may only change the resource's `tags` attribute, and within it only the **`GitCommitHash`** tag | a modify changes any other attribute, or any other tag |

If either check fails the decision is **DO NOT PROCEED**, and the action
required to fix each offending resource is printed.

## How to run

Requires Python 3 (tested on 3.9). No installation, no third-party packages.

```bash
cd scripting
python3 script.py tfplan-1.json       # check one plan file
```

Any filename works — `.json` or `.tfplan`. Other forms:

```bash
python3 script.py                     # check every plan file in this folder
python3 script.py --steps tfplan-3.json   # also list every step and its result
python3 /full/path/to/script.py tfplan-1.json   # runs from any directory
```

## Exit codes

| Code | Meaning |
|------|---------|
| `0`  | PROCEED — the apply may run |
| `1`  | DO NOT PROCEED, or the file could not be read as a plan |

Usable directly as a gate:

```bash
python3 script.py tfplan.json && terraform apply tfplan
```

## Example output

```
$ python3 script.py tfplan-1.json
tfplan-1.json
  DECISION: PROCEED

$ python3 script.py tfplan-3.json
tfplan-3.json
  DECISION: DO NOT PROCEED

  Action required:
    1. module.aihub.azapi_resource.hub
       Restore those tags to their previous values; only the GitCommitHash tag may change.
    2. module.aihub.azapi_resource.project
       Revert the change to body so this step only updates the GitCommitHash tag.
```

With `--steps`, every step is listed with its result, so the decision can be
checked by hand:

```
$ python3 script.py --steps tfplan-3.json
tfplan-3.json
  7 step(s):
    no-op    module.aihub.azapi_resource.AISearchServices             ok
    no-op    module.aihub.azapi_resource.AISearchServicesConnection   ok
    no-op    module.aihub.azapi_resource.AIServicesConnection         ok
    no-op    module.aihub.azapi_resource.AIServicesResource           ok
    update   module.aihub.azapi_resource.hub                          FAIL (rule 2) changes 3 tag(s) other than GitCommitHash
    update   module.aihub.azapi_resource.project                      FAIL (rule 2) changes body
    no-op    module.aihub.random_string.suffix                        ok

  DECISION: DO NOT PROCEED
  ...
```

## Results for the supplied files

| File | Decision | Why |
|------|----------|-----|
| `tfplan-1.json` | PROCEED | a single create step |
| `tfplan-2.json` | PROCEED | no steps to apply |
| `tfplan-3.json` | DO NOT PROCEED | `hub` changes three `__SYSTEM__*` tags instead of `GitCommitHash`; `project` changes `body` |
| `dummy.json` | CANNOT CHECK | not a Terraform plan (a deliberate negative case) |

Check 1 never fires on these three files — none of them destroys anything. It
was verified against plans containing a destroy and a replacement.

## The functions

| Function | Purpose |
|----------|---------|
| `load_plan(path)` | Read and parse the file; returns `(document, error)` |
| `plan_steps(doc)` | The plan's `resource_changes` |
| `step_actions(step)` | What a step does: `("create",)`, `("delete","create")`… |
| `check_only_create_or_modify(doc)` | **Check 1** → `(passed, failures)` |
| `changed_attributes(step)` | Attributes really changed, ignoring computed ones |
| `changed_tags(step)` | Tags other than `GitCommitHash` that change |
| `check_modify_only_changes_commit_tag(doc)` | **Check 2** → `(passed, failures)` |
| `decide(doc)` | Runs both checks and returns the decision plus actions |

## Decisions worth knowing

- **A replacement is a destroy.** Terraform writes it as `["delete","create"]`
  (either order), so a test for "contains create" would wave it through. It is
  matched explicitly and blocked.
- **`no-op` and `read` steps are allowed** — they change no infrastructure.
- **Computed values are ignored.** Terraform lists values known only after
  apply in `after_unknown`; these change on nearly every plan (`output`,
  computed ids). Counting them would block every legitimate tag-only change.
- **Unverifiable tags fail closed.** If the whole `tags` value is unknown until
  apply, the rule cannot be proven, so the plan is blocked rather than assumed
  safe.
