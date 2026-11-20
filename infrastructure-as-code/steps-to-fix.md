# Deleting the 2nd resource without touching the other four

The task was to delete the second of five files — `file1.txt`, managed by
`local_file.foo[1]` — and leave `file0`, `file2`, `file3` and `file4` exactly
as they were. The same approach works for any of them; you just leave a
different number out.

## The problem with `count`

`count` numbers resources by position. `local_file.foo[1]` doesn't mean "the
resource that owns file1.txt" — it means "whatever happens to be sitting in
slot 1". Terraform can only add or remove slots at the end of that list, so
there's no way to say "drop the middle one".

You can see it happen. Lowering the count to 4 removes the wrong file:

```
$ terraform plan -var 'files=4'
  # local_file.foo[4] will be destroyed
Plan: 0 to add, 0 to change, 1 to destroy.
```

That deletes `file4.txt`, not `file1.txt`.

And you can't leave a hole in the middle either. If you take `foo[1]` out of
state and plan again, Terraform immediately fills the gap back in:

```
  # local_file.foo[1] will be created
  # local_file.foo[4] will be destroyed
Plan: 1 to add, 0 to change, 1 to destroy.
```

The other option — deleting `file1.txt` by hand and shuffling the rest up a
slot — is worse than it looks. Every remaining file would land on a different
index, so its `filename` would change, and Terraform would destroy and
recreate three perfectly good files to get there.

What's really wrong here is that these resources are identified by *where they
sit* rather than by *what they are*. Fixing that is the whole solution.

## The fix, in three steps

### 1. Give each file a name instead of a position

Switch the resource from `count` to `for_each`, keyed by the number in the
filename. Before:

```hcl
variable "files" {
  default = 5
}

resource "local_file" "foo" {
  count    = var.files
  content  = "# Some content for file ${count.index}"
  filename = "file${count.index}.txt"
}
```

After:

```hcl
variable "files" {
  type    = set(string)
  default = ["0", "2", "3", "4"]   # no "1" — that's the file being deleted
}

resource "local_file" "foo" {
  for_each = var.files
  content  = "# Some content for file ${each.key}"
  filename = "file${each.key}.txt"
}
```

The key is the number in the filename, so `each.key` builds exactly the same
`content` and `filename` these files already have. Nothing about the files
themselves changes — only how Terraform refers to them. Deleting a file is now
just removing its key from that list.

The addresses do change, though: `local_file.foo[0]` becomes
`local_file.foo["0"]`. Terraform needs to be told about that, which is step 2.

### 2. Tell Terraform the resources moved

Skip this and Terraform sees four addresses it doesn't recognise plus four
orphans, and cheerfully destroys and recreates all of them. A `moved` block for
each survivor prevents that:

```hcl
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
```

There's deliberately no block for `local_file.foo[1]`. It isn't in the new
configuration and nothing claims it, so Terraform destroys it — which is the
deletion we're after.

You can do the same thing from the command line:

```bash
terraform state mv 'local_file.foo[0]' 'local_file.foo["0"]'
terraform state mv 'local_file.foo[2]' 'local_file.foo["2"]'
terraform state mv 'local_file.foo[3]' 'local_file.foo["3"]'
terraform state mv 'local_file.foo[4]' 'local_file.foo["4"]'
```

I went with `moved` blocks because they're committed with the change, get
reviewed alongside it, and run themselves for anyone else who applies the
configuration. `state mv` only fixes the machine you run it on, so the next
person hits the same migration by hand.

### 3. Check the plan, then apply

```bash
terraform init
terraform plan
```

You want four moves, one destroy, and nothing created or changed:

```
  # local_file.foo[1] will be destroyed
  # local_file.foo[0] has moved to local_file.foo["0"]
  # local_file.foo[2] has moved to local_file.foo["2"]
  # local_file.foo[3] has moved to local_file.foo["3"]
  # local_file.foo[4] has moved to local_file.foo["4"]
Plan: 0 to add, 0 to change, 1 to destroy.
```

If anything shows up as "to add" or "to change", stop — it means a key doesn't
line up with the value it had under `count`.

Then apply:

```bash
terraform apply
```

```
local_file.foo[1]: Destroying... [id=2e6d03ed1e47ed0cd076e718e721994f1b882f52]
local_file.foo[1]: Destruction complete after 0s

Apply complete! Resources: 0 added, 0 changed, 1 destroyed.
```

## Confirming it's clean

Run `terraform apply` once more. It should have nothing left to do:

```
Terraform has compared your real infrastructure against your configuration
and found no differences, so no changes are needed.

Apply complete! Resources: 0 added, 0 changed, 0 destroyed.
```

The end result:

```
$ ls file*.txt
file0.txt  file2.txt  file3.txt  file4.txt

$ terraform state list
local_file.foo["0"]
local_file.foo["2"]
local_file.foo["3"]
local_file.foo["4"]
```

`file1.txt` is gone and the other four were never rewritten — same contents,
same modification timestamps, and the same resource IDs in state as before.
That last part is the real proof: matching IDs mean Terraform carried the same
objects across rather than quietly replacing them.

## One last thing

Once everyone has applied this, the `moved` blocks have served their purpose
and can be deleted. Leaving them in does no harm.

And deleting a file from now on is a one-line change — no `moved` blocks, no
state commands. To drop `file3.txt`:

```hcl
default = ["0", "2", "4"]
```

`terraform plan` will report exactly one resource to destroy.
