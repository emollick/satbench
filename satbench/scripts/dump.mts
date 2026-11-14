import * as D from './repo/src/lib/data.ts';
import fs from 'node:fs';
const out = D.allSummaries().map((s) => ({
  id: s.b.id, name: s.b.name, family: s.b.family ?? null, version: s.b.version ?? null, area: s.area,
  category: s.b.category ?? null, released: s.b.released ?? null, unit: s.b.unit ?? null, better: s.b.better ?? 'higher',
  level: s.b.level ?? null, format: s.b.format ?? null, scoring: s.b.scoring ?? null, org: s.b.org ?? null, successor: s.b.successor ?? null,
  epoch: s.b.epoch ?? null, edi: s.b.edi ?? null,
  first: s.first ?? null, last: s.last ?? null, status: s.status, why: s.why ?? null,
  saturatedAt: s.saturatedAt ?? null, nearCeilingAt: s.nearCeilingAt ?? null, nScores: s.nScores,
  best: s.best ? { model: s.best.model, value: s.best.value, date: s.best.date ?? null } : null,
  frontier: s.frontier.map((p) => ({ date: p.date, value: p.value, model: p.model, source: p.source, via: (p as any).via ?? null })),
  allpoints: null,
  cites: s.cites.map((c) => ({ card: c.card.id, date: c.card.date, lab: c.card.lab, model: c.card.model, score: c.score })),
  nDocCites: s.docCites.length,
}));
fs.writeFileSync('dump/summaries.json', JSON.stringify(out));
fs.writeFileSync('dump/models.json', JSON.stringify(D.models));
fs.writeFileSync('dump/labs.json', JSON.stringify(D.labs));
fs.writeFileSync('dump/cards.json', JSON.stringify(D.cards.map((c:any)=>({id:c.id,date:c.date,lab:c.lab,model:c.model,n:(c.results??[]).length}))));
fs.writeFileSync('dump/eci.json', JSON.stringify([...D.eciByModel.entries()]));
console.log(out.length, 'AS_OF', D.AS_OF);
const indep: Record<string, any[]> = {};
for (const s of [...D.leaderboardScores.map((x:any)=>({...x,src:'leaderboard'})), ...D.epochScores.map((x:any)=>({...x,src:'epoch'})), ...D.viaBoardScores.map((x:any)=>({...x,src:'collected-board'}))]) {
  if (!s.date) continue;
  (indep[s.benchmark] ??= []).push({ date: s.date, value: s.value, model: s.model, source: s.src });
}
fs.writeFileSync('dump/indep_points.json', JSON.stringify(indep));
