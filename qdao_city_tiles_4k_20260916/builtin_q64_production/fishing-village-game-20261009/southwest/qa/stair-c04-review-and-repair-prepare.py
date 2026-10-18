from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
Q=Path(__file__).resolve().parent;Z=Q.parent;R=Z.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def save(p,v):
 assert not p.exists(),p
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
t=read(Q/'full-tile-r11_c04-assembly.json')
bad=['v1024-part03','h2048-part02','intersection-x1024-y2048']
qa=t.get('qa',t.get('qaFiles',[]))
if not isinstance(qa,list):raise RuntimeError(type(qa))
print(t.keys())
viewed=[]
for x in qa:
 name=Path(x['file']).name
 viewed.append({**x,'result':'repair_required' if any(s in name for s in bad) else 'pass'})
assert len(viewed)==39,len(viewed)
a={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r11_c04','reviewer':'stair_finish_1016','status':'repair_required','trace':ref(Q/'full-tile-r11_c04-assembly.json'),'candidate':ref(Q/'full-tile-r11_c04-candidate-4096.png'),'context':ref(Q/'full-tile-r11_c04-context-native.png'),'nativeQaViewedCount':39,'viewed':viewed,'issues':[{'id':'first-riser-base-notch','description':'First broad stair riser base has a 60px offset across x1024 near y2060; same issue visible in three native windows. Repair continuous straight stone/sand boundary without changing step count.','coreApproxBox':[900,1900,1200,2200]}],'externalJoinsVerified':False}
save(Q/'r11_c04-internal-native-art-audit-v1.json',a)
box=[500,1500,1754,2754];src=Q/'r11_c04-riser-base-repair-v1-source-native.png'
with Image.open(Q/'full-tile-r11_c04-context-native.png') as im:im.crop(box).save(src)
save(Path(str(src)+'.derivation.json'),{'source':ref(Q/'full-tile-r11_c04-context-native.png'),'contextBox':box,'operation':'integer crop only','nativePixelsResampled':False})
stem='r11_c04_riser_base_repair_v1';g=[12173+box[0],40845+box[1],12173+box[2],40845+box[3]]
refs=[{'path':src.as_posix(),'role':'native local edit target'},*read(Z/'references.json')]
req={'stem':stem,'tile':'r11_c04','patch':'localized_riser_base','coordinates':{'role':'localized native seam repair: riser base','globalContextBox':g,'expectedNativeDimensions':[1254,1254]},'references':refs,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'rulesReadBeforeRequest':[ref(R/'AGENTS.md'),ref(R/'docs/MAP_PARALLEL_SPLIT_20261013.json')]}
save(Z/'native'/(stem+'.request.json'),req);print(json.dumps({'audit':ref(Q/'r11_c04-internal-native-art-audit-v1.json'),'source':ref(src),'box':box}))
