# [Backstage](https://backstage.io)

This is your newly scaffolded Backstage App, Good Luck!

Requires **Node.js 24.15 or newer** - Backstage 1.57 refuses to start on
Node 20 or 22. If you use nvm, run `nvm use 24` first.

To start the app, run:

```sh
yarn install
yarn start
```

This app contains the custom scaffolder action `my:custom:action`
(`packages/backend/src/actions/createFileAction.ts`), which creates a file in
the temporary workspace of a template run. It is the only step in the example
template in `examples/template/template.yaml`.
