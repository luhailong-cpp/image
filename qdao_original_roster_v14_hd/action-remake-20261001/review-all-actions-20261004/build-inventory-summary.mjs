import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.dirname(fileURLToPath(import.meta.url));
const read = rel => JSON.parse(fs.readFileSync(path.join(root,rel),'utf8').replace(/^\uFEFF/,''));
const rows = new Map();
const role = id => { if (!rows.has(id)) rows.set(id,{id,groups:{},frames:0,manifestShaMismatches:0,missing:0}); return rows.get(id); };
const add = (id,action,direction,frame,shaMatches) => {
  const r=role(id); r.frames++; const key=`${action}/${direction}`;
  r.groups[key]=(r.groups[key]||0)+1;
  if(shaMatches === false) r.manifestShaMismatches++;
};
const a=read('group-a/snapshot.json');
for(const [id,c] of Object.entries(a.characters)) {
  for(const f of c.frames) add(id,f.action,f.direction,f.frame,f.manifestMatch);
  role(id).missing=c.missing.length;
}
const b=read('group-b/source-evidence.json');
for(const [id,c] of Object.entries(b.characters)) for(const [key,g] of Object.entries(c.groups)) {
  const [action,direction]=key.split('/');
  for(const f of g.frames) add(id,action,direction,f.frame,f.shaMatchesManifest);
}
const c=read('group-c/source-evidence.json');
for(const f of c.frames) {
  if(f.error) { role(f.character).missing++; continue; }
  add(f.character,f.action,f.direction,f.frame,f.shaMatches);
}
for(const r of rows.values()) {
  r.groupCount=Object.keys(r.groups).length;
  r.expectedFrames=196;
  const expected = Object.fromEntries(['N','NE','E','SE','S','SW','W','NW'].map(d=>[`run/${d}`,16]));
  for(const [action,count] of [['hit',6],['attack',12],['cast',16]]) for(const d of ['E','W']) expected[`${action}/${d}`]=count;
  r.groupCountErrors=Object.entries(expected).filter(([key,count])=>r.groups[key]!==count).map(([key,count])=>({key,expected:count,actual:r.groups[key]||0}));
  r.completeByInventory=r.frames===196 && r.groupCount===14 && r.missing===0 && r.groupCountErrors.length===0;
  r.visualAcceptance='not_inferred_from_inventory';
}
const out={schemaVersion:1,generatedAt:new Date().toISOString(),scope:'Technical inventory from audit source snapshots; not current artwork or dynamic acceptance.',snapshots:{groupA:a.atUtc,groupB:b.checkedAtUtc,groupC:c.createdAtUTC},characters:[...rows.values()],totals:{characters:rows.size,frames:[...rows.values()].reduce((n,r)=>n+r.frames,0),completeByInventory:[...rows.values()].filter(r=>r.completeByInventory).length},sourcePngsModified:false};
fs.writeFileSync(path.join(root,'inventory-summary.json'),JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify(out.totals));
