import { allSummaries, AS_OF, models, cards, systemCards } from './repo/src/lib/data.ts';
import { writeFileSync } from 'node:fs';
const out = allSummaries().map(s => ({
  id: s.b.id, name: s.b.name, category: s.b.category, subcategory: s.b.subcategory, level: s.b.level, scoring: s.b.scoring, format: s.b.format,
  unit: s.b.unit, better: s.b.better, released: s.b.released, family: s.b.family, successor: s.b.successor, area: s.area, org: s.b.org,
  status: s.status, why: s.why, first: s.first, last: s.last, ncites: s.cites.length, citeLabs: s.labs, citeDates: s.cites.map(c=>[c.card.date,c.card.lab,c.card.model,c.score]),
  ndoc: s.docCites.length, frontier: s.frontier.map(p=>[p.date,p.value,p.model,p.source]), saturatedAt: s.saturatedAt, nearCeilingAt: s.nearCeilingAt,
  boardSource: s.boardSource, board: s.board.map(x=>[x.model,x.value,x.date,x.source]),
  lb: s.leaderboardBoard.map(x=>[x.model,x.value,x.date]), ep: s.epochBoard.map(x=>[x.model,x.value,x.date]), via: s.viaBoard.map(x=>[x.model,x.value,x.date]), card: s.cardBoard.map(x=>[x.model,x.value,x.date]), claim: s.claimBoard.map(x=>[x.model,x.value,x.date]),
  nScores: s.nScores, epoch: s.b.epoch,
}));
writeFileSync('summaries.json', JSON.stringify({asOf: AS_OF, benches: out}));
console.log(AS_OF, out.length);
