from pathlib import Path
from datetime import datetime,timezone
import sys
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c08');sys.path.insert(0,str(T.parent));import production_v2 as p
rules=(p.REPO/'AGENTS.md').read_text(encoding='utf-8-sig');split=p.read(p.REPO/'docs/MAP_PARALLEL_SPLIT_20261013.json')
assert 'r06_c08' not in [t for b in split['batches'] if b['map']=='main-city-game-20261009' and b['status']=='allocated_root_reserved' for t in b['tiles']]
sel=p.read(T/'selection.json');refs=[]
for k,f in sel.items():refs.append(dict(patch=k,**p.validate_native(f,T,k)))
p.write_json(T/'resume-checkpoint-20261017-v01.json',dict(recordedAtUtc=datetime.now(timezone.utc).isoformat(),tile='r06_c08',worker='/root/resume_r06_c08_20261017',originalProductionIdentity='/root/independent_qa_20261016',selectedCoreCount=len(sel),requiredCoreCount=16,missing=['s01_04'],selected=refs,nativeSourceVersionCount=len(list((T/'native').glob('*.png'))),unconsumedResultReceipts=[],builtinGenerationResumedSuccessfully=True,actualModel=None,actualModelEvidence='Built-in tool returned no model metadata',completeCandidateProduced=False,internalQAPassed=False,formalAccepted=False,reusedPartialQA=str(T/'qa/partial15-restart-20261017/reviewed-status.json'),newSelectedRepairs=['s03_01_fix02','s04_04_fix02'],pendingIssues=[dict(patch='s03_01',status='needs_repair',finding='Residual west/top turquoise glaze tone step after two local AI repair calls; best fix02 selected; retained unpassed.')],nextStep='Await stable selected r05_c08/s04_04 south edge then generate s01_04 from actual N/W/S/SW anchors, assemble full native16 and audit all33 plus actual external edges.',rootRuleHash=p.sha(p.REPO/'AGENTS.md'),splitHash=p.sha(p.REPO/'docs/MAP_PARALLEL_SPLIT_20261013.json')),replace=False)
print('Saved 15/16 checkpoint; source hashes and mechanical native validation verified.')

