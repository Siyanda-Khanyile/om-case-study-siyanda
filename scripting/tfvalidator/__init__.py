"""Validation of Terraform JSON documents (plans, state, config, schemas).

Layering (dependencies point inwards only):

    interface      -> application -> domain
    infrastructure -> domain

`domain` holds the Terraform rules and performs no I/O, `infrastructure` does
the file access, `application` wires them into a use case, and `interface`
renders the result for a human.
"""
