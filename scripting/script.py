#!/usr/bin/env python3
"""Decide whether `terraform apply` should proceed for a plan file.

The plan (a `terraform show -json` plan converted to JSON) is checked against
two rules, taken from the case study:

    Check 1 - the plan must only contain create or modify steps.
    Check 2 - a modify step must only change the resource's `tags` attribute,
              and within it only the `GitCommitHash` tag.

If either check fails the apply must not proceed, and the action required to
fix each offending resource is printed.

Usage:
    python3 script.py tfplan-1.json      # check one plan file
    python3 script.py                    # check each plan file in this folder
    python3 script.py --steps tfplan.json   # also list every step and its result

Exit code: 0 if the apply may proceed, 1 if it must not.
"""

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# Files picked up when no file is named. The case study calls them "*.tfplan";
# the supplied ones are named "tfplan-*.json".
PLAN_SUFFIXES = (".json", ".tfplan")

# The only attribute a modify may change, and the only tag within it.
ALLOWED_ATTRIBUTE = "tags"
ALLOWED_TAG = "GitCommitHash"

# Step actions that are permitted by Check 1. "no-op" and "read" change no
# infrastructure, so they are not treated as changes.
CREATE = ("create",)
MODIFY = ("update",)
HARMLESS = (("no-op",), ("read",))


# ==========================================================================
# Reading the plan
# ==========================================================================

def load_plan(path):
    """Read a plan file. Returns `(document, error message)`.

    Errors are returned rather than raised so the caller can report them
    cleanly instead of showing a traceback.
    """
    try:
        with Path(path).open(encoding="utf-8") as handle:
            document = json.load(handle)
    except OSError as error:
        return None, "cannot read file: %s" % (error.strerror or error)
    except UnicodeDecodeError:
        return None, "the file is not UTF-8 text"
    except json.JSONDecodeError as error:
        return None, "the file is not valid JSON: %s (line %d, column %d)" % (
            error.msg, error.lineno, error.colno)

    if not isinstance(document, dict) or "format_version" not in document:
        return None, "this is not a Terraform plan in JSON form"
    if not ({"planned_values", "resource_changes", "configuration", "applyable"}
            & set(document)):
        return None, "this is Terraform data, but not a plan"
    return document, None


def plan_steps(document):
    """The plan's steps (its `resource_changes`), or an empty list."""
    steps = document.get("resource_changes")
    return steps if isinstance(steps, list) else []


def step_actions(step):
    """What this step does, as a tuple: ("create",), ("delete", "create")..."""
    return tuple((step.get("change") or {}).get("actions") or ())


# ==========================================================================
# Check 1 - the plan must only contain create or modify steps
# ==========================================================================

def check_only_create_or_modify(document):
    """Check 1. Returns `(passed, failures)`.

    A destroy or a replacement fails. A replacement is listed by Terraform as
    `["delete", "create"]` (in either order), so it is matched explicitly: a
    test for "does it contain create?" would let a destroy through.
    """
    failures = []

    for step in plan_steps(document):
        actions = step_actions(step)
        if actions in (CREATE, MODIFY) or actions in HARMLESS:
            continue

        address = step.get("address") or "(unknown resource)"
        if set(actions) == {"create", "delete"}:
            failures.append({
                "address": address,
                "action": "Revert the change that forces replacement, or "
                          "replace this resource separately with approval.",
            })
        elif actions == ("delete",):
            failures.append({
                "address": address,
                "action": "Restore this resource in the configuration, or "
                          "destroy it separately with approval.",
            })
        else:
            failures.append({
                "address": address,
                "action": "Only create and modify steps are allowed; review "
                          "this step by hand.",
            })

    return not failures, failures


# ==========================================================================
# Check 2 - a modify may only change tags.GitCommitHash
# ==========================================================================

def changed_attributes(step):
    """The attributes this step really changes.

    Values that Terraform will only know after the apply are skipped. They are
    listed in `after_unknown` and change on almost every plan (computed ids,
    ARNs, outputs), so counting them would block every legitimate tag-only
    change. Only an entry of exactly `true` is wholly unknown; a nested object
    means part of the value is genuinely being set.
    """
    detail = step.get("change") or {}
    before = detail.get("before") if isinstance(detail.get("before"), dict) else {}
    after = detail.get("after") if isinstance(detail.get("after"), dict) else {}
    unknown = detail.get("after_unknown") or {}

    names = set(before) | set(after) | set(k for k, v in unknown.items() if v)
    return set(name for name in names
               if unknown.get(name) is not True and before.get(name) != after.get(name))


def changed_tags(step):
    """Tags other than GitCommitHash whose value this step changes."""
    detail = step.get("change") or {}
    before = (detail.get("before") or {}).get(ALLOWED_ATTRIBUTE)
    after = (detail.get("after") or {}).get(ALLOWED_ATTRIBUTE)
    before = before if isinstance(before, dict) else {}
    after = after if isinstance(after, dict) else {}

    return sorted(tag for tag in set(before) | set(after)
                  if tag != ALLOWED_TAG and before.get(tag) != after.get(tag))


