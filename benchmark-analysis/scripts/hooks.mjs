import { readFile } from 'node:fs/promises';
export async function load(url, context, next) {
  if (url.endsWith('.json')) return { format: 'json', source: await readFile(new URL(url)), shortCircuit: true };
  return next(url, context);
}
