from pathlib import Path
import argparse,json,hashlib,datetime
B=Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--dir',required=True);p.add_argument('--finding',required=True);p.add_argument('--preferred',choices=['true','false'],default='true');p.add_argument('--local-pass',choices=['true','false'],default='false');a=p.parse_args()
d=Path(a.dir).resolve();assert d.is_relative_to(B/'qa') and 'r13-c07' in d.name
j=json.loads((d/'assembly.json').read_text(encoding='utf-8-sig'))
q={'schemaVersion':1,'recordedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'assembly':{'path':str(d/'assembly.json'),'sha256':sha(d/'assembly.json')},'repairCrop':{'path':str(d/'repair-overlay-native.png'),'sha256':sha(d/'repair-overlay-native.png')},'reviewedAtNative1254':True,'reviewedRegions':['center','top','bottom','left','right'],'finding':a.finding,'preferredForFurtherReview':a.preferred=='true','localRepairAccepted':a.local_pass=='true','wholeTileInternalAccepted':False,'formalAccepted':False,'external':'pending','otherFindingsRemainOpen':True,'sourceReplay':j['proof']}
out=d/'repair-visual-qa-v1.json'
with out.open('x',encoding='utf-8') as f:json.dump(q,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'qa':str(out),'sha256':sha(out),'candidate':j['tiles'][0]}))