def check_modify_only_changes_commit_tag(document):
    """Check 2. Returns `(passed, failures)`.

    Only modify steps are examined; creates are allowed to set anything.
    """
    failures = []

    for step in plan_steps(document):
        if step_actions(step) != MODIFY:
            continue

        address = step.get("address") or "(unknown resource)"
        changed = changed_attributes(step)

        other = sorted(changed - {ALLOWED_ATTRIBUTE})
        if other:
            failures.append({
                "address": address,
                "action": "Revert the change to %s so this step only updates "
                          "the %s tag." % (name_list(other), ALLOWED_TAG),
            })
            continue

        # Checked before "did tags change?": tags that are wholly unknown were
        # skipped above as computed, so the rule cannot be confirmed either way.
        if (step.get("change") or {}).get("after_unknown", {}).get(ALLOWED_ATTRIBUTE) is True:
            failures.append({
                "address": address,
                "action": "Resolve the unknown tag values, or apply this "
                          "resource separately with approval.",
            })
            continue

        if ALLOWED_ATTRIBUTE not in changed:
            continue

        offending = changed_tags(step)
        if offending:
            failures.append({
                "address": address,
                "action": "Restore those tags to their previous values; only "
                          "the %s tag may change." % ALLOWED_TAG,
            })

    return not failures, failures


# ==========================================================================
# The decision
# ==========================================================================

def decide(document):
    """Run both checks. Returns `{"proceed": bool, "actions": [...]}`."""
    create_or_modify_ok, step_failures = check_only_create_or_modify(document)
    tags_ok, tag_failures = check_modify_only_changes_commit_tag(document)

    return {
        "proceed": create_or_modify_ok and tags_ok,
        "actions": step_failures + tag_failures,
    }


# ==========================================================================
# Output
# ==========================================================================

def name_list(names, limit=3, width=34):
    """Render a list of names, capping the count and shortening long ones."""
    shown = [n if len(n) <= width else n[:width - 1] + "…" for n in names[:limit]]
    text = ", ".join(shown)
    if len(names) > limit:
        text += " and %d more" % (len(names) - limit)
    return text


def step_verification(step):
    """How one step fares against each rule: (action, rule 1, rule 2)."""
    actions = step_actions(step)
    action = "/".join(actions) or "none"

    rule1 = "OK" if actions in (CREATE, MODIFY) or actions in HARMLESS else "FAIL"

    if actions != MODIFY:
        return action, rule1, "n/a (not a modify)"

    other = sorted(changed_attributes(step) - {ALLOWED_ATTRIBUTE})
    if other:
        return action, rule1, "FAIL changes %s" % name_list(other)
    if (step.get("change") or {}).get("after_unknown", {}).get(ALLOWED_ATTRIBUTE) is True:
        return action, rule1, "FAIL tags unknown until apply"
    offending = changed_tags(step)
    if offending:
        return action, rule1, "FAIL changes %d tag(s) other than %s" % (
            len(offending), ALLOWED_TAG)
    return action, rule1, "OK"


def print_steps(document, stream):
    """List every step in the plan with its result against both rules."""
    steps = plan_steps(document)
    if not steps:
        stream.write("  no steps (neither rule can be broken)\n\n")
        return

    width = max(len(step.get("address", "?")) for step in steps)
    stream.write("  %d step(s):\n" % len(steps))
    for step in steps:
        action, rule1, rule2 = step_verification(step)
        if rule1 != "OK":
            result = "FAIL (rule 1) %s" % rule1_reason(step)
        elif rule2.startswith("FAIL"):
            result = "FAIL (rule 2) %s" % rule2[5:]
        else:
            result = "ok"
        stream.write("    %-8s %-*s   %s\n"
                     % (action, width, step.get("address", "?"), result))
    stream.write("\n")


def rule1_reason(step):
    """Why a step fails rule 1."""
    actions = step_actions(step)
    if set(actions) == {"create", "delete"}:
        return "destroys and recreates this resource"
    if actions == ("delete",):
        return "destroys this resource"
    return "not a create or modify step"


def print_decision(path, steps=False, stream=None):
    """Check one plan file and print the decision. Returns True if it may apply."""
    stream = stream or sys.stdout
    document, error = load_plan(path)

    stream.write("%s\n" % Path(path).name)

    if error is not None:
        stream.write("  CANNOT CHECK - %s\n\n" % error)
        return None

    if steps:
        print_steps(document, stream)

    outcome = decide(document)
    if outcome["proceed"]:
        stream.write("  DECISION: PROCEED\n\n")
        return True

    stream.write("  DECISION: DO NOT PROCEED\n")
    stream.write("\n  Action required:\n")
    for number, failure in enumerate(outcome["actions"], start=1):
        stream.write("    %d. %s\n" % (number, failure["address"]))
        stream.write("       %s\n" % failure["action"])
    stream.write("\n")
    return False


# ==========================================================================
# Entry point
# ==========================================================================

def list_plan_files(directory=SCRIPT_DIR):
    """Plan files sitting directly in `directory`, sorted by name."""
    directory = Path(directory).resolve()
    return sorted((entry for entry in directory.iterdir()
                   if entry.is_file() and entry.suffix.lower() in PLAN_SUFFIXES),
                  key=lambda entry: entry.name)


def main(argv=None):
    """Check the named plan file, or every plan file in this folder."""
    argv = list(sys.argv[1:] if argv is None else argv)
    steps = "--steps" in argv
    paths = [Path(arg) for arg in argv if not arg.startswith("-")]

    if not paths:
        paths = list_plan_files()
        if not paths:
            print("No plan files found in %s" % SCRIPT_DIR)
            return 0

    results = [print_decision(path, steps=steps) for path in paths]
    return 0 if all(result is True for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
