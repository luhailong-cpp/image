from pathlib import Path
import sys,json
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T.parent));import production_v2 as p
identifier,oldid,prompt=sys.argv[1:4]
rules=(p.REPO/'AGENTS.md').read_text(encoding='utf-8-sig');split=p.read(p.REPO/'docs/MAP_PARALLEL_SPLIT_20261013.json')
assert T.name not in {t for b in split['batches'] if b['map']=='main-city-game-20261009' and b['status']=='allocated_root_reserved' for t in b['tiles']}
native=T/'native'/(oldid+'.png');v=p.validate_native(native,T,identifier[:6])
args={'prompt':prompt,'referenced_image_paths':[str(native)],'transparent_background':False}
p.write_json(T/'planned'/(identifier+'.parameters.json'),args,replace=False)
p.write_json(T/'receipts'/(identifier+'.rules-read.json'),{'rulesActuallyRead':True,'agentsSha256':p.sha(p.REPO/'AGENTS.md'),'splitSha256':p.sha(p.REPO/'docs/MAP_PARALLEL_SPLIT_20261013.json'),'editBase':v},replace=False)
p.record_request(T.name,identifier,T/'planned'/(identifier+'.parameters.json'))
print(json.dumps(args))
