# Case Study 

This case study consists of 4 parts, and the themes are as follows:

- Containers
- Infrastructure as Code
- Scripting
- Extra

They are each designed to asses the capability with the given theme or concept.

Containers -> Docker, Containerisation 

IAC -> Terraform, infrastructure mananegment, declaritive configuration code

Scripting -> general scripting automation

Extra -> a (Hopefully) new problem and domain, that will be used to assess novel problem solving, information gathering and synthethis, and execution of new knowledge


Knowledge and tools required to complete:
- Git
- Docker
- Terraform
- Node.js (javascript)
- One Of: Python, Bash, Ruby, Powershell, etc for scripting

## Start

Make a fork of this repository (or clone it).

## 1. Scripting

write a script that will take `tfplan.json` file ( A terraform plan file converted to json) and parse it and then determine whether the apply should proceed or not based on the following:

- The plan must only contain `create` or `modify` steps
- the `modify` step must ONLY modify the resource's `tags` attribute and then only the `GitCommitHash` tag
- if anything else is being modified or destroyed the plan must not proceed (Print out the action that must be taken)

Add code to the `script.py` file in the `scripting` folder (you can use any language to solve, as long as you also provide instructions on how to excute said script or code agains the test files).
The script will be tested agains the `*.tfplan` files in that directory.


## 2. Infrastructure As Code

You have a Terraform configuration that deploys a set of resources using the count meta argument. Currently, you have deployed 5 resources.

You need to delete the "2nd" resource without affecting the other resources.
The count variable is part of the resource naming convention.

How would you go about deleting the "2nd" resource while ensuring that the other resources remain unchanged? Please provide a detailed explanation of the steps you would take and any Terraform features or commands you would use to achieve this. Please add these steps/actions to the `steps-to-fix.md` file in the `infrastructure-as-code` folder.

[https://developer.hashicorp.com/terraform/cli/commands/state/mv](https://developer.hashicorp.com/terraform/cli/commands/state/mv)

[https://developer.hashicorp.com/terraform/language/meta-arguments/for_each](https://developer.hashicorp.com/terraform/language/meta-arguments/for_each)

Manually deleting and renaming resources may work but is not the optimal solution.
You must be able to run `terraform apply` at the end and it must report "no changes".

## 3. Containers

Dockerise the express.js app and write a dockercompose file that will spin up and expose the app on port 4567.
Needed Files are in the `express-app` folder.


## 4. Dev/Problem Solving

All of the following actions must be taken in the "wild" directory:

Create a new instance of backstage

[https://backstage.io/docs/getting-started/](https://backstage.io/docs/getting-started/)

Create a custom action that will create a new file in the temp workspace.

The custom action must have an id of `my:custom:action`.

[https://backstage.io/docs/features/software-templates/writing-custom-actions](https://backstage.io/docs/features/software-templates/writing-custom-actions)

add the custom action to the example template in the repo
make sure it is the only action/step in the example template


## 5. Submission
Commit your code to a github repository and give acces to "adamaucamp"
(or make the repo public if you want.) But do send the relevant git repo link to adam.aucamp@oldmutual.com when finished.


---

# Submission notes

How to run each part.

| Part | Folder | Command | Details |
|------|--------|---------|---------|
| 1. Scripting | `scripting/` | `python3 script.py tfplan-1.json` | [scripting/README.md](scripting/README.md) |
| 2. Infrastructure as Code | `infrastructure-as-code/` | `terraform init && terraform apply` | [steps-to-fix.md](infrastructure-as-code/steps-to-fix.md) |
| 3. Containers | `express-app/` | `docker compose up --build` → http://localhost:4567 | |
| 4. Dev/Problem Solving | `wild/backstage/` | `nvm use 24 && yarn install && yarn start` → http://localhost:3000 | |

## Prerequisites

- **Python 3** for part 1 — standard library only, nothing to install.
- **Terraform** for part 2. Run `terraform apply` and it should report no changes.
- **Docker** for part 3.
- **Node.js 24.15+ for part 4.** This is stricter than the general "Node.js"
  requirement above: Backstage 1.57 refuses to start on Node 20 or 22 with
  `Node version 20 is not a supported LTS version`. Use `nvm use 24` (or
  `nvm install 24`) before `yarn install` in `wild/backstage`.

## Part 4 in brief

The custom action `my:custom:action` lives in
[`wild/backstage/packages/backend/src/actions/createFileAction.ts`](wild/backstage/packages/backend/src/actions/createFileAction.ts)
and is registered with the scaffolder by
[`scaffolderModuleCustomActions.ts`](wild/backstage/packages/backend/src/modules/scaffolderModuleCustomActions.ts).
It is the only step in
[the example template](wild/backstage/examples/template/template.yaml).

To see it run: start the app, sign in as Guest, then **Create** → **Example
Node.js Template** → **Create**. The step writes the file into the scaffolder's
temporary workspace and prints the path it used.
