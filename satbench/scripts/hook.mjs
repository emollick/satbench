export async function load(url, context, next) {
  if (url.endsWith('.json')) {
    const fs = await import('node:fs');
    const src = fs.readFileSync(new URL(url), 'utf8');
    return { format: 'module', source: 'export default ' + src + ';', shortCircuit: true };
  }
  return next(url, context);
}
