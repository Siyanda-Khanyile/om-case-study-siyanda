"""Facts about Terraform's JSON formats, kept in one place.

Sources: the plan/state representation in `terraform show -json` and the
Terraform JSON configuration syntax.
"""

# Block types allowed at the top level of Terraform's JSON configuration syntax.
HCL_JSON_BLOCKS = frozenset({
    "terraform", "provider", "resource", "data", "module", "variable",
    "output", "locals", "moved", "import", "check", "removed",
})

# A top-level block body is an object, or an array when the block repeats.
BLOCK_BODY_TYPES = (dict, list)

# Actions Terraform may list in resource_changes[].change.actions.
PLAN_ACTIONS = frozenset({"no-op", "create", "read", "update", "delete"})

# Keys that identify a plan representation rather than a state representation.
PLAN_MARKER_KEYS = frozenset({
    "planned_values", "resource_changes", "resource_drift", "configuration", "applyable",
})

# Plan/state wire-format major version this package understands.
SUPPORTED_FORMAT_MAJOR = 1

# Required fields on each resource_changes entry.
RESOURCE_CHANGE_FIELDS = ("address", "type", "name")
