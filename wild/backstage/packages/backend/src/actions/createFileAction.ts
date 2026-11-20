import { resolveSafeChildPath } from '@backstage/backend-plugin-api';
import { createTemplateAction } from '@backstage/plugin-scaffolder-node';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';

/**
 * A custom scaffolder action that writes a file into the temporary workspace
 * that the scaffolder creates for each template run.
 *
 * Every action in a template run shares that workspace directory, which is
 * exposed as `ctx.workspacePath`. Later steps (for example `publish:github`)
 * operate on whatever is left there, so creating a file in it is how an action
 * contributes to the generated output.
 */
export function createFileAction() {
  return createTemplateAction({
    id: 'my:custom:action',
    description:
      'Creates a file with the given contents in the temporary workspace of the template run.',
    // The action only ever writes inside the run's own temporary workspace, so
    // it is safe to execute during a dry run instead of being skipped.
    supportsDryRun: true,
    schema: {
      input: {
        filename: z =>
          z
            .string()
            .default('hello.txt')
            .describe('Path of the file to create, relative to the workspace'),
        contents: z =>
          z
            .string()
            .default('Hello from my:custom:action!')
            .describe('Text to write into the file'),
      },
      output: {
        path: z =>
          z.string().describe('Absolute path of the file that was created'),
      },
    },
    async handler(ctx) {
      const { filename, contents } = ctx.input;

      // Resolves within the workspace and throws on anything that would escape
      // it, so a template cannot write outside its own temporary directory.
      const targetPath = resolveSafeChildPath(ctx.workspacePath, filename);

      await mkdir(dirname(targetPath), { recursive: true });
      await writeFile(targetPath, contents, 'utf-8');

      ctx.logger.info(`Created ${filename} in the workspace`);
      ctx.output('path', targetPath);
    },
  });
}
