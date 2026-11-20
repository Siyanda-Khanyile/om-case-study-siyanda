variable "files" {
  description = <<-DESC
    The files to manage, identified by the number in their name.

    This is a set of strings rather than a count, so each file has a stable
    identity of its own. Removing an entry affects only that file; the others
    keep their addresses and are left untouched.
  DESC
  type        = set(string)
  default     = ["0", "2", "3", "4"]
}

resource "local_file" "foo" {
  for_each = var.files
  content  = "# Some content for file ${each.key}"
  filename = "file${each.key}.txt"
}

# Carry the existing resources from their count addresses to their for_each
# addresses, so Terraform tracks them as the same objects instead of destroying
# and recreating them. local_file.foo[1] is deliberately absent: it is the
# resource being deleted.
moved {
  from = local_file.foo[0]
  to   = local_file.foo["0"]
}

moved {
  from = local_file.foo[2]
  to   = local_file.foo["2"]
}

moved {
  from = local_file.foo[3]
  to   = local_file.foo["3"]
}

moved {
  from = local_file.foo[4]
  to   = local_file.foo["4"]
}
