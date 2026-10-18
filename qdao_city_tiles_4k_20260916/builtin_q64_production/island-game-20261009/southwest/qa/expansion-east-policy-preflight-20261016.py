from pathlib import Path
import sys,json,hashlib
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
import production as p
cmd,stem=sys.argv[1:3];reqpath=R/'prompts'/f'{stem}.request.json';req=p.load(reqpath)
if cmd=='preflight':
 repo=R.parents[3]
 rules=repo/'AGENTS.md';split=repo/'docs'/'MAP_PARALLEL_SPLIT_20261013.json'
 rt=rules.read_text(encoding='utf-8-sig');sp=json.loads(split.read_text(encoding='utf-8-sig'));tile=req['coordinates']['tile']
 conflicts=[b for b in sp['batches'] if b.get('map')=='island-game-20261009' and b.get('status')=='allocated_root_reserved' and tile in b['tiles']]
 assert not conflicts,conflicts
 assert '回退' in rt and '2.0' in rt
 req['preflight']={'rereadAtUtc':p.now(),'rootAgentsSha256':p.hashfile(rules),'parallelSplitSha256':p.hashfile(split),'parallelBatchCount':sp['batchTileCount'],'exclusiveTargetConflict':False,'paidRouteAuthorized':False,'actualModel':None}
 req['submittedAtUtc']=p.now();req['submitted']=True;p.dump(reqpath,req)
 d=p.load(R/'qa'/'expansion-east-worker-map.json');d.update(currentStem=stem,inFlight=True,status='builtin_image_request_submitting',updatedAtUtc=p.now());p.dump(R/'qa'/'expansion-east-worker-map.json',d)
 print(json.dumps({'stem':stem,'preflight':req['preflight']}))
elif cmd=='finalize':
 receipt=p.load(R/'receipts'/f'{stem}.tool.json');recpath=R/'native'/f'{stem}.png.generation.json';rec=p.load(recpath)
 assert all(p.hashfile(ref['path'])==ref['sha256'] for ref in req['references'])
 req['submitted']=True;req.setdefault('submittedAtUtc',receipt['recordedAtUtc']);req['promptSha256']=p.hashfile(rec['prompt']);p.dump(reqpath,req)
 rec['promptSha256']=req['promptSha256'];rec['receiptSha256']=p.hashfile(R/'receipts'/f'{stem}.tool.json');rec['preflight']=req.get('preflight');p.dump(recpath,rec)
 d=p.load(R/'qa'/'expansion-east-worker-map.json');d.update(inFlight=False,unsavedSuccessfulOutput=False,updatedAtUtc=p.now());p.dump(R/'qa'/'expansion-east-worker-map.json',d)
 print(json.dumps({'stem':stem,'refsVerified':True,'outputSha256':rec['sha256']}))
