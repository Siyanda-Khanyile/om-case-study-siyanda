import { mkdtemp, readFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createFileAction } from './createFileAction';

/** A minimal action context: only what this action actually touches. */
function makeContext(workspacePath: string, input: any) {
  const outputs: Record<string, unknown> = {};
  return {
    ctx: {
      input,
      workspacePath,
      logger: { info: () => {}, warn: () => {}, error: () => {}, debug: () => {}, child: () => ({}) },
      output: (name: string, value: unknown) => {
        outputs[name] = value;
      },
    } as any,
    outputs,
  };
}

describe('my:custom:action', () => {
  it('has the id required by the brief', () => {
    expect(createFileAction().id).toBe('my:custom:action');
  });

  it('creates the file in the workspace', async () => {
    const workspacePath = await mkdtemp(join(tmpdir(), 'scaffolder-'));
    const { ctx, outputs } = makeContext(workspacePath, {
      filename: 'hello.txt',
      contents: 'Hello from my:custom:action!',
    });

    await createFileAction().handler(ctx);

    const written = await readFile(join(workspacePath, 'hello.txt'), 'utf-8');
    expect(written).toBe('Hello from my:custom:action!');
    expect(outputs.path).toBe(join(workspacePath, 'hello.txt'));
  });

  it('creates intermediate directories', async () => {
    const workspacePath = await mkdtemp(join(tmpdir(), 'scaffolder-'));
    const { ctx } = makeContext(workspacePath, {
      filename: 'nested/dir/file.md',
      contents: '# nested',
    });

    await createFileAction().handler(ctx);

    expect(await readFile(join(workspacePath, 'nested/dir/file.md'), 'utf-8')).toBe('# nested');
  });

  it('refuses to write outside the workspace', async () => {
    const workspacePath = await mkdtemp(join(tmpdir(), 'scaffolder-'));
    const { ctx } = makeContext(workspacePath, {
      filename: '../escaped.txt',
      contents: 'nope',
    });

    await expect(createFileAction().handler(ctx)).rejects.toThrow();
  });
});
